"""
Polyrhythmic Learning System - Innovation 4

Makes track periods learnable parameters that adapt based on:
- Performance feedback (reward signals)
- Context-specific rhythm profiles
- Harmonic relationships between tracks
- Habituation as harmonic learning

Key concepts:
- Track periods are no longer fixed - they evolve
- Rhythms adapt to optimize coherence and performance
- Context-specific rhythm profiles (exploration vs survival)
- Harmonic learning: tracks naturally synchronize or desynchronize
"""

from typing import Dict, List, Optional, Tuple, Callable
from dataclasses import dataclass, field
from enum import Enum
import math


class AdaptationStrategy(Enum):
    """How track periods adapt"""
    REWARD_BASED = "reward_based"      # Adapt based on reward signals
    COHERENCE_BASED = "coherence_based"  # Adapt to maximize coherence
    HARMONIC = "harmonic"              # Adapt to harmonic ratios
    CONTEXT_SPECIFIC = "context_specific"  # Different rhythms per context


@dataclass
class RhythmProfile:
    """
    Context-specific rhythm configuration.
    
    Each context (exploration, survival, learning) has optimal rhythm patterns.
    """
    name: str
    track_periods: Dict[str, int]  # Optimal periods for each track
    harmonic_ratios: Dict[Tuple[str, str], float]  # Desired ratios between tracks
    plasticity: float = 1.0  # How quickly rhythms adapt in this context
    
    def __repr__(self):
        return f"RhythmProfile({self.name}, {len(self.track_periods)} tracks)"


@dataclass
class TrackRhythmState:
    """
    Learnable rhythm state for a single track.
    
    Tracks the current period and adaptation history.
    """
    track_name: str
    current_period: int
    base_period: int  # Original period
    min_period: int = 10
    max_period: int = 1000
    
    # Learning parameters
    learning_rate: float = 0.01
    momentum: float = 0.9
    
    # Adaptation history
    period_history: List[int] = field(default_factory=list)
    reward_history: List[float] = field(default_factory=list)
    velocity: float = 0.0  # Momentum term
    
    # Performance tracking
    total_activations: int = 0
    successful_activations: int = 0
    coherence_contributions: List[float] = field(default_factory=list)
    
    def success_rate(self) -> float:
        """Compute success rate"""
        if self.total_activations == 0:
            return 0.5
        return self.successful_activations / self.total_activations
    
    def avg_coherence_contribution(self) -> float:
        """Average coherence contribution"""
        if not self.coherence_contributions:
            return 0.5
        return sum(self.coherence_contributions[-20:]) / len(self.coherence_contributions[-20:])
    
    def __repr__(self):
        return f"TrackRhythm({self.track_name}, period={self.current_period})"


