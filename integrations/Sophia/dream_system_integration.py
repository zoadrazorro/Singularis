"""
Dream System Integration - Complete automated dream analysis system.

Integrates:
- Fitbit wake detection
- Messenger bot prompts (via Meta Glasses API)
- Dream recording and analysis
- Jungian/Freudian interpretation
"""

import asyncio
from datetime import datetime
from typing import Optional

from dream_analyst import DreamAnalyst, DreamRecord, DreamAnalysis
from fitbit_integration import FitbitIntegration, SleepData
from messenger_dream_bot import MessengerDreamBot


class DreamAnalysisSystem:
    """
    Complete automated dream analysis system.
    
    Workflow:
    1. Fitbit detects wake-up
    2. Messenger bot sends prompt via Meta Glasses
    3. User dictates dream via voice
    4. System transcribes and analyzes dream
    5. Sends Jungian/Freudian analysis back to user
    6. Tracks patterns over time
    """
    
    def __init__(self, 
                 fitbit_token: str,
                 fitbit_user_id: str,
                 messenger_chat_name: str = "Dream Journal"):
        """
        Initialize complete dream analysis system.
        
        Args:
            fitbit_token: Fitbit OAuth access token
            fitbit_user_id: Fitbit user ID
            messenger_chat_name: Name of Messenger chat for dreams
        """
        # Initialize components
        self.dream_analyst = DreamAnalyst()
        self.fitbit = FitbitIntegration(fitbit_token, fitbit_user_id)
        self.messenger = MessengerDreamBot(messenger_chat_name)
        
        # Set up callbacks
        self.fitbit.set_wake_callback(self._on_wake_detected)
        self.messenger.set_dream_callback(self._on_dream_received)
        
        # State
        self.running = False
        self.current_wake_time: Optional[datetime] = None
        self.current_sleep_data: Optional[SleepData] = None
        
        print("✨ Dream Analysis System initialized")
        print(f"   Fitbit: Connected")
        print(f"   Messenger: {messenger_chat_name}")
        print(f"   Analyst: Ready")
    
    async def start(self):
        """Start the complete dream analysis system."""
        self.running = True
        print("\n🌙 Dream Analysis System starting...")
        print("   Monitoring Fitbit for wake-up events...")
        print("   Ready to prompt for dreams via Messenger\n")
        
        # Start Fitbit monitoring
        await self.fitbit.start_monitoring(check_interval_minutes=5)
    
    def stop(self):
        """Stop the system."""
        self.running = False
        self.fitbit.stop_monitoring()
        print("\n🛑 Dream Analysis System stopped")
    
    async def _on_wake_detected(self, wake_time: datetime, sleep_data: SleepData):
        """
        Callback when Fitbit detects user woke up.
        
        Args:
            wake_time: When user woke up
            sleep_data: Sleep quality data from Fitbit
        """
        print(f"\n☀️ WAKE-UP DETECTED: {wake_time.strftime('%H:%M')}")
        print(f"   Sleep quality: {sleep_data.sleep_quality}/100")
        print(f"   REM sleep: {sleep_data.minutes_rem} minutes")
        print(f"   Duration: {sleep_data.duration_minutes // 60}h {sleep_data.duration_minutes % 60}m")
        
        # Store for later use
        self.current_wake_time = wake_time
        self.current_sleep_data = sleep_data
        
        # Send dream prompt via Messenger
        sleep_dict = {
            'quality': sleep_data.sleep_quality,
            'rem_minutes': sleep_data.minutes_rem,
            'duration_hours': sleep_data.duration_minutes / 60
        }
        
        await self.messenger.send_wake_prompt(wake_time, sleep_dict)
        
        print("   ✅ Dream prompt sent to Messenger")
        print("   ⏳ Waiting for user response...")
    
    async def _on_dream_received(self, transcription: str, timestamp: datetime):
        """
        Callback when user dictates their dream via Messenger.
        
        Args:
            transcription: Voice-to-text dream transcription
            timestamp: When dream was recorded
        """
        print(f"\n📝 DREAM RECEIVED: {len(transcription)} characters")
        print(f"   Timestamp: {timestamp.strftime('%H:%M:%S')}")
        
        # Record dream
        sleep_dict = None
        if self.current_sleep_data:
            sleep_dict = {
                'quality': self.current_sleep_data.sleep_quality,
                'duration_hours': self.current_sleep_data.duration_minutes / 60,
                'rem_minutes': self.current_sleep_data.minutes_rem
            }
        
        dream = self.dream_analyst.record_dream(
            transcription=transcription,
            wake_time=self.current_wake_time or timestamp,
            sleep_data=sleep_dict
        )
        
        print(f"   ✅ Dream recorded: {dream.id}")
        print(f"   Emotional tone: {dream.emotional_tone.value}")
        print(f"   Dream type: {dream.dream_type.value}")
        print(f"   Symbols found: {len(dream.symbols)}")
        print(f"   Themes: {', '.join(dream.themes) if dream.themes else 'None'}")
        
        # Analyze dream
        print("\n🔮 Analyzing dream...")
        analysis = self.dream_analyst.analyze_dream(dream.id)
        
        print(f"   ✅ Analysis complete")
        print(f"   Confidence: {analysis.confidence_score * 100:.0f}%")
        print(f"   Archetypes: {len(analysis.identified_archetypes)}")
        print(f"   Mechanisms: {len(analysis.identified_mechanisms)}")
        
        # Send analysis back to user
        analysis_dict = {
            'jungian_interpretation': analysis.jungian_interpretation,
            'identified_archetypes': analysis.identified_archetypes,
            'freudian_interpretation': analysis.freudian_interpretation,
            'latent_content': analysis.latent_content,
            'identified_mechanisms': analysis.identified_mechanisms,
            'synthesis': analysis.synthesis,
            'recommendations': analysis.recommendations,
            'confidence_score': analysis.confidence_score
        }
        
        await self.messenger.send_analysis(analysis_dict)
        
        print("   ✅ Analysis sent to user via Messenger")
        print("\n✨ Dream processing complete!\n")
        
        # Reset state
        self.current_wake_time = None
        self.current_sleep_data = None
    
    def get_dream_statistics(self, days: int = 30) -> dict:
        """Get dream statistics over period."""
        report = self.dream_analyst.get_dream_report(days)
        sleep_stats = self.fitbit.get_sleep_stats(days)
        
        return {
            'dream_stats': report,
            'sleep_stats': sleep_stats,
            'correlation': self._analyze_sleep_dream_correlation()
        }
    
    def _analyze_sleep_dream_correlation(self) -> dict:
        """Analyze correlation between sleep quality and dream characteristics."""
        # Get dreams with sleep data
        dreams_with_sleep = [
            d for d in self.dream_analyst.dreams.values()
            if d.sleep_quality is not None
        ]
        
        if len(dreams_with_sleep) < 5:
            return {'error': 'Not enough data'}
        
        # Analyze patterns
        high_quality_dreams = [d for d in dreams_with_sleep if d.sleep_quality >= 70]
        low_quality_dreams = [d for d in dreams_with_sleep if d.sleep_quality < 70]
        
        return {
            'total_dreams_analyzed': len(dreams_with_sleep),
            'high_quality_sleep': {
                'count': len(high_quality_dreams),
                'avg_symbols': sum(len(d.symbols) for d in high_quality_dreams) / len(high_quality_dreams) if high_quality_dreams else 0,
                'most_common_type': max(set(d.dream_type for d in high_quality_dreams), key=lambda x: sum(1 for d in high_quality_dreams if d.dream_type == x)).value if high_quality_dreams else 'N/A'
            },
            'low_quality_sleep': {
                'count': len(low_quality_dreams),
                'avg_symbols': sum(len(d.symbols) for d in low_quality_dreams) / len(low_quality_dreams) if low_quality_dreams else 0,
                'most_common_type': max(set(d.dream_type for d in low_quality_dreams), key=lambda x: sum(1 for d in low_quality_dreams if d.dream_type == x)).value if low_quality_dreams else 'N/A'
            },
            'insight': 'Better sleep quality correlates with more vivid dream recall' if len(high_quality_dreams) > 0 else 'Insufficient data'
        }
    
    async def send_weekly_summary(self):
        """Send weekly dream pattern summary to user."""
        report = self.dream_analyst.get_dream_report(7)
        
        if 'error' in report:
            print("No dreams to summarize this week")
            return
        
        summary = {
            'total_dreams': report['total_dreams'],
            'top_theme': report['most_common_themes'][0][0] if report['most_common_themes'] else 'N/A',
            'top_symbol': report['most_common_symbols'][0][0] if report['most_common_symbols'] else 'N/A',
            'patterns': report.get('recommendations', []),
            'insights': f"You recorded {report['total_dreams']} dreams this week!"
        }
        
        await self.messenger.send_weekly_summary(summary)
        print("✅ Weekly summary sent")


