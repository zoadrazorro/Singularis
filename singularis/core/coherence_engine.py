"""
CoherenceEngine - The One Function

Computes global coherence C from all subsystems.
This is the 'one thing' all learning and decision-making optimize.

The metaphysical "how well am I being?" made executable.
"""

from typing import Dict
import math
from .being_state import BeingState, LuminaState


class CoherenceEngine:
    """
    Computes global coherence C_global from BeingState.
    
    This is the metaphysical glue-function:
    - Integrates all subsystem coherences
    - Balances the Three Lumina
    - Produces one scalar everyone optimizes
    
    This is Spinoza's conatus (striving to persist in being),
    IIT's Φ (integrated information),
    and Lumen philosophy (balance of Being)
    compiled into one executable function.
    """
    
    def __init__(self, verbose: bool = True):
        """
        Initialize the CoherenceEngine.
        
        Args:
            verbose: Print coherence calculations
        """
        self.verbose = verbose
        
        # Component weights - how much each aspect contributes to global coherence
        # These can be learned/tuned over time
        self.component_weights = {
            'lumina': 0.25,           # Balance of Three Lumina
            'consciousness': 0.20,    # Consciousness metrics (C, Phi, unity)
            'cognitive': 0.15,        # Mind system coherence
            'temporal': 0.10,         # Temporal binding coherence
            'rl': 0.10,               # RL performance
            'meta_rl': 0.08,          # Meta-learning quality
            'emotion': 0.07,          # Emotional coherence
            'voice': 0.05             # Voice-state alignment
        }
        
        # Lumina weights - how to balance the three
        self.lumina_weights = {
            'ontic': 0.33,
            'structural': 0.33,
            'participatory': 0.34
        }
        
        # Coherence history
        self.coherence_history = []
        self.max_history = 1000
        
        if verbose:
            print("[COHERENCE] CoherenceEngine initialized")
            print(f"[COHERENCE] Component weights: {self.component_weights}")
    
    def _lumina_coherence(self, lumina: LuminaState) -> float:
        """
        Compute coherence from the Three Lumina.
        
        Uses geometric mean to ensure all three dimensions are present.
        Balance matters - you can't just max one Lumina and ignore others.
        
        Returns:
            Lumina coherence [0, 1]
        """
        # Geometric mean - all three must be present
        vals = [
            max(1e-6, lumina.ontic),
            max(1e-6, lumina.structural),
            max(1e-6, lumina.participatory)
        ]
        geometric = (vals[0] * vals[1] * vals[2]) ** (1.0 / 3.0)
        
        # Balance bonus - reward balanced Lumina
        balance = lumina.balance_score()
        
        # Combine: 70% geometric mean, 30% balance
        return 0.7 * geometric + 0.3 * balance
    
    def _consciousness_coherence(self, state: BeingState) -> float:
        """
        Compute coherence from consciousness metrics.
        
        Combines:
        - C (coherence) - how coherent the conscious state is
        - Phi (phi) - integrated information
        - Unity index - how unified subsystems are
        
        Returns:
            Consciousness coherence [0, 1]
        """
        # Average of the three consciousness metrics
        return (state.coherence_C + state.unity_index + state.phi_hat) / 3.0
    
    def _cognitive_coherence(self, state: BeingState) -> float:
        """
        Compute coherence from Mind system.
        
        Rewards:
        - High cognitive coherence
        - Few dissonances
        - Active heuristics
        
        Returns:
            Cognitive coherence [0, 1]
        """
        base_coherence = state.cognitive_coherence
        
        # Penalty for dissonances
        dissonance_penalty = min(0.5, len(state.cognitive_dissonances) * 0.05)
        
        # Bonus for active heuristics (up to 0.1)
        heuristic_bonus = min(0.1, len(state.active_heuristics) * 0.02)
        
        return max(0.0, min(1.0, base_coherence - dissonance_penalty + heuristic_bonus))
    
    def _temporal_coherence(self, state: BeingState) -> float:
        """
        Compute coherence from temporal binding.
        
        Rewards:
        - High temporal coherence
        - Few unclosed bindings
        - No stuck loops
        
        Returns:
            Temporal coherence [0, 1]
        """
        base_temporal = state.temporal_coherence
        
        # Penalty for unclosed bindings
        unclosed_penalty = min(0.3, state.unclosed_bindings * 0.03)
        
        # Strong penalty for stuck loops
        stuck_penalty = min(0.5, state.stuck_loop_count * 0.1)
        
        return max(0.0, min(1.0, base_temporal - unclosed_penalty - stuck_penalty))
    
    def _rl_coherence(self, state: BeingState) -> float:
        """
        Compute coherence from RL performance.
        
        Uses average reward as proxy for how well
        the being is achieving its goals.
        
        Returns:
            RL coherence [0, 1]
        """
        # Normalize reward to [0, 1]
        # Assumes rewards are roughly in [-1, 1] range
        normalized_reward = (state.avg_reward + 1.0) / 2.0
        
        # Balance exploration - too much or too little is bad
        exploration_balance = 1.0 - abs(state.exploration_rate - 0.2)  # Ideal ~0.2
        
        # Combine: 80% reward, 20% exploration balance
        return 0.8 * normalized_reward + 0.2 * exploration_balance
    
    def _meta_rl_coherence(self, state: BeingState) -> float:
        """
        Compute coherence from Meta-RL.
        
        Rewards meta-learning quality and knowledge transfer.
        
        Returns:
            Meta-RL coherence [0, 1]
        """
        # Meta score (if available)
        meta_score = state.meta_score
        
        # Bonus for having done meta-analyses
        analysis_bonus = min(0.2, state.total_meta_analyses * 0.01)
        
        return min(1.0, meta_score + analysis_bonus)
    
    def _emotion_coherence(self, state: BeingState) -> float:
        """
        Compute coherence from emotion system.
        
        Checks if emotions are coherent with situation.
        
        Returns:
            Emotion coherence [0, 1]
        """
        # Get emotion coherence from state
        emotion_coh = state.emotion_state.get('coherence', 0.5)
        
        # Intensity should be moderate (not too high, not too low)
        intensity_balance = 1.0 - abs(state.emotion_intensity - 0.5)
        
        # Combine: 70% coherence, 30% intensity balance
        return 0.7 * emotion_coh + 0.3 * intensity_balance
    
    def _voice_coherence(self, state: BeingState) -> float:
        """
        Compute coherence from voice system.
        
        Measures alignment between inner state and outer expression.
        
        Returns:
            Voice coherence [0, 1]
        """
        # Voice alignment (how well voice matches inner state)
        return state.voice_alignment
    
    def compute(self, state: BeingState) -> float:
        """
        Compute the single global coherence C_global from BeingState.
        
        This is the metaphysical 'how well am I being?' score.
        Everything optimizes this one number.
        
        Args:
            state: The current BeingState
            
        Returns:
            Global coherence C_global in [0, 1]
        """
        # Compute component coherences
        lumina_C = self._lumina_coherence(state.lumina)
        consciousness_C = self._consciousness_coherence(state)
        cognitive_C = self._cognitive_coherence(state)
        temporal_C = self._temporal_coherence(state)
        rl_C = self._rl_coherence(state)
        meta_rl_C = self._meta_rl_coherence(state)
        emotion_C = self._emotion_coherence(state)
        voice_C = self._voice_coherence(state)
        
        # Weighted sum
        C_global = (
            self.component_weights['lumina'] * lumina_C +
            self.component_weights['consciousness'] * consciousness_C +
            self.component_weights['cognitive'] * cognitive_C +
            self.component_weights['temporal'] * temporal_C +
            self.component_weights['rl'] * rl_C +
            self.component_weights['meta_rl'] * meta_rl_C +
            self.component_weights['emotion'] * emotion_C +
            self.component_weights['voice'] * voice_C
        )
        
        # Clamp to [0, 1]
        C_global = max(0.0, min(1.0, C_global))
        
        # Store in history
        self.coherence_history.append((state.timestamp, C_global))
        if len(self.coherence_history) > self.max_history:
            self.coherence_history.pop(0)
        
        # Verbose output
        if self.verbose and state.cycle_number % 10 == 0:
            print(f"\n[COHERENCE] Cycle {state.cycle_number}: C_global = {C_global:.3f}")
            print(f"  Lumina:        {lumina_C:.3f} (l_o={state.lumina.ontic:.3f}, l_s={state.lumina.structural:.3f}, l_p={state.lumina.participatory:.3f})")
            print(f"  Consciousness: {consciousness_C:.3f} (C={state.coherence_C:.3f}, Phi={state.phi_hat:.3f}, unity={state.unity_index:.3f})")
            print(f"  Cognitive:     {cognitive_C:.3f}")
            print(f"  Temporal:      {temporal_C:.3f}")
            print(f"  RL:            {rl_C:.3f}")
            print(f"  Meta-RL:       {meta_rl_C:.3f}")
            print(f"  Emotion:       {emotion_C:.3f}")
            print(f"  Voice:         {voice_C:.3f}")
        
        return C_global
    
    def get_component_breakdown(self, state: BeingState) -> Dict[str, float]:
        """
        Get breakdown of coherence by component.
        
        Useful for debugging and optimization.
        
        Args:
            state: The current BeingState
            
        Returns:
            Dictionary of component name -> coherence value
        """
        return {
            'lumina': self._lumina_coherence(state.lumina),
            'consciousness': self._consciousness_coherence(state),
            'cognitive': self._cognitive_coherence(state),
            'temporal': self._temporal_coherence(state),
            'rl': self._rl_coherence(state),
            'meta_rl': self._meta_rl_coherence(state),
            'emotion': self._emotion_coherence(state),
            'voice': self._voice_coherence(state)
        }
    
    def get_trend(self, window: int = 10) -> str:
        """
        Get coherence trend over recent history.
        
        Args:
            window: How many recent samples to analyze
            
        Returns:
            "increasing", "decreasing", or "stable"
        """
        if len(self.coherence_history) < window:
            return "insufficient_data"
        
        recent = [c for _, c in self.coherence_history[-window:]]
        
        # Simple linear trend
        first_half = sum(recent[:window//2]) / (window//2)
        second_half = sum(recent[window//2:]) / (window - window//2)
        
        diff = second_half - first_half
        
        if diff > 0.05:
            return "increasing"
        elif diff < -0.05:
            return "decreasing"
        else:
            return "stable"
    
    def get_stats(self) -> Dict[str, Any]:
        """Get coherence engine statistics."""
        if not self.coherence_history:
            return {
                'samples': 0,
                'current': 0.0,
                'avg': 0.0,
                'min': 0.0,
                'max': 0.0,
                'trend': 'no_data'
            }
        
        coherences = [c for _, c in self.coherence_history]
        
        return {
            'samples': len(coherences),
            'current': coherences[-1],
            'avg': sum(coherences) / len(coherences),
            'min': min(coherences),
            'max': max(coherences),
            'trend': self.get_trend()
        }
    
    def print_stats(self):
        """Print coherence statistics."""
        stats = self.get_stats()
        
        print("\n" + "="*80)
        print("COHERENCE ENGINE STATISTICS".center(80))
        print("="*80)
        print(f"Samples: {stats['samples']}")
        print(f"Current C_global: {stats['current']:.3f}")
        print(f"Average: {stats['avg']:.3f}")
        print(f"Min: {stats['min']:.3f}")
        print(f"Max: {stats['max']:.3f}")
        print(f"Trend: {stats['trend']}")
        print("="*80 + "\n")
