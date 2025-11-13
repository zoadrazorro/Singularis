"""
Emotion Integration for Skyrim AGI

Integrates HuiHui emotion system with Skyrim gameplay to provide:
1. Emotional responses to combat situations
2. Emotional valence tracking during gameplay
3. Emotion-influenced decision making
4. Emotional state logging for analysis

Based on session analysis showing:
- Combat-heavy scenarios (fear, fortitude, desire)
- Health-critical situations (fear, sadness, hope)
- Resource management (anxiety, relief)
- Adaptive behaviors (pride, shame based on success/failure)
"""

import asyncio
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from loguru import logger

from ..emotion import (
    HuiHuiEmotionEngine,
    EmotionConfig,
    EmotionState,
    EmotionType,
    EmotionalValence
)


@dataclass
class SkyrimEmotionContext:
    """
    Emotion context specific to Skyrim gameplay.
    
    Maps game state to emotional triggers.
    """
    # Combat state
    in_combat: bool = False
    health_percent: float = 1.0
    stamina_percent: float = 1.0
    magicka_percent: float = 1.0
    
    # Threat assessment
    enemy_nearby: bool = False
    enemy_count: int = 0
    enemy_threat_level: float = 0.0  # 0.0 = low, 1.0 = deadly
    
    # Resources
    health_critical: bool = False
    stamina_low: bool = False
    resources_low: bool = False
    
    # Recent outcomes
    recent_damage_taken: float = 0.0
    recent_damage_dealt: float = 0.0
    recent_kills: int = 0
    recent_deaths: int = 0
    
    # Exploration
    new_location_discovered: bool = False
    quest_completed: bool = False
    quest_failed: bool = False
    
    # Social
    npc_interaction: bool = False
    npc_friendly: bool = True
    
    # Action outcomes
    action_succeeded: bool = True
    stuck_detected: bool = False
    
    # Coherence from consciousness system
    coherence_delta: float = 0.0
    adequacy_score: float = 0.5


