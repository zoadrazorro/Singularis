"""
AGI Intervention Decider

Uses Singularis Double Helix to make empathetic, context-aware
intervention decisions based on detected patterns and anomalies.

Architecture:
    Pattern/Anomaly → AGI Decider → Intervention Decision
    
    AGI considers:
    - User context (time, mood, preferences)
    - Pattern significance
    - Intervention history (avoid spam)
    - Empathy and timing
    - Multiple subsystem consensus
"""

from __future__ import annotations

import json
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum

from loguru import logger


class InterventionType(Enum):
    """Types of interventions."""
    ENCOURAGEMENT = "encouragement"    # Positive reinforcement
    REMINDER = "reminder"              # Gentle nudge
    WARNING = "warning"                # Concern, needs attention
    EMERGENCY = "emergency"            # Critical, immediate action
    INSIGHT = "insight"                # Educational, informative
    SUGGESTION = "suggestion"          # Optional improvement


class Channel(Enum):
    """Delivery channels for interventions."""
    MESSENGER = "messenger"    # Text message
    VOICE = "voice"           # Spoken alert
    PUSH = "push"             # Push notification
    EMAIL = "email"           # Email
    SILENT = "silent"         # Log only, no notification


@dataclass
class InterventionDecision:
    """AGI's decision about whether/how to intervene."""
    
    # Decision
    should_intervene: bool
    intervention_type: InterventionType
    channel: Channel
    priority: int  # 1-10
    immediate: bool  # Send now vs wait for good timing
    
    # Content
    message: str
    reasoning: str  # AGI's reasoning
    
    # Context
    pattern_id: Optional[str] = None
    user_id: Optional[str] = None
    timestamp: datetime = None
    
    # Empathy factors
    user_mood: Optional[str] = None
    time_appropriateness: float = 0.0  # 0-1
    intervention_fatigue: float = 0.0  # 0-1 (higher = more fatigued)
    
    # Multi-system consensus
    subsystem_votes: Optional[Dict[str, bool]] = None
    consensus_strength: float = 0.0  # 0-1
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        d = asdict(self)
        d['intervention_type'] = self.intervention_type.value
        d['channel'] = self.channel.value
        d['timestamp'] = self.timestamp.isoformat()
        return d


