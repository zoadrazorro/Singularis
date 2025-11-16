"""
Fitbit Integration - Wake detection and sleep data collection.

Monitors Fitbit for wake-up events and retrieves sleep data to trigger dream recording.
"""

from typing import Dict, Optional, Callable
from datetime import datetime, timedelta
import asyncio
import requests
from dataclasses import dataclass


@dataclass
class SleepData:
    """Sleep data from Fitbit."""
    date: datetime
    duration_minutes: int
    efficiency: float  # 0-100
    minutes_asleep: int
    minutes_awake: int
    minutes_rem: Optional[int] = None
    minutes_light: Optional[int] = None
    minutes_deep: Optional[int] = None
    wake_time: Optional[datetime] = None
    sleep_quality: float = 0.0  # Calculated 0-100


class FitbitIntegration:
    """
    Fitbit API integration for sleep tracking and wake detection.
    
    Features:
    - Detect when user wakes up
    - Retrieve detailed sleep data
    - Trigger dream recording prompt via Messenger bot
    - Calculate sleep quality score
    """
    
    def __init__(self, access_token: str, user_id: str):
        """
        Initialize Fitbit integration.
        
        Args:
            access_token: Fitbit OAuth access token
            user_id: Fitbit user ID
        """
        self.access_token = access_token
        self.user_id = user_id
        self.base_url = "https://api.fitbit.com/1.2"
        self.headers = {
            'Authorization': f'Bearer {access_token}',
            'Accept': 'application/json'
        }
        
        # Wake detection
        self.last_sleep_end: Optional[datetime] = None
        self.wake_callback: Optional[Callable] = None
        self.monitoring = False
    
    def set_wake_callback(self, callback: Callable[[datetime, SleepData], None]):
        """
        Set callback function to trigger when user wakes up.
        
        Args:
            callback: Function that takes (wake_time, sleep_data)
        """
        self.wake_callback = callback
    
    async def start_monitoring(self, check_interval_minutes: int = 5):
        """
        Start monitoring for wake-up events.
        
        Args:
            check_interval_minutes: How often to check Fitbit API
        """
        self.monitoring = True
        print(f"🌙 Fitbit wake monitoring started (checking every {check_interval_minutes} min)")
        
        while self.monitoring:
            try:
                # Check for recent sleep end
                sleep_data = self.get_latest_sleep()
                
                if sleep_data and sleep_data.wake_time:
                    # Check if this is a new wake-up
                    if self.last_sleep_end is None or sleep_data.wake_time > self.last_sleep_end:
                        # User just woke up!
                        self.last_sleep_end = sleep_data.wake_time
                        
                        # Check if wake-up was recent (within last 30 minutes)
                        time_since_wake = (datetime.now() - sleep_data.wake_time).total_seconds() / 60
                        
                        if time_since_wake <= 30:
                            print(f"☀️ Wake-up detected at {sleep_data.wake_time.strftime('%H:%M')}")
                            
                            # Trigger callback (send Messenger prompt)
                            if self.wake_callback:
                                await self.wake_callback(sleep_data.wake_time, sleep_data)
                
                # Wait before next check
                await asyncio.sleep(check_interval_minutes * 60)
                
            except Exception as e:
                print(f"Error monitoring Fitbit: {e}")
                await asyncio.sleep(60)  # Wait 1 min on error
    
    def stop_monitoring(self):
        """Stop wake monitoring."""
        self.monitoring = False
        print("🛑 Fitbit wake monitoring stopped")
    
    def get_latest_sleep(self) -> Optional[SleepData]:
        """
        Get most recent sleep session from Fitbit.
        
        Returns:
            SleepData object or None if no recent sleep
        """
        try:
            # Get sleep data for today
            today = datetime.now().strftime('%Y-%m-%d')
            url = f"{self.base_url}/user/{self.user_id}/sleep/date/{today}.json"
            
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            data = response.json()
            
            if not data.get('sleep'):
                return None
            
            # Get most recent sleep session
            sleep_session = data['sleep'][0]
            
            # Parse data
            start_time = datetime.fromisoformat(sleep_session['startTime'].replace('Z', '+00:00'))
            end_time = datetime.fromisoformat(sleep_session['endTime'].replace('Z', '+00:00'))
            
            # Get sleep stages
            levels = sleep_session.get('levels', {})
            summary = levels.get('summary', {})
            
            rem_minutes = summary.get('rem', {}).get('minutes', 0)
            light_minutes = summary.get('light', {}).get('minutes', 0)
            deep_minutes = summary.get('deep', {}).get('minutes', 0)
            
            # Calculate sleep quality (0-100)
            efficiency = sleep_session.get('efficiency', 0)
            quality = self._calculate_sleep_quality(
                efficiency=efficiency,
                rem_minutes=rem_minutes,
                deep_minutes=deep_minutes,
                duration_minutes=sleep_session['duration'] // 60000
            )
            
            return SleepData(
                date=start_time.date(),
                duration_minutes=sleep_session['duration'] // 60000,  # Convert ms to minutes
                efficiency=efficiency,
                minutes_asleep=sleep_session['minutesAsleep'],
                minutes_awake=sleep_session['minutesAwake'],
                minutes_rem=rem_minutes,
                minutes_light=light_minutes,
                minutes_deep=deep_minutes,
                wake_time=end_time,
                sleep_quality=quality
            )
            
        except Exception as e:
            print(f"Error fetching Fitbit sleep data: {e}")
            return None
    
    def _calculate_sleep_quality(self, 
                                 efficiency: float,
                                 rem_minutes: int,
                                 deep_minutes: int,
                                 duration_minutes: int) -> float:
        """
        Calculate overall sleep quality score (0-100).
        
        Based on:
        - Sleep efficiency (how much time asleep vs in bed)
        - REM sleep amount (important for dreams!)
        - Deep sleep amount
        - Total duration
        """
        score = 0
        
        # Efficiency (0-30 points)
        score += (efficiency / 100) * 30
        
        # REM sleep (0-30 points) - optimal: 90-120 minutes
        rem_score = min(rem_minutes / 120, 1) * 30
        score += rem_score
        
        # Deep sleep (0-20 points) - optimal: 60-90 minutes
        deep_score = min(deep_minutes / 90, 1) * 20
        score += deep_score
        
        # Duration (0-20 points) - optimal: 7-9 hours
        if 420 <= duration_minutes <= 540:  # 7-9 hours
            score += 20
        elif 360 <= duration_minutes < 420 or 540 < duration_minutes <= 600:
            score += 10
        
        return round(score, 1)
    
    def get_sleep_history(self, days: int = 30) -> List[SleepData]:
        """
        Get sleep history for the last N days.
        
        Args:
            days: Number of days to retrieve
        
        Returns:
            List of SleepData objects
        """
        sleep_history = []
        
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            url = f"{self.base_url}/user/{self.user_id}/sleep/date/{start_date.strftime('%Y-%m-%d')}/{end_date.strftime('%Y-%m-%d')}.json"
            
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            data = response.json()
            
            for session in data.get('sleep', []):
                start_time = datetime.fromisoformat(session['startTime'].replace('Z', '+00:00'))
                end_time = datetime.fromisoformat(session['endTime'].replace('Z', '+00:00'))
                
                levels = session.get('levels', {})
                summary = levels.get('summary', {})
                
                rem_minutes = summary.get('rem', {}).get('minutes', 0)
                light_minutes = summary.get('light', {}).get('minutes', 0)
                deep_minutes = summary.get('deep', {}).get('minutes', 0)
                
                efficiency = session.get('efficiency', 0)
                duration_minutes = session['duration'] // 60000
                
                quality = self._calculate_sleep_quality(
                    efficiency=efficiency,
                    rem_minutes=rem_minutes,
                    deep_minutes=deep_minutes,
                    duration_minutes=duration_minutes
                )
                
                sleep_history.append(SleepData(
                    date=start_time.date(),
                    duration_minutes=duration_minutes,
                    efficiency=efficiency,
                    minutes_asleep=session['minutesAsleep'],
                    minutes_awake=session['minutesAwake'],
                    minutes_rem=rem_minutes,
                    minutes_light=light_minutes,
                    minutes_deep=deep_minutes,
                    wake_time=end_time,
                    sleep_quality=quality
                ))
            
            return sleep_history
            
        except Exception as e:
            print(f"Error fetching sleep history: {e}")
            return []
    
    def get_sleep_stats(self, days: int = 30) -> Dict:
        """Get sleep statistics over period."""
        history = self.get_sleep_history(days)
        
        if not history:
            return {'error': 'No sleep data available'}
        
        from statistics import mean
        
        return {
            'avg_duration_hours': round(mean(s.duration_minutes for s in history) / 60, 1),
            'avg_efficiency': round(mean(s.efficiency for s in history), 1),
            'avg_rem_minutes': round(mean(s.minutes_rem for s in history if s.minutes_rem), 1),
            'avg_deep_minutes': round(mean(s.minutes_deep for s in history if s.minutes_deep), 1),
            'avg_sleep_quality': round(mean(s.sleep_quality for s in history), 1),
            'total_nights': len(history)
        }


