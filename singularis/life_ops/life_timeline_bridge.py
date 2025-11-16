"""
Life Timeline Bridge

Connects Life Timeline database to Singularis consciousness layer,
providing formatted life context for AGI processing.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import numpy as np

# Add integrations to path
integrations_path = Path(__file__).parent.parent.parent / "integrations"
sys.path.insert(0, str(integrations_path))

from life_timeline import LifeTimeline, LifeEvent, EventType, EventSource
from loguru import logger


class LifeTimelineBridge:
    """
    Bridge between Life Timeline and Singularis consciousness.
    
    Provides formatted life context for AGI processing:
    - Recent events summary
    - Health state
    - Activity patterns
    - Contextual insights
    """
    
    def __init__(self, timeline: LifeTimeline):
        """
        Initialize bridge.
        
        Args:
            timeline: Life Timeline instance
        """
        self.timeline = timeline
        logger.info("[LIFE-BRIDGE] Initialized Life Timeline bridge")
    
    def get_recent_context(
        self,
        user_id: str,
        hours: int = 24,
        max_events: int = 50
    ) -> str:
        """
        Get formatted recent life events for consciousness.
        
        Args:
            user_id: User ID
            hours: How many hours back to query
            max_events: Maximum events to include
            
        Returns:
            Formatted context string for GPT-5
        """
        # Query recent events
        events = self.timeline.query_by_time(
            user_id,
            datetime.now() - timedelta(hours=hours),
            datetime.now()
        )
        
        if not events:
            return "No recent life events recorded."
        
        # Limit to most recent
        events = events[-max_events:]
        
        # Format for consciousness
        context_lines = [f"📊 Recent Life Events (past {hours}h):"]
        context_lines.append("")
        
        # Group by type for better readability
        by_type: Dict[EventType, List[LifeEvent]] = {}
        for event in events:
            if event.type not in by_type:
                by_type[event.type] = []
            by_type[event.type].append(event)
        
        # Format each type
        for event_type, type_events in sorted(by_type.items(), key=lambda x: x[0].value):
            context_lines.append(f"  {self._format_event_type_summary(event_type, type_events)}")
        
        return "\n".join(context_lines)
    
    def get_health_summary(self, user_id: str, hours: int = 24) -> Dict[str, Any]:
        """
        Get current health state for consciousness.
        
        Args:
            user_id: User ID
            hours: Time window for analysis
            
        Returns:
            Health summary dict
        """
        summary = {
            'timestamp': datetime.now().isoformat(),
            'window_hours': hours,
        }
        
        # Heart rate
        hr_events = self.timeline.query_by_type(
            user_id,
            EventType.HEART_RATE,
            start_time=datetime.now() - timedelta(hours=hours)
        )
        
        if hr_events:
            bpms = [e.features.get('bpm', 0) for e in hr_events if 'bpm' in e.features]
            if bpms:
                summary['heart_rate'] = {
                    'avg': round(np.mean(bpms), 1),
                    'min': min(bpms),
                    'max': max(bpms),
                    'readings': len(bpms),
                    'status': self._classify_heart_rate(np.mean(bpms))
                }
        
        # Sleep
        sleep_events = self.timeline.query_by_type(
            user_id,
            EventType.SLEEP,
            start_time=datetime.now() - timedelta(hours=hours)
        )
        
        if sleep_events:
            durations = [e.features.get('duration', 0) for e in sleep_events if 'duration' in e.features]
            if durations:
                summary['sleep'] = {
                    'total_hours': round(sum(durations), 1),
                    'avg_per_night': round(np.mean(durations), 1),
                    'nights': len(durations),
                    'quality': self._classify_sleep_quality(np.mean(durations))
                }
        
        # Exercise
        exercise_events = self.timeline.query_by_type(
            user_id,
            EventType.EXERCISE,
            start_time=datetime.now() - timedelta(hours=hours)
        )
        
        if exercise_events:
            summary['exercise'] = {
                'sessions': len(exercise_events),
                'last_session': exercise_events[-1].timestamp.isoformat() if exercise_events else None,
                'activity_level': self._classify_activity_level(len(exercise_events), hours)
            }
        
        # Room activity (from cameras)
        room_events = self.timeline.query_by_type(
            user_id,
            EventType.ROOM_ENTER,
            start_time=datetime.now() - timedelta(hours=hours)
        )
        
        if room_events:
            rooms = [e.features.get('room') for e in room_events if 'room' in e.features]
            summary['activity'] = {
                'room_changes': len(rooms),
                'most_visited': max(set(rooms), key=rooms.count) if rooms else None,
                'mobility': 'active' if len(set(rooms)) > 3 else 'sedentary'
            }
        
        return summary
    
    def get_formatted_health_context(self, user_id: str) -> str:
        """
        Get human-readable health context for consciousness.
        
        Args:
            user_id: User ID
            
        Returns:
            Formatted health context string
        """
        health = self.get_health_summary(user_id)
        
        lines = ["💊 Current Health State:"]
        
        if 'heart_rate' in health:
            hr = health['heart_rate']
            lines.append(f"  ❤️ Heart Rate: {hr['avg']} bpm avg ({hr['status']}) - {hr['readings']} readings")
        
        if 'sleep' in health:
            sleep = health['sleep']
            lines.append(f"  😴 Sleep: {sleep['avg_per_night']}h/night avg ({sleep['quality']}) - {sleep['nights']} nights")
        
        if 'exercise' in health:
            ex = health['exercise']
            lines.append(f"  🏃 Exercise: {ex['sessions']} sessions ({ex['activity_level']})")
        
        if 'activity' in health:
            act = health['activity']
            lines.append(f"  🚶 Activity: {act['room_changes']} room changes ({act['mobility']})")
        
        if len(lines) == 1:
            lines.append("  No health data available")
        
        return "\n".join(lines)
    
    def get_last_significant_event(self, user_id: str) -> Optional[str]:
        """
        Get the most recent significant event.
        
        Args:
            user_id: User ID
            
        Returns:
            Description of last significant event
        """
        # Query recent events
        events = self.timeline.query_by_time(
            user_id,
            datetime.now() - timedelta(hours=24),
            datetime.now()
        )
        
        if not events:
            return None
        
        # Find most significant (highest importance)
        significant = max(events, key=lambda e: e.importance or 0)
        
        if significant.importance and significant.importance > 0.5:
            time_ago = self._format_time_ago(significant.timestamp)
            return f"{significant.type.value} {time_ago}: {self._format_event_details(significant)}"
        
        return None
    
    def _format_event_type_summary(self, event_type: EventType, events: List[LifeEvent]) -> str:
        """Format summary for a specific event type."""
        count = len(events)
        
        if event_type == EventType.HEART_RATE:
            bpms = [e.features.get('bpm', 0) for e in events if 'bpm' in e.features]
            if bpms:
                return f"❤️ Heart Rate: {count} readings, avg {np.mean(bpms):.0f} bpm (range: {min(bpms)}-{max(bpms)})"
        
        elif event_type == EventType.SLEEP:
            durations = [e.features.get('duration', 0) for e in events if 'duration' in e.features]
            if durations:
                return f"😴 Sleep: {count} sessions, avg {np.mean(durations):.1f}h"
        
        elif event_type == EventType.EXERCISE:
            return f"🏃 Exercise: {count} sessions"
        
        elif event_type == EventType.ROOM_ENTER:
            rooms = [e.features.get('room', 'unknown') for e in events if 'room' in e.features]
            unique_rooms = len(set(rooms))
            return f"🚶 Room Activity: {count} movements across {unique_rooms} rooms"
        
        elif event_type == EventType.FALL:
            return f"⚠️ Falls: {count} detected"
        
        elif event_type == EventType.MESSAGE:
            return f"💬 Messages: {count} conversations"
        
        else:
            return f"📝 {event_type.value}: {count} events"
    
    def _format_event_details(self, event: LifeEvent) -> str:
        """Format event details."""
        if event.type == EventType.HEART_RATE:
            return f"{event.features.get('bpm')} bpm"
        elif event.type == EventType.SLEEP:
            return f"{event.features.get('duration')}h"
        elif event.type == EventType.ROOM_ENTER:
            return f"entered {event.features.get('room')}"
        elif event.type == EventType.EXERCISE:
            return f"{event.features.get('activity_type', 'workout')}"
        else:
            return event.type.value
    
    def _format_time_ago(self, timestamp: datetime) -> str:
        """Format time ago string."""
        delta = datetime.now() - timestamp
        
        if delta.total_seconds() < 60:
            return "just now"
        elif delta.total_seconds() < 3600:
            mins = int(delta.total_seconds() / 60)
            return f"{mins}m ago"
        elif delta.total_seconds() < 86400:
            hours = int(delta.total_seconds() / 3600)
            return f"{hours}h ago"
        else:
            days = int(delta.total_seconds() / 86400)
            return f"{days}d ago"
    
    def _classify_heart_rate(self, avg_bpm: float) -> str:
        """Classify heart rate."""
        if avg_bpm < 60:
            return "low"
        elif avg_bpm < 100:
            return "normal"
        elif avg_bpm < 120:
            return "elevated"
        else:
            return "high"
    
    def _classify_sleep_quality(self, avg_hours: float) -> str:
        """Classify sleep quality."""
        if avg_hours < 6:
            return "insufficient"
        elif avg_hours < 7:
            return "adequate"
        elif avg_hours < 9:
            return "good"
        else:
            return "excessive"
    
    def _classify_activity_level(self, sessions: int, hours: int) -> str:
        """Classify activity level."""
        sessions_per_day = sessions / (hours / 24)
        
        if sessions_per_day < 0.2:
            return "sedentary"
        elif sessions_per_day < 0.5:
            return "light"
        elif sessions_per_day < 1:
            return "moderate"
        else:
            return "active"