class PolyrhythmicLearner:
    """
    Adaptive polyrhythmic learning system.
    
    Makes track periods learnable parameters that optimize for:
    - Reward maximization
    - Coherence maximization
    - Harmonic relationships
    - Context-specific performance
    """
    
    def __init__(
        self,
        strategy: AdaptationStrategy = AdaptationStrategy.REWARD_BASED,
        global_learning_rate: float = 0.01,
        harmonic_attraction: float = 0.1,
        verbose: bool = True
    ):
        self.strategy = strategy
        self.global_learning_rate = global_learning_rate
        self.harmonic_attraction = harmonic_attraction
        self.verbose = verbose
        
        # Track states
        self.track_states: Dict[str, TrackRhythmState] = {}
        
        # Context-specific profiles
        self.rhythm_profiles: Dict[str, RhythmProfile] = {}
        self.current_profile: Optional[str] = None
        
        # Global state
        self.global_beat = 0
        self.total_adaptations = 0
        self.adaptation_history: List[Dict] = []
        
        # Harmonic relationships
        self.harmonic_pairs: List[Tuple[str, str, float]] = []  # (track1, track2, target_ratio)
        
        if self.verbose:
            print("[POLYRHYTHMIC LEARNING] System initialized")
            print(f"  Strategy: {strategy.value}")
            print(f"  Learning rate: {global_learning_rate}")
            print(f"  Harmonic attraction: {harmonic_attraction}")
    
    def register_track(
        self,
        track_name: str,
        initial_period: int,
        min_period: int = 10,
        max_period: int = 1000,
        learning_rate: Optional[float] = None
    ):
        """
        Register a track for adaptive learning.
        
        Args:
            track_name: Name of the track
            initial_period: Starting period
            min_period: Minimum allowed period
            max_period: Maximum allowed period
            learning_rate: Track-specific learning rate (or use global)
        """
        lr = learning_rate if learning_rate is not None else self.global_learning_rate
        
        state = TrackRhythmState(
            track_name=track_name,
            current_period=initial_period,
            base_period=initial_period,
            min_period=min_period,
            max_period=max_period,
            learning_rate=lr
        )
        
        self.track_states[track_name] = state
        
        if self.verbose:
            print(f"[POLYRHYTHMIC LEARNING] Registered track: {track_name}")
            print(f"  Period: {initial_period}, Range: [{min_period}, {max_period}]")
    
    def add_rhythm_profile(self, profile: RhythmProfile):
        """Add a context-specific rhythm profile"""
        self.rhythm_profiles[profile.name] = profile
        
        if self.verbose:
            print(f"[POLYRHYTHMIC LEARNING] Added profile: {profile.name}")
    
    def set_active_profile(self, profile_name: str):
        """Switch to a different rhythm profile"""
        if profile_name not in self.rhythm_profiles:
            if self.verbose:
                print(f"[POLYRHYTHMIC LEARNING] WARNING: Profile '{profile_name}' not found")
            return
        
        self.current_profile = profile_name
        
        if self.verbose:
            print(f"[POLYRHYTHMIC LEARNING] Switched to profile: {profile_name}")
    
    def add_harmonic_constraint(self, track1: str, track2: str, target_ratio: float):
        """
        Add harmonic relationship between two tracks.
        
        Args:
            track1: First track name
            track2: Second track name
            target_ratio: Desired period ratio (period1 / period2)
        
        Example:
            # Fast track should be 5x faster than slow track
            learner.add_harmonic_constraint('fast', 'slow', 0.2)
        """
        self.harmonic_pairs.append((track1, track2, target_ratio))
        
        if self.verbose:
            print(f"[POLYRHYTHMIC LEARNING] Harmonic constraint: {track1}/{track2} = {target_ratio:.2f}")
    
    def adapt_from_reward(
        self,
        track_name: str,
        reward: float,
        coherence: Optional[float] = None
    ):
        """
        Adapt track period based on reward signal.
        
        Uses gradient-free optimization (evolutionary strategy):
        - If reward high: keep current period
        - If reward low: explore nearby periods
        
        Args:
            track_name: Track to adapt
            reward: Reward signal (-1.0 to 1.0)
            coherence: Optional coherence contribution
        """
        if track_name not in self.track_states:
            return
        
        state = self.track_states[track_name]
        state.reward_history.append(reward)
        
        if coherence is not None:
            state.coherence_contributions.append(coherence)
        
        # Compute gradient estimate
        # If recent rewards increasing → keep direction
        # If recent rewards decreasing → reverse direction
        if len(state.reward_history) >= 2:
            recent_rewards = state.reward_history[-10:]
            reward_trend = recent_rewards[-1] - recent_rewards[0]
            
            # Update velocity with momentum
            gradient = reward_trend * 100  # Scale to period units
            state.velocity = state.momentum * state.velocity + state.learning_rate * gradient
            
            # Apply update
            new_period = state.current_period + int(state.velocity)
            new_period = max(state.min_period, min(state.max_period, new_period))
            
            if new_period != state.current_period:
                state.period_history.append(state.current_period)
                state.current_period = new_period
                self.total_adaptations += 1
                
                if self.verbose:
                    print(f"[POLYRHYTHMIC LEARNING] Adapted {track_name}: {state.period_history[-1]} -> {new_period}")
                    print(f"  Reward trend: {reward_trend:.3f}, Velocity: {state.velocity:.2f}")
    
    def adapt_from_coherence(
        self,
        coherence_scores: Dict[str, float],
        global_coherence: float
    ):
        """
        Adapt all tracks to maximize global coherence.
        
        Tracks with low coherence contribution get period adjustments.
        
        Args:
            coherence_scores: Per-track coherence contributions
            global_coherence: Overall system coherence
        """
        for track_name, coherence in coherence_scores.items():
            if track_name not in self.track_states:
                continue
            
            state = self.track_states[track_name]
            state.coherence_contributions.append(coherence)
            
            # If coherence low, try adjusting period
            if coherence < 0.5:
                # Try moving toward harmonic ratios with other tracks
                self._apply_harmonic_attraction(track_name)
    
    def adapt_to_context(self, context_name: str):
        """
        Adapt all tracks to context-specific rhythm profile.
        
        Args:
            context_name: Name of context (must have registered profile)
        """
        if context_name not in self.rhythm_profiles:
            if self.verbose:
                print(f"[POLYRHYTHMIC LEARNING] No profile for context: {context_name}")
            return
        
        profile = self.rhythm_profiles[context_name]
        self.current_profile = context_name
        
        # Gradually move tracks toward profile targets
        for track_name, target_period in profile.track_periods.items():
            if track_name not in self.track_states:
                continue
            
            state = self.track_states[track_name]
            current = state.current_period
            
            # Move toward target with plasticity factor
            delta = int((target_period - current) * profile.plasticity * 0.1)
            
            if delta != 0:
                new_period = current + delta
                new_period = max(state.min_period, min(state.max_period, new_period))
                
                if new_period != current:
                    state.period_history.append(current)
                    state.current_period = new_period
                    self.total_adaptations += 1
                    
                    if self.verbose:
                        print(f"[POLYRHYTHMIC LEARNING] Context adaptation: {track_name}")
                        print(f"  {current} -> {new_period} (target: {target_period})")
    
    def _apply_harmonic_attraction(self, track_name: str):
        """
        Apply harmonic attraction to move track toward harmonic ratios.
        
        This creates emergent synchronization between related tracks.
        """
        if track_name not in self.track_states:
            return
        
        state = self.track_states[track_name]
        
        # Find all harmonic constraints involving this track
        attractions = []
        
        for t1, t2, ratio in self.harmonic_pairs:
            if t1 == track_name and t2 in self.track_states:
                # This track should be ratio * other_period
                other_period = self.track_states[t2].current_period
                target_period = int(ratio * other_period)
                attractions.append(target_period)
            
            elif t2 == track_name and t1 in self.track_states:
                # This track should be other_period / ratio
                other_period = self.track_states[t1].current_period
                target_period = int(other_period / ratio)
                attractions.append(target_period)
        
        if not attractions:
            return
        
        # Average all attractions
        target = sum(attractions) // len(attractions)
        current = state.current_period
        
        # Move toward target with harmonic attraction strength
        delta = int((target - current) * self.harmonic_attraction)
        
        if delta != 0:
            new_period = current + delta
            new_period = max(state.min_period, min(state.max_period, new_period))
            
            if new_period != current:
                state.period_history.append(current)
                state.current_period = new_period
                self.total_adaptations += 1
                
                if self.verbose:
                    print(f"[POLYRHYTHMIC LEARNING] Harmonic attraction: {track_name}")
                    print(f"  {current} -> {new_period} (target: {target})")
    
    def get_current_period(self, track_name: str) -> Optional[int]:
        """Get current period for a track"""
        if track_name in self.track_states:
            return self.track_states[track_name].current_period
        return None
    
    def get_all_periods(self) -> Dict[str, int]:
        """Get all current periods"""
        return {name: state.current_period for name, state in self.track_states.items()}
    
    def compute_harmonic_coherence(self) -> float:
        """
        Compute how well tracks align with harmonic constraints.
        
        Returns:
            Score 0.0-1.0, where 1.0 means perfect harmonic alignment
        """
        if not self.harmonic_pairs:
            return 1.0
        
        total_error = 0.0
        
        for t1, t2, target_ratio in self.harmonic_pairs:
            if t1 not in self.track_states or t2 not in self.track_states:
                continue
            
            p1 = self.track_states[t1].current_period
            p2 = self.track_states[t2].current_period
            
            actual_ratio = p1 / p2
            error = abs(actual_ratio - target_ratio) / target_ratio
            total_error += error
        
        avg_error = total_error / len(self.harmonic_pairs)
        coherence = max(0.0, 1.0 - avg_error)
        
        return coherence
    
    def get_statistics(self) -> Dict:
        """Get learning statistics"""
        return {
            'total_tracks': len(self.track_states),
            'total_adaptations': self.total_adaptations,
            'current_profile': self.current_profile,
            'harmonic_coherence': self.compute_harmonic_coherence(),
            'avg_success_rate': sum(s.success_rate() for s in self.track_states.values()) / max(1, len(self.track_states)),
            'strategy': self.strategy.value
        }
    
    def __repr__(self):
        return f"PolyrhythmicLearner({len(self.track_states)} tracks, {self.total_adaptations} adaptations)"