class AGIInterventionDecider:
    """
    AGI-powered intervention decision maker.
    
    Uses Singularis consciousness (and optionally Double Helix)
    to make empathetic, context-aware intervention decisions.
    """
    
    def __init__(self, consciousness, double_helix=None):
        """
        Initialize decider.
        
        Args:
            consciousness: UnifiedConsciousnessLayer instance
            double_helix: Optional DoubleHelixArchitecture for multi-system consensus
        """
        self.consciousness = consciousness
        self.double_helix = double_helix
        
        # Intervention history (to avoid spam)
        self.intervention_history: List[InterventionDecision] = []
        
        # User preferences (learned over time)
        self.user_preferences: Dict[str, Any] = {}
        
        mode = "Double Helix" if double_helix else "Consciousness"
        logger.info(f"[AGI-DECIDER] Intervention decider initialized - Mode: {mode}")
    
    async def decide_intervention(
        self,
        pattern_or_anomaly: Dict[str, Any],
        user_context: Optional[Dict[str, Any]] = None
    ) -> InterventionDecision:
        """
        Decide whether and how to intervene.
        
        Args:
            pattern_or_anomaly: Pattern or anomaly dict
            user_context: User context (mood, preferences, etc.)
            
        Returns:
            InterventionDecision
        """
        user_context = user_context or {}
        user_id = user_context.get('user_id', 'unknown')
        
        logger.info(
            f"[AGI-DECIDER] Deciding intervention for: "
            f"{pattern_or_anomaly.get('name', 'unnamed')}"
        )
        
        # Build decision prompt
        prompt = self._build_decision_prompt(pattern_or_anomaly, user_context)
        
        # Get AGI decision
        if self.double_helix:
            # Use Double Helix for multi-system consensus
            decision_data = await self._decide_with_double_helix(
                prompt,
                pattern_or_anomaly,
                user_context
            )
        else:
            # Use consciousness alone
            decision_data = await self._decide_with_consciousness(
                prompt,
                pattern_or_anomaly,
                user_context
            )
        
        # Create decision object
        decision = self._parse_decision(
            decision_data,
            pattern_or_anomaly,
            user_context
        )
        
        # Record in history
        self.intervention_history.append(decision)
        
        # Learn from decision (update preferences)
        self._update_preferences(decision, user_context)
        
        logger.info(
            f"[AGI-DECIDER] Decision: "
            f"{'INTERVENE' if decision.should_intervene else 'NO INTERVENTION'} "
            f"(priority: {decision.priority}/10)"
        )
        
        return decision
    
    async def _decide_with_consciousness(
        self,
        prompt: str,
        pattern_or_anomaly: Dict[str, Any],
        user_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Make decision using consciousness alone."""
        
        response = await self.consciousness.process(
            query=prompt,
            subsystem_inputs={
                'pattern_data': pattern_or_anomaly,
                'decision_type': 'intervention'
            },
            context=user_context
        )
        
        # Parse JSON response
        try:
            return json.loads(response.response)
        except json.JSONDecodeError:
            logger.warning("[AGI-DECIDER] Failed to parse JSON, using fallback")
            return self._fallback_decision(pattern_or_anomaly)
    
    async def _decide_with_double_helix(
        self,
        prompt: str,
        pattern_or_anomaly: Dict[str, Any],
        user_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Make decision using Double Helix (multi-system consensus)."""
        
        # Query multiple subsystems through Double Helix
        # Each subsystem votes on intervention
        
        # For now, use consciousness (Double Helix integration would be here)
        # TODO: Integrate with actual Double Helix when available
        
        logger.info("[AGI-DECIDER] Using Double Helix consensus...")
        
        response = await self.consciousness.process(
            query=prompt + "\n\nConsider multiple perspectives: emotional, logical, practical.",
            subsystem_inputs={
                'pattern_data': pattern_or_anomaly,
                'decision_type': 'intervention_consensus'
            },
            context=user_context
        )
        
        try:
            return json.loads(response.response)
        except json.JSONDecodeError:
            return self._fallback_decision(pattern_or_anomaly)
    
    def _build_decision_prompt(
        self,
        pattern_or_anomaly: Dict[str, Any],
        user_context: Dict[str, Any]
    ) -> str:
        """Build prompt for intervention decision."""
        
        # Determine if pattern or anomaly
        is_anomaly = 'deviation' in pattern_or_anomaly
        item_type = "anomaly" if is_anomaly else "pattern"
        
        # Get recent intervention history
        recent_interventions = self._get_recent_interventions(
            user_context.get('user_id'),
            hours=24
        )
        
        # Calculate intervention fatigue
        fatigue = len(recent_interventions) / 10.0  # 0-1 scale
        
        prompt = f"""
        You are an empathetic AI life coach deciding whether to intervene.
        
        Context:
        - User ID: {user_context.get('user_id', 'unknown')}
        - Current time: {datetime.now().strftime('%A %I:%M %p')}
        - User mood: {user_context.get('mood', 'unknown')}
        - Recent interventions (24h): {len(recent_interventions)}
        - Intervention fatigue: {fatigue:.2f} (0=fresh, 1=overwhelmed)
        
        {item_type.capitalize()} Detected:
        - Name: {pattern_or_anomaly.get('name', 'Unknown')}
        - Type: {pattern_or_anomaly.get('type', 'unknown')}
        - Description: {pattern_or_anomaly.get('description', 'No description')}
        - Alert Level: {pattern_or_anomaly.get('alert_level', 'unknown')}
        """
        
        if is_anomaly:
            prompt += f"""
        - Expected: {pattern_or_anomaly.get('expected_value')}
        - Actual: {pattern_or_anomaly.get('actual_value')}
        - Deviation: {pattern_or_anomaly.get('deviation')}
            """
        else:
            prompt += f"""
        - Confidence: {pattern_or_anomaly.get('confidence', 0)}
        - Frequency: {pattern_or_anomaly.get('frequency', 'unknown')}
            """
        
        prompt += f"""
        
        Your Decision Framework:
        
        1. **Should we intervene?**
           - Is this actionable?
           - Will user find it helpful or annoying?
           - Is timing appropriate?
           - Have we intervened too much recently? (fatigue: {fatigue:.2f})
        
        2. **If yes, what type?**
           - encouragement: Positive reinforcement
           - reminder: Gentle nudge
           - warning: Needs attention
           - emergency: Critical, immediate
           - insight: Educational
           - suggestion: Optional improvement
        
        3. **What channel?**
           - messenger: Text (least intrusive)
           - voice: Spoken (more urgent)
           - push: Notification (moderate)
           - email: Detailed (can wait)
           - silent: Log only (no notification)
        
        4. **Priority (1-10)?**
           - 10: Life-threatening emergency
           - 7-9: Important, needs attention soon
           - 4-6: Useful information
           - 1-3: Nice to know
        
        5. **Timing?**
           - immediate: Send now
           - delayed: Wait for better timing
        
        6. **What to say?**
           - Be empathetic and supportive
           - Be specific and actionable
           - Consider user's current state
           - Avoid being preachy or annoying
           - CRITICAL: Never say "I will call 911" - only advise user to call
           - Say: "Please call 911" or "Consider calling emergency services"
           - Never take emergency actions automatically
        
        Respond in JSON:
        {{
            "should_intervene": true/false,
            "reasoning": "your reasoning process",
            "intervention_type": "type",
            "channel": "channel",
            "priority": 1-10,
            "immediate": true/false,
            "message": "what to say to user",
            "time_appropriateness": 0.0-1.0,
            "empathy_factors": ["factor1", "factor2"]
        }}
        """
        
        return prompt
    
    def _parse_decision(
        self,
        decision_data: Dict[str, Any],
        pattern_or_anomaly: Dict[str, Any],
        user_context: Dict[str, Any]
    ) -> InterventionDecision:
        """Parse AGI response into InterventionDecision."""
        
        try:
            return InterventionDecision(
                should_intervene=decision_data.get('should_intervene', False),
                intervention_type=InterventionType[
                    decision_data.get('intervention_type', 'insight').upper()
                ],
                channel=Channel[
                    decision_data.get('channel', 'messenger').upper()
                ],
                priority=int(decision_data.get('priority', 5)),
                immediate=decision_data.get('immediate', False),
                message=decision_data.get('message', 'Pattern detected'),
                reasoning=decision_data.get('reasoning', 'AGI decision'),
                pattern_id=pattern_or_anomaly.get('id'),
                user_id=user_context.get('user_id'),
                time_appropriateness=float(decision_data.get('time_appropriateness', 0.5)),
                intervention_fatigue=self._calculate_fatigue(user_context.get('user_id'))
            )
        except (KeyError, ValueError) as e:
            logger.warning(f"[AGI-DECIDER] Failed to parse decision: {e}, using fallback")
            return self._fallback_decision_object(pattern_or_anomaly, user_context)
    
    def _fallback_decision(self, pattern_or_anomaly: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback decision when AGI fails."""
        
        alert_level = pattern_or_anomaly.get('alert_level', 'low')
        
        if alert_level == 'critical':
            return {
                'should_intervene': True,
                'intervention_type': 'emergency',
                'channel': 'voice',
                'priority': 10,
                'immediate': True,
                'message': f"ALERT: {pattern_or_anomaly.get('message', 'Critical event detected')}. Please seek help immediately if needed.",
                'reasoning': 'Critical alert level - advising user to take action'
            }
        elif alert_level == 'high':
            return {
                'should_intervene': True,
                'intervention_type': 'warning',
                'channel': 'push',
                'priority': 7,
                'immediate': True,
                'message': pattern_or_anomaly.get('message', 'Important alert'),
                'reasoning': 'High alert level - automatic intervention'
            }
        else:
            return {
                'should_intervene': False,
                'intervention_type': 'insight',
                'channel': 'silent',
                'priority': 3,
                'immediate': False,
                'message': 'Pattern noted',
                'reasoning': 'Low priority - no intervention needed'
            }
    
    def _fallback_decision_object(
        self,
        pattern_or_anomaly: Dict[str, Any],
        user_context: Dict[str, Any]
    ) -> InterventionDecision:
        """Create fallback InterventionDecision object."""
        
        fallback = self._fallback_decision(pattern_or_anomaly)
        
        return InterventionDecision(
            should_intervene=fallback['should_intervene'],
            intervention_type=InterventionType[fallback['intervention_type'].upper()],
            channel=Channel[fallback['channel'].upper()],
            priority=fallback['priority'],
            immediate=fallback['immediate'],
            message=fallback['message'],
            reasoning=fallback['reasoning'],
            pattern_id=pattern_or_anomaly.get('id'),
            user_id=user_context.get('user_id')
        )
    
    def _get_recent_interventions(
        self,
        user_id: Optional[str],
        hours: int = 24
    ) -> List[InterventionDecision]:
        """Get recent interventions for user."""
        
        if not user_id:
            return []
        
        cutoff = datetime.now().timestamp() - (hours * 3600)
        
        return [
            decision for decision in self.intervention_history
            if decision.user_id == user_id
            and decision.timestamp.timestamp() > cutoff
            and decision.should_intervene
        ]
    
    def _calculate_fatigue(self, user_id: Optional[str]) -> float:
        """Calculate intervention fatigue (0-1)."""
        
        recent = self._get_recent_interventions(user_id, hours=24)
        
        # 0 interventions = 0 fatigue
        # 10+ interventions = 1.0 fatigue
        return min(len(recent) / 10.0, 1.0)
    
    def _update_preferences(
        self,
        decision: InterventionDecision,
        user_context: Dict[str, Any]
    ):
        """Learn from decision to update user preferences."""
        
        user_id = user_context.get('user_id')
        if not user_id:
            return
        
        if user_id not in self.user_preferences:
            self.user_preferences[user_id] = {
                'preferred_channel': 'messenger',
                'intervention_tolerance': 0.5,
                'best_times': []
            }
        
        # TODO: Learn from user feedback
        # For now, just track decisions
    
    def get_intervention_stats(self, user_id: Optional[str] = None) -> Dict[str, Any]:
        """Get intervention statistics."""
        
        if user_id:
            interventions = [d for d in self.intervention_history if d.user_id == user_id]
        else:
            interventions = self.intervention_history
        
        if not interventions:
            return {'total': 0}
        
        delivered = [d for d in interventions if d.should_intervene]
        
        return {
            'total_decisions': len(interventions),
            'interventions_delivered': len(delivered),
            'intervention_rate': len(delivered) / len(interventions) if interventions else 0,
            'avg_priority': sum(d.priority for d in delivered) / len(delivered) if delivered else 0,
            'by_type': self._count_by_field(delivered, 'intervention_type'),
            'by_channel': self._count_by_field(delivered, 'channel'),
            'current_fatigue': self._calculate_fatigue(user_id)
        }
    
    def _count_by_field(
        self,
        decisions: List[InterventionDecision],
        field: str
    ) -> Dict[str, int]:
        """Count decisions by field value."""
        
        counts = {}
        for decision in decisions:
            value = getattr(decision, field)
            key = value.value if isinstance(value, Enum) else str(value)
            counts[key] = counts.get(key, 0) + 1
        
        return counts