class SkyrimEmotionIntegration:
    """
    Integrates HuiHui emotion system with Skyrim AGI.
    
    Provides emotion-aware decision making and emotional state tracking
    during gameplay.
    """
    
    def __init__(self, emotion_config: Optional[EmotionConfig] = None):
        """
        Initialize Skyrim emotion integration.
        
        Args:
            emotion_config: Configuration for emotion engine
        """
        # Create emotion engine
        self.emotion_engine = HuiHuiEmotionEngine(
            emotion_config or EmotionConfig()
        )
        
        # Emotion history for Skyrim session
        self.session_emotions: List[EmotionState] = []
        
        # Emotion-influenced decision weights
        self.emotion_weights = {
            'aggression': 0.5,  # How aggressive to be in combat
            'caution': 0.5,     # How cautious to be
            'exploration': 0.5, # Drive to explore
            'social': 0.5       # Willingness to interact
        }
        
        # Statistics
        self.combat_emotions: Dict[EmotionType, int] = {}
        self.exploration_emotions: Dict[EmotionType, int] = {}
        
        logger.info("[EMOTION] Skyrim emotion integration initialized")
    
    async def initialize_llm(self):
        """Initialize LLM for emotion engine."""
        await self.emotion_engine.initialize_llm()
    
    async def process_game_state(
        self,
        game_state: Dict[str, Any],
        context: SkyrimEmotionContext
    ) -> EmotionState:
        """
        Process current game state and compute emotional response.
        
        Args:
            game_state: Current game state from perception
            context: Skyrim-specific emotion context
        
        Returns:
            EmotionState with computed emotions
        """
        # Build emotion stimulus from game context
        stimulus = self._build_stimulus(game_state, context)
        
        # Process emotion
        emotion_state = await self.emotion_engine.process_emotion(
            context={
                'game_state': game_state,
                'skyrim_context': context.__dict__,
                'state_summary': stimulus
            },
            stimuli=stimulus,
            coherence_delta=context.coherence_delta,
            adequacy_score=context.adequacy_score
        )
        
        # Update session history
        self.session_emotions.append(emotion_state)
        
        # Update statistics
        self._update_statistics(emotion_state, context)
        
        # Update decision weights based on emotion
        self._update_decision_weights(emotion_state)
        
        return emotion_state
    
    def _build_stimulus(
        self,
        game_state: Dict[str, Any],
        context: SkyrimEmotionContext
    ) -> str:
        """Build natural language stimulus for emotion processing."""
        parts = []
        
        # Combat situation
        if context.in_combat:
            if context.health_critical:
                parts.append("I'm in critical danger! My health is extremely low and I'm fighting for survival.")
            elif context.enemy_threat_level > 0.7:
                parts.append(f"I'm facing {context.enemy_count} dangerous enemies. This is a serious threat.")
            else:
                parts.append(f"I'm engaged in combat with {context.enemy_count} enemies.")
            
            if context.recent_damage_taken > 50:
                parts.append("I've taken heavy damage recently.")
            if context.recent_kills > 0:
                parts.append(f"I've successfully defeated {context.recent_kills} enemies.")
        
        # Resource state
        if context.health_critical:
            parts.append("My health is critically low. I need healing urgently.")
        elif context.stamina_low:
            parts.append("I'm exhausted. My stamina is depleted.")
        elif context.resources_low:
            parts.append("My resources are running low.")
        
        # Exploration
        if context.new_location_discovered:
            parts.append("I've discovered a new location! This is exciting.")
        
        # Quest outcomes
        if context.quest_completed:
            parts.append("I've successfully completed a quest. This is a significant achievement.")
        elif context.quest_failed:
            parts.append("I've failed a quest. This is disappointing.")
        
        # Action outcomes
        if context.stuck_detected:
            parts.append("I seem to be stuck and unable to progress. This is frustrating.")
        elif not context.action_succeeded:
            parts.append("My recent action failed. I need to try a different approach.")
        
        # Default neutral
        if not parts:
            parts.append("I'm exploring the world, assessing my surroundings.")
        
        return " ".join(parts)
    
    def _update_statistics(
        self,
        emotion_state: EmotionState,
        context: SkyrimEmotionContext
    ):
        """Update emotion statistics."""
        if context.in_combat:
            if emotion_state.primary_emotion not in self.combat_emotions:
                self.combat_emotions[emotion_state.primary_emotion] = 0
            self.combat_emotions[emotion_state.primary_emotion] += 1
        else:
            if emotion_state.primary_emotion not in self.exploration_emotions:
                self.exploration_emotions[emotion_state.primary_emotion] = 0
            self.exploration_emotions[emotion_state.primary_emotion] += 1
    
    def _update_decision_weights(self, emotion_state: EmotionState):
        """
        Update decision weights based on current emotion.
        
        Emotions influence tactical decisions:
        - FEAR → increase caution, decrease aggression
        - FORTITUDE → increase aggression, decrease caution
        - CURIOSITY → increase exploration
        - SADNESS → decrease all drives
        - JOY → increase all drives
        """
        emotion = emotion_state.primary_emotion
        intensity = emotion_state.intensity
        
        # Reset to baseline
        self.emotion_weights = {k: 0.5 for k in self.emotion_weights}
        
        # Adjust based on emotion
        if emotion == EmotionType.FEAR:
            self.emotion_weights['caution'] = 0.5 + (intensity * 0.4)
            self.emotion_weights['aggression'] = 0.5 - (intensity * 0.3)
        
        elif emotion == EmotionType.FORTITUDE:
            self.emotion_weights['aggression'] = 0.5 + (intensity * 0.4)
            self.emotion_weights['caution'] = 0.5 - (intensity * 0.2)
        
        elif emotion == EmotionType.CURIOSITY:
            self.emotion_weights['exploration'] = 0.5 + (intensity * 0.4)
        
        elif emotion == EmotionType.JOY:
            # Positive emotion increases all drives
            boost = intensity * 0.2
            for key in self.emotion_weights:
                self.emotion_weights[key] = min(1.0, 0.5 + boost)
        
        elif emotion == EmotionType.SADNESS:
            # Negative emotion decreases all drives
            reduction = intensity * 0.2
            for key in self.emotion_weights:
                self.emotion_weights[key] = max(0.0, 0.5 - reduction)
        
        elif emotion == EmotionType.HOPE:
            self.emotion_weights['exploration'] = 0.5 + (intensity * 0.2)
            self.emotion_weights['caution'] = 0.5 + (intensity * 0.1)
        
        elif emotion == EmotionType.GRATITUDE:
            self.emotion_weights['social'] = 0.5 + (intensity * 0.3)
    
    def get_decision_modifier(self, decision_type: str) -> float:
        """
        Get emotion-based modifier for a decision type.
        
        Args:
            decision_type: Type of decision ('aggression', 'caution', 'exploration', 'social')
        
        Returns:
            Modifier value [0.0, 1.0]
        """
        return self.emotion_weights.get(decision_type, 0.5)
    
    def should_retreat(self) -> bool:
        """
        Determine if emotions suggest retreating from combat.
        
        Returns:
            True if fear/caution is high and aggression is low
        """
        current_emotion = self.emotion_engine.get_current_state()
        
        # High fear or sadness + low health → retreat
        if current_emotion.primary_emotion in [EmotionType.FEAR, EmotionType.SADNESS]:
            if current_emotion.intensity > 0.7:
                return True
        
        # High caution weight → retreat
        if self.emotion_weights['caution'] > 0.8:
            return True
        
        return False
    
    def should_be_aggressive(self) -> bool:
        """
        Determine if emotions suggest aggressive combat.
        
        Returns:
            True if fortitude/desire is high
        """
        current_emotion = self.emotion_engine.get_current_state()
        
        # Fortitude or desire → be aggressive
        if current_emotion.primary_emotion in [EmotionType.FORTITUDE, EmotionType.DESIRE]:
            if current_emotion.intensity > 0.6:
                return True
        
        # High aggression weight → attack
        if self.emotion_weights['aggression'] > 0.7:
            return True
        
        return False
    
    def get_exploration_drive(self) -> float:
        """
        Get current exploration drive based on emotions.
        
        Returns:
            Exploration drive [0.0, 1.0]
        """
        current_emotion = self.emotion_engine.get_current_state()
        
        # Curiosity boosts exploration
        if current_emotion.primary_emotion == EmotionType.CURIOSITY:
            return min(1.0, 0.5 + current_emotion.intensity * 0.5)
        
        return self.emotion_weights['exploration']
    
    def get_session_summary(self) -> Dict[str, Any]:
        """Get summary of emotions during session."""
        if not self.session_emotions:
            return {
                'total_emotions': 0,
                'dominant_emotion': 'none',
                'average_valence': 0.0,
                'average_intensity': 0.0
            }
        
        # Compute statistics
        total = len(self.session_emotions)
        
        # Count emotions
        emotion_counts = {}
        total_valence = 0.0
        total_intensity = 0.0
        
        for emotion_state in self.session_emotions:
            emotion = emotion_state.primary_emotion
            if emotion not in emotion_counts:
                emotion_counts[emotion] = 0
            emotion_counts[emotion] += 1
            
            total_valence += emotion_state.valence.valence
            total_intensity += emotion_state.intensity
        
        # Find dominant
        dominant = max(emotion_counts.items(), key=lambda x: x[1])[0] if emotion_counts else EmotionType.NEUTRAL
        
        return {
            'total_emotions': total,
            'dominant_emotion': dominant.value,
            'emotion_distribution': {e.value: c for e, c in emotion_counts.items()},
            'average_valence': total_valence / total,
            'average_intensity': total_intensity / total,
            'combat_emotions': {e.value: c for e, c in self.combat_emotions.items()},
            'exploration_emotions': {e.value: c for e, c in self.exploration_emotions.items()},
            'current_weights': self.emotion_weights.copy()
        }
    
    def log_emotion_state(self, cycle: int):
        """Log current emotion state for debugging."""
        current = self.emotion_engine.get_current_state()
        logger.info(
            f"[EMOTION] Cycle {cycle}: {current.primary_emotion.value} "
            f"(intensity={current.intensity:.2f}, "
            f"valence={current.valence.valence:.2f}, "
            f"{'ACTIVE' if current.is_active else 'PASSIVE'})"
        )