# ========== Predefined Rhythm Profiles ==========

def create_exploration_profile() -> RhythmProfile:
    """Rhythm profile for exploration context"""
    return RhythmProfile(
        name='exploration',
        track_periods={
            'perception': 50,
            'curiosity': 100,
            'reflection': 200,
            'strategic': 500
        },
        harmonic_ratios={
            ('perception', 'curiosity'): 0.5,
            ('curiosity', 'reflection'): 0.5
        },
        plasticity=1.2
    )


def create_survival_profile() -> RhythmProfile:
    """Rhythm profile for survival/danger context"""
    return RhythmProfile(
        name='survival',
        track_periods={
            'perception': 20,      # Very fast perception
            'fast_response': 30,   # Quick reactions
            'danger_assessment': 50,
            'strategic': 200       # Slower strategic thinking
        },
        harmonic_ratios={
            ('perception', 'fast_response'): 0.67,
            ('fast_response', 'danger_assessment'): 0.6
        },
        plasticity=0.8  # Less plastic in survival mode
    )


def create_learning_profile() -> RhythmProfile:
    """Rhythm profile for learning/consolidation context"""
    return RhythmProfile(
        name='learning',
        track_periods={
            'perception': 100,
            'reflection': 150,
            'memory_consolidation': 200,
            'pattern_recognition': 300
        },
        harmonic_ratios={
            ('perception', 'reflection'): 0.67,
            ('reflection', 'memory_consolidation'): 0.75
        },
        plasticity=1.5  # High plasticity for learning
    )