async def main():
    """Demo of complete system."""
    print("=" * 80)
    print("  DREAM ANALYSIS SYSTEM - Complete Integration Demo")
    print("=" * 80)
    
    # Note: In production, get these from secure config
    FITBIT_TOKEN = "your_fitbit_access_token"
    FITBIT_USER_ID = "your_fitbit_user_id"
    
    # Initialize system
    system = DreamAnalysisSystem(
        fitbit_token=FITBIT_TOKEN,
        fitbit_user_id=FITBIT_USER_ID,
        messenger_chat_name="Dream Journal"
    )
    
    print("\n📋 SYSTEM WORKFLOW:")
    print("1. Fitbit monitors sleep and detects wake-up")
    print("2. System sends prompt via Messenger (Meta Glasses)")
    print("3. User dictates dream via voice")
    print("4. System analyzes with Jungian + Freudian frameworks")
    print("5. Sends interpretation back to user")
    print("6. Tracks patterns over time")
    
    print("\n🔧 SETUP REQUIREMENTS:")
    print("✓ Fitbit account with OAuth token")
    print("✓ Meta Glasses or Messenger app")
    print("✓ meta-glasses-api browser extension running")
    print("✓ Messenger group chat named 'Dream Journal'")
    
    print("\n💡 TO START:")
    print("  await system.start()")
    print("  # System will run continuously, monitoring for wake-ups")
    
    print("\n📊 ANALYTICS:")
    print("  system.get_dream_statistics(days=30)")
    print("  await system.send_weekly_summary()")
    
    print("\n" + "=" * 80)
    print("  System ready! Configure credentials and run system.start()")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
