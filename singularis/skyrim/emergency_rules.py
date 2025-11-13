"""
Emergency Response Rules for Stuck Detection and Recovery

Implements fast-path rules that override normal planning when critical
situations are detected. These rules provide immediate responses to:
- Stuck/frozen states
- Low coherence (system confusion)
- Perception-action mismatches
- Repeated failures

This bridges the gap between consciousness (awareness) and agency (action).
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum


class EmergencyLevel(Enum):
    """Severity of emergency situation."""
    CRITICAL = 3  # Immediate override required
    HIGH = 2      # Strong recommendation
    MEDIUM = 1    # Suggestion
    NONE = 0      # Normal operation


@dataclass
class EmergencyResponse:
    """Emergency response recommendation."""
    level: EmergencyLevel
    action: str
    reason: str
    confidence_modifier: float  # Multiply action confidence
    override: bool  # If True, skip normal planning


class EmergencyRules:
    """
    Emergency rule system for critical situations.
    
    These rules fire BEFORE expensive LLM reasoning and can override
    normal planning when system is in a critical state.
    """
    
    def __init__(self):
        self.stuck_cycle_threshold = 3
        self.low_coherence_threshold = 0.25
        self.visual_similarity_stuck_threshold = 0.95
        self.confidence_reduction_threshold = 0.5
        
        # Tracking
        self.cycles_since_strategy_change = 0
        self.last_strategy = None
    
    def evaluate_emergency_state(
        self,
        context: Dict[str, Any]
    ) -> Optional[EmergencyResponse]:
        """
        Evaluate if emergency response is needed.
        
        Args:
            context: System state including:
                - visual_similarity: float
                - recent_actions: List[str]
                - coherence: float
                - action_confidence: float
                - sensorimotor_status: str
                - cycles_since_change: int
                
        Returns:
            EmergencyResponse if emergency detected, None otherwise
        """
        # Check rules in priority order
        
        # CRITICAL: Stuck with high visual similarity
        response = self._rule_stuck_visual(context)
        if response:
            return response
        
        # HIGH: Perception-action mismatch
        response = self._rule_perception_action_mismatch(context)
        if response:
            return response
        
        # HIGH: Repeated action failure
        response = self._rule_repeated_failure(context)
        if response:
            return response
        
        # MEDIUM: Low coherence (system confusion)
        response = self._rule_low_coherence(context)
        if response:
            return response
        
        # MEDIUM: Long time without strategy change
        response = self._rule_strategy_stagnation(context)
        if response:
            return response
        
        return None
    
    def _rule_stuck_visual(self, context: Dict[str, Any]) -> Optional[EmergencyResponse]:
        """
        CRITICAL: If stuck for N cycles with high visual similarity, force change.
        
        Rule:
            visual_similarity > 0.95 AND
            action_history has repeated actions AND
            cycles_since_change > 3
            
        Response:
            Emergency override with rotation or interaction
        """
        visual_sim = context.get('visual_similarity', 0.0)
        recent_actions = context.get('recent_actions', [])
        cycles_since_change = context.get('cycles_since_change', 0)
        
        if visual_sim > self.visual_similarity_stuck_threshold and len(recent_actions) >= 3:
            # Check for repeated movement actions
            movement_actions = ['move_forward', 'move_backward', 'explore']
            recent_movements = [a for a in recent_actions[-3:] if a in movement_actions]
            
            if len(recent_movements) >= 2 and cycles_since_change >= self.stuck_cycle_threshold:
                # Force unstuck action
                last_action = recent_actions[-1] if recent_actions else None
                
                if last_action in ['move_forward', 'explore']:
                    # Try interaction first, then rotation
                    return EmergencyResponse(
                        level=EmergencyLevel.CRITICAL,
                        action='activate',
                        reason='STUCK: High visual similarity with repeated forward movement. Try interaction.',
                        confidence_modifier=1.0,
                        override=True
                    )
                elif last_action == 'move_backward':
                    # Try rotation
                    return EmergencyResponse(
                        level=EmergencyLevel.CRITICAL,
                        action='turn_right',
                        reason='STUCK: High visual similarity with repeated backward movement. Try rotation.',
                        confidence_modifier=1.0,
                        override=True
                    )
                else:
                    # Default: jump to break state
                    return EmergencyResponse(
                        level=EmergencyLevel.CRITICAL,
                        action='jump',
                        reason='STUCK: High visual similarity. Break state with jump.',
                        confidence_modifier=1.0,
                        override=True
                    )
        
        return None
    
    def _rule_perception_action_mismatch(self, context: Dict[str, Any]) -> Optional[EmergencyResponse]:
        """
        HIGH: Sensorimotor reports STUCK but action planning continues normal movement.
        
        Rule:
            sensorimotor_status == "STUCK" AND
            last_action in movement actions
            
        Response:
            Override with unstuck strategy
        """
        sensorimotor_status = context.get('sensorimotor_status', '').upper()
        recent_actions = context.get('recent_actions', [])
        
        if 'STUCK' in sensorimotor_status and recent_actions:
            last_action = recent_actions[-1]
            movement_actions = ['move_forward', 'move_backward', 'explore', 'turn_left', 'turn_right']
            
            if last_action in movement_actions:
                # Perception says stuck, but we're trying to move
                # Try interaction to resolve
                return EmergencyResponse(
                    level=EmergencyLevel.HIGH,
                    action='activate',
                    reason='MISMATCH: Sensorimotor detects STUCK but planning chose movement. Try interaction.',
                    confidence_modifier=0.9,
                    override=True
                )
        
        return None
    
    def _rule_repeated_failure(self, context: Dict[str, Any]) -> Optional[EmergencyResponse]:
        """
        HIGH: Same action repeated 4+ times with no progress.
        
        Rule:
            action_history[-4:] all same action AND
            coherence not improving
            
        Response:
            Force different action
        """
        recent_actions = context.get('recent_actions', [])
        coherence_history = context.get('coherence_history', [])
        
        if len(recent_actions) >= 4:
            last_four = recent_actions[-4:]
            if len(set(last_four)) == 1:  # All same action
                repeated_action = last_four[0]
                
                # Check if coherence improved
                coherence_improving = False
                if len(coherence_history) >= 2:
                    coherence_improving = coherence_history[-1] > coherence_history[-4] + 0.05
                
                if not coherence_improving:
                    # Repeated action with no improvement
                    # Suggest orthogonal action
                    if repeated_action in ['move_forward', 'explore']:
                        new_action = 'turn_right'
                    elif repeated_action in ['turn_left', 'turn_right']:
                        new_action = 'jump'
                    else:
                        new_action = 'move_backward'
                    
                    return EmergencyResponse(
                        level=EmergencyLevel.HIGH,
                        action=new_action,
                        reason=f'REPEATED FAILURE: {repeated_action} x4 with no progress. Force change.',
                        confidence_modifier=0.8,
                        override=True
                    )
        
        return None
    
    def _rule_low_coherence(self, context: Dict[str, Any]) -> Optional[EmergencyResponse]:
        """
        MEDIUM: System coherence < threshold, reduce action confidence.
        
        Rule:
            system_coherence < 0.25 AND
            action_confidence > 0.7
            
        Response:
            Reduce confidence, request conscious oversight
        """
        coherence = context.get('coherence', 1.0)
        action_confidence = context.get('action_confidence', 0.5)
        
        if coherence < self.low_coherence_threshold and action_confidence > 0.7:
            # System is confused but overconfident
            return EmergencyResponse(
                level=EmergencyLevel.MEDIUM,
                action=None,  # Don't override action, just modify confidence
                reason=f'LOW COHERENCE: System coherence {coherence:.2f} < {self.low_coherence_threshold}. Reducing confidence.',
                confidence_modifier=0.5,  # Cut confidence in half
                override=False
            )
        
        return None
    
    def _rule_strategy_stagnation(self, context: Dict[str, Any]) -> Optional[EmergencyResponse]:
        """
        MEDIUM: No strategy change for extended period.
        
        Rule:
            cycles_since_change > 10
            
        Response:
            Request re-evaluation
        """
        cycles_since_change = context.get('cycles_since_change', 0)
        
        if cycles_since_change > 10:
            self.cycles_since_strategy_change = 0  # Reset
            
            return EmergencyResponse(
                level=EmergencyLevel.MEDIUM,
                action=None,
                reason=f'STAGNATION: {cycles_since_change} cycles without strategy change. Request re-evaluation.',
                confidence_modifier=0.7,
                override=False
            )
        
        return None
    
    def suggest_unstuck_action(
        self,
        last_action: Optional[str],
        available_actions: List[str]
    ) -> str:
        """
        Suggest an unstuck action based on what was tried last.
        
        Strategy:
        1. If moving forward -> try activate (door/gate)
        2. If moving backward -> try rotation
        3. If rotating -> try jump
        4. If jumping -> try opposite direction
        
        Args:
            last_action: Last action attempted
            available_actions: Actions currently available
            
        Returns:
            Recommended unstuck action
        """
        preferences = {
            'move_forward': ['activate', 'turn_right', 'jump'],
            'explore': ['activate', 'turn_around', 'jump'],
            'move_backward': ['turn_right', 'turn_left', 'jump'],
            'turn_left': ['jump', 'move_backward', 'activate'],
            'turn_right': ['jump', 'move_backward', 'activate'],
            'jump': ['turn_around', 'move_backward', 'activate'],
            'activate': ['turn_right', 'move_backward', 'jump'],
        }
        
        # Get preferences for last action
        preferred = preferences.get(last_action, ['activate', 'turn_right', 'jump'])
        
        # Return first available preference
        for action in preferred:
            if action in available_actions:
                return action
        
        # Fallback: any action except last
        for action in available_actions:
            if action != last_action:
                return action
        
        # Last resort: random available
        return available_actions[0] if available_actions else 'wait'
    
    def record_strategy_change(self, new_strategy: str):
        """Record that strategy changed (resets cycle counter)."""
        if new_strategy != self.last_strategy:
            self.cycles_since_strategy_change = 0
            self.last_strategy = new_strategy
        else:
            self.cycles_since_strategy_change += 1
