"""
Life Query Handler

Handles natural language queries about life data using AGI consciousness.

Examples:
- "How did I sleep last week?"
- "Am I exercising enough?"
- "Why am I tired today?"
- "What patterns do you see in my routine?"
"""

from __future__ import annotations

import asyncio
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from dataclasses import dataclass

from loguru import logger
from singularis.utils.semantic_router import SemanticRouter
import json
import os

try:
    from integrations.life_timeline import LifeTimeline, EventType, EventSource
except ImportError:
    # Fallback for different import paths
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent.parent / "integrations"))
    from life_timeline import LifeTimeline, EventType, EventSource


@dataclass
class QueryResult:
    """Result of a life query."""
    query: str
    response: str
    confidence: float
    data_sources: List[str]
    event_count: int
    pattern_count: int
    timestamp: datetime
    metadata: Optional[Dict] = None


class LifeQueryHandler:
    """
    Handle natural language queries about life data.
    
    Uses AGI consciousness to analyze life events and provide insights.
    """
    
    def __init__(
        self,
        consciousness,
        timeline: LifeTimeline,
        pattern_engine=None
    ):
        """
        Initialize life query handler.
        
        Args:
            consciousness: UnifiedConsciousnessLayer instance
            timeline: LifeTimeline database
            pattern_engine: Optional PatternEngine for pattern analysis
        """
        self.consciousness = consciousness
        self.timeline = timeline
        self.pattern_engine = pattern_engine
        
        # Initialize Semantic Router
        self.router = SemanticRouter()
        
        # Default keywords (used as initial training data)
        self.default_keywords = {
            'sleep': ['sleep', 'slept', 'sleeping', 'rest', 'rested', 'tired', 'fatigue', 'insomnia', 'awake'],
            'exercise': ['exercise', 'workout', 'activity', 'steps', 'walking', 'running', 'gym', 'fitness', 'cardio'],
            'health': ['health', 'heart rate', 'hr', 'pulse', 'blood pressure', 'vitals', 'weight', 'sick', 'ill'],
            'pattern': ['pattern', 'routine', 'habit', 'trend', 'usually', 'typically', 'always', 'never'],
            'location': ['where', 'location', 'room', 'place', 'home', 'away', 'office', 'work'],
            'time': ['when', 'time', 'today', 'yesterday', 'week', 'month', 'schedule', 'calendar'],
            'mood': ['mood', 'feeling', 'emotion', 'happy', 'sad', 'stressed', 'anxious', 'excited'],
            'social': ['people', 'social', 'interaction', 'conversation', 'message', 'friend', 'family'],
        }
        
        # Load external config or use defaults
        self.load_config()
        
        logger.info("[LIFE-QUERY] Handler initialized with Semantic Router")
    
    def load_config(self, config_path: str = "life_query_config.json"):
        """Load keywords from config file or use defaults."""
        keywords = self.default_keywords.copy()
        
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    custom_config = json.load(f)
                    # Merge custom keywords
                    for cat, words in custom_config.get('keywords', {}).items():
                        if cat in keywords:
                            keywords[cat].extend(words)
                        else:
                            keywords[cat] = words
                logger.info(f"Loaded custom config from {config_path}")
            except Exception as e:
                logger.warning(f"Failed to load config: {e}")
        
        # Train router
        for category, examples in keywords.items():
            for example in examples:
                self.router.train(example, category)

    def _categorize_query(self, query: str) -> List[str]:
        """
        Categorize query using Semantic Router.
        
        Args:
            query: User query text
            
        Returns:
            List of relevant categories
        """
        categories = self.router.predict(query)
        return categories if categories else ['general']
    
    def _get_time_range(self, query: str) -> tuple[datetime, datetime]:
        """
        Extract time range from query.
        
        Args:
            query: User query text
            
        Returns:
            Tuple of (start_time, end_time)
        """
        query_lower = query.lower()
        now = datetime.now()
        
        # Today
        if 'today' in query_lower:
            start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            return (start, now)
        
        # Yesterday
        if 'yesterday' in query_lower:
            yesterday = now - timedelta(days=1)
            start = yesterday.replace(hour=0, minute=0, second=0, microsecond=0)
            end = yesterday.replace(hour=23, minute=59, second=59)
            return (start, end)
        
        # This week
        if 'this week' in query_lower or 'week' in query_lower:
            start = now - timedelta(days=7)
            return (start, now)
        
        # This month
        if 'this month' in query_lower or 'month' in query_lower:
            start = now - timedelta(days=30)
            return (start, now)
        
        # Last X days
        if 'last' in query_lower:
            if 'days' in query_lower or 'day' in query_lower:
                # Try to extract number
                words = query_lower.split()
                for i, word in enumerate(words):
                    if word == 'last' and i + 1 < len(words):
                        try:
                            days = int(words[i + 1])
                            start = now - timedelta(days=days)
                            return (start, now)
                        except ValueError:
                            pass
        
        # Default: last 7 days
        start = now - timedelta(days=7)
        return (start, now)
    
    async def _get_relevant_events(
        self,
        user_id: str,
        categories: List[str],
        start_time: datetime,
        end_time: datetime
    ) -> List[Any]:
        """
        Get relevant events based on query categories.
        
        Args:
            user_id: User identifier
            categories: Query categories
            start_time: Start of time range
            end_time: End of time range
            
        Returns:
            List of relevant LifeEvents
        """
        events = []
        
        # Get events by category
        for category in categories:
            if category == 'sleep':
                # Get sleep events
                sleep_events = self.timeline.query_by_time(
                    user_id, start_time, end_time,
                    source=EventSource.FITBIT
                )
                events.extend([e for e in sleep_events if e.type == EventType.SLEEP_PERIOD])
            
            elif category == 'exercise':
                # Get activity events
                activity_events = self.timeline.query_by_time(
                    user_id, start_time, end_time,
                    source=EventSource.FITBIT
                )
                events.extend([e for e in activity_events if e.type == EventType.ACTIVITY_DETECTED])
            
            elif category == 'health':
                # Get health metric events
                health_events = self.timeline.query_by_time(
                    user_id, start_time, end_time,
                    source=EventSource.FITBIT
                )
                events.extend([e for e in health_events if e.type == EventType.HEALTH_METRIC])
            
            elif category == 'location':
                # Get location events
                location_events = self.timeline.query_by_time(
                    user_id, start_time, end_time,
                    source=EventSource.CAMERA
                )
                events.extend([
                    e for e in location_events 
                    if e.type in [EventType.ROOM_ENTER, EventType.ROOM_EXIT]
                ])
            
            elif category == 'social':
                # Get social events
                social_events = self.timeline.query_by_time(
                    user_id, start_time, end_time,
                    source=EventSource.MESSENGER
                )
                events.extend([e for e in social_events if e.type == EventType.MESSAGE_RECEIVED])
            
            else:
                # Get all events for general queries
                all_events = self.timeline.query_by_time(
                    user_id, start_time, end_time
                )
                events.extend(all_events)
        
        # Remove duplicates
        seen = set()
        unique_events = []
        for event in events:
            event_id = id(event)
            if event_id not in seen:
                seen.add(event_id)
                unique_events.append(event)
        
        return unique_events
    
    def _summarize_events(self, events: List[Any]) -> str:
        """
        Create a summary of events for context.
        
        Args:
            events: List of LifeEvents
            
        Returns:
            Summary text
        """
        if not events:
            return "No events found in the specified time range."
        
        summary_parts = []
        
        # Count by type
        type_counts = {}
        for event in events:
            event_type = event.type.value
            type_counts[event_type] = type_counts.get(event_type, 0) + 1
        
        summary_parts.append(f"Total events: {len(events)}")
        summary_parts.append("\nEvent breakdown:")
        for event_type, count in sorted(type_counts.items(), key=lambda x: x[1], reverse=True):
            summary_parts.append(f"  - {event_type}: {count}")
        
        # Recent events (last 5)
        if len(events) > 0:
            summary_parts.append("\nRecent events:")
            for event in events[-5:]:
                timestamp = event.timestamp.strftime('%Y-%m-%d %H:%M')
                event_desc = f"{event.type.value}"
                if hasattr(event, 'features') and event.features:
                    # Add key features
                    if 'duration_minutes' in event.features:
                        event_desc += f" ({event.features['duration_minutes']}min)"
                    if 'room' in event.features:
                        event_desc += f" in {event.features['room']}"
                summary_parts.append(f"  - {timestamp}: {event_desc}")
        
        return "\n".join(summary_parts)
    
    async def _get_patterns(self, user_id: str) -> Dict[str, Any]:
        """
        Get detected patterns for user.
        
        Args:
            user_id: User identifier
            
        Returns:
            Pattern analysis dictionary
        """
        if not self.pattern_engine:
            return {'patterns': [], 'message': 'Pattern engine not available'}
        
        try:
            # Get patterns from pattern engine
            patterns = await self.pattern_engine.analyze_all(user_id)
            return patterns
        except Exception as e:
            logger.warning(f"[LIFE-QUERY] Pattern analysis failed: {e}")
            return {'patterns': [], 'error': str(e)}
    
    def _get_health_state(self, user_id: str) -> Dict[str, Any]:
        """
        Get current health state for user.
        
        Args:
            user_id: User identifier
            
        Returns:
            Health state dictionary
        """
        # Get most recent health metrics
        now = datetime.now()
        recent_start = now - timedelta(hours=1)
        
        health_events = self.timeline.query_by_time(
            user_id, recent_start, now,
            source=EventSource.FITBIT
        )
        
        health_state = {}
        
        for event in health_events:
            if event.type == EventType.HEALTH_METRIC:
                if 'heart_rate' in event.features:
                    health_state['heart_rate'] = event.features['heart_rate']
                if 'steps' in event.features:
                    health_state['steps'] = event.features['steps']
                if 'calories' in event.features:
                    health_state['calories'] = event.features['calories']
        
        return health_state
    
    async def handle_query(
        self,
        user_id: str,
        query: str
    ) -> QueryResult:
        """
        Process natural language query about life data.
        
        Args:
            user_id: User identifier
            query: Natural language query
            
        Returns:
            QueryResult with response and metadata
        """
        logger.info(f"[LIFE-QUERY] Processing query: '{query}' for user {user_id}")
        
        # Categorize query
        categories = self._categorize_query(query)
        logger.debug(f"[LIFE-QUERY] Categories: {categories}")
        
        # Get time range
        start_time, end_time = self._get_time_range(query)
        logger.debug(f"[LIFE-QUERY] Time range: {start_time} to {end_time}")
        
        # Get relevant events
        events = await self._get_relevant_events(user_id, categories, start_time, end_time)
        logger.debug(f"[LIFE-QUERY] Found {len(events)} relevant events")
        
        # Get patterns
        patterns = await self._get_patterns(user_id)
        
        # Get health state
        health_state = self._get_health_state(user_id)
        
        # Build context for consciousness
        event_summary = self._summarize_events(events)
        
        context = f"""
User Query: {query}

Time Range: {start_time.strftime('%Y-%m-%d %H:%M')} to {end_time.strftime('%Y-%m-%d %H:%M')}
Query Categories: {', '.join(categories)}

Available Data:
- {len(events)} life events from specified time range
- {len(patterns.get('patterns', []))} detected patterns
- Current health state: {health_state if health_state else 'No recent data'}

Events Summary:
{event_summary}

Detected Patterns:
{self._format_patterns(patterns)}

Instructions:
Answer the user's question using this data. Be conversational, insightful, and actionable.
Provide specific numbers and examples when available. If you notice concerning patterns
or anomalies, mention them. Focus on being helpful and empathetic.
"""
        
        # Process through consciousness
        try:
            result = await self.consciousness.process_unified(
                query=query,
                context=context,
                subsystem_data={
                    'user_id': user_id,
                    'query_type': 'life_query',
                    'categories': categories,
                    'event_count': len(events),
                    'pattern_count': len(patterns.get('patterns', [])),
                }
            )
            
            response = result.response
            confidence = result.coherence_score
            
            logger.info(
                f"[LIFE-QUERY] Response generated "
                f"(confidence: {confidence:.3f}, length: {len(response)} chars)"
            )
            
        except Exception as e:
            logger.error(f"[LIFE-QUERY] Consciousness processing failed: {e}")
            response = self._generate_fallback_response(query, events, patterns)
            confidence = 0.5
        
        # Create result
        query_result = QueryResult(
            query=query,
            response=response,
            confidence=confidence,
            data_sources=list(set([e.source.value for e in events])) if events else [],
            event_count=len(events),
            pattern_count=len(patterns.get('patterns', [])),
            timestamp=datetime.now(),
            metadata={
                'categories': categories,
                'time_range': {
                    'start': start_time.isoformat(),
                    'end': end_time.isoformat()
                },
                'health_state': health_state
            }
        )
        
        return query_result
    
    def _format_patterns(self, patterns: Dict[str, Any]) -> str:
        """Format patterns for context."""
        if not patterns.get('patterns'):
            return "No patterns detected yet."
        
        lines = []
        for pattern in patterns['patterns'][:5]:  # Top 5 patterns
            pattern_type = pattern.get('type', 'unknown')
            confidence = pattern.get('confidence', 0)
            description = pattern.get('description', 'No description')
            lines.append(f"  - {pattern_type} (confidence: {confidence:.2f}): {description}")
        
        return "\n".join(lines) if lines else "No patterns detected yet."
    
    def _generate_fallback_response(
        self,
        query: str,
        events: List[Any],
        patterns: Dict[str, Any]
    ) -> str:
        """
        Generate fallback response if consciousness fails.
        
        Args:
            query: User query
            events: Relevant events
            patterns: Pattern analysis
            
        Returns:
            Fallback response text
        """
        if not events:
            return (
                f"I don't have enough data to answer '{query}' yet. "
                "Keep using the system and I'll be able to provide insights soon!"
            )
        
        # Basic summary
        response_parts = [
            f"Based on {len(events)} events I found:",
            "",
            self._summarize_events(events)
        ]
        
        if patterns.get('patterns'):
            response_parts.append("")
            response_parts.append("Detected patterns:")
            response_parts.append(self._format_patterns(patterns))
        
        return "\n".join(response_parts)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get query handler statistics."""
        return {
            'consciousness_available': self.consciousness is not None,
            'timeline_available': self.timeline is not None,
            'pattern_engine_available': self.pattern_engine is not None,
            'query_categories': list(self.query_keywords.keys()),
        }