# OAuth helper functions
def get_fitbit_auth_url(client_id: str, redirect_uri: str) -> str:
    """
    Generate Fitbit OAuth authorization URL.
    
    User needs to visit this URL to authorize the app.
    """
    scope = "sleep"
    return (
        f"https://www.fitbit.com/oauth2/authorize?"
        f"client_id={client_id}&"
        f"response_type=code&"
        f"scope={scope}&"
        f"redirect_uri={redirect_uri}"
    )


def exchange_code_for_token(code: str, client_id: str, client_secret: str, redirect_uri: str) -> Dict:
    """
    Exchange authorization code for access token.
    
    Returns dict with 'access_token', 'refresh_token', 'user_id'
    """
    import base64
    
    # Encode credentials
    credentials = f"{client_id}:{client_secret}"
    encoded = base64.b64encode(credentials.encode()).decode()
    
    headers = {
        'Authorization': f'Basic {encoded}',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    
    data = {
        'code': code,
        'grant_type': 'authorization_code',
        'redirect_uri': redirect_uri
    }
    
    response = requests.post('https://api.fitbit.com/oauth2/token', headers=headers, data=data)
    response.raise_for_status()
    
    return response.json()


if __name__ == "__main__":
    # Demo usage (requires valid Fitbit credentials)
    print("=== FITBIT INTEGRATION DEMO ===\n")
    
    # Note: In production, you'd get these from OAuth flow
    ACCESS_TOKEN = "your_access_token_here"
    USER_ID = "your_user_id_here"
    
    # Initialize
    fitbit = FitbitIntegration(ACCESS_TOKEN, USER_ID)
    
    # Get latest sleep
    print("Fetching latest sleep data...")
    sleep = fitbit.get_latest_sleep()
    
    if sleep:
        print(f"\n📊 Latest Sleep Session:")
        print(f"  Date: {sleep.date}")
        print(f"  Duration: {sleep.duration_minutes // 60}h {sleep.duration_minutes % 60}m")
        print(f"  Efficiency: {sleep.efficiency}%")
        print(f"  REM: {sleep.minutes_rem} min")
        print(f"  Deep: {sleep.minutes_deep} min")
        print(f"  Quality Score: {sleep.sleep_quality}/100")
        if sleep.wake_time:
            print(f"  Woke up at: {sleep.wake_time.strftime('%H:%M')}")
    
    # Get stats
    print("\n📈 Sleep Stats (Last 30 Days):")
    stats = fitbit.get_sleep_stats(30)
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    print("\n💡 To enable wake detection:")
    print("  1. Set up OAuth with Fitbit")
    print("  2. Set wake callback: fitbit.set_wake_callback(your_function)")
    print("  3. Start monitoring: await fitbit.start_monitoring()")
    print("  4. System will trigger dream recording prompt on wake-up")
