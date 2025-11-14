"""
HaackLang 2.0 Operators - Full Cognitive DSL

Extends HaackLang from a guard language to a full cognitive DSL with:
- Fuzzy logic operators (⊕, ⊗)
- Paraconsistent operators (⊓, ⊔)
- Temporal operators (Δ, last, future)
- Multi-track operations (sync, interfere)
- Probabilistic operators (P, ~)

These operators compile to SCCE primitives and execute on the track system.
"""

from typing import List, Dict, Optional, Callable, Any
from dataclasses import dataclass
import math


# ========== Fuzzy Logic Operators ==========

def fuzzy_blend(a: float, b: float, weight: float = 0.5) -> float:
    """
    Fuzzy blend operator: ⊕
    
    Blends two truth values with specified weight.
    
    Args:
        a: First truth value [0, 1]
        b: Second truth value [0, 1]
        weight: Blend weight [0, 1], default 0.5 (equal blend)
    
    Returns:
        Blended value [0, 1]
    
    Example:
        main ⊕ perception  # Equal blend
        main ⊕(0.1) slow   # 90% main, 10% slow
    """
    return (1.0 - weight) * a + weight * b


def fuzzy_product(a: float, b: float) -> float:
    """
    Fuzzy product operator: ⊗
    
    Multiplicative combination (both must be high).
    
    Args:
        a: First truth value [0, 1]
        b: Second truth value [0, 1]
    
    Returns:
        Product [0, 1]
    
    Example:
        danger ⊗ proximity  # High only if both are high
    """
    return a * b


def fuzzy_sum(a: float, b: float) -> float:
    """
    Fuzzy sum operator: ⊞
    
    Probabilistic sum (at least one is high).
    
    Args:
        a: First truth value [0, 1]
        b: Second truth value [0, 1]
    
    Returns:
        Sum [0, 1]
    
    Example:
        threat ⊞ uncertainty  # High if either is high
    """
    return a + b - a * b


def fuzzy_not(a: float) -> float:
    """
    Fuzzy negation: ¬
    
    Args:
        a: Truth value [0, 1]
    
    Returns:
        Negation [0, 1]
    """
    return 1.0 - a


# ========== Paraconsistent Operators ==========

@dataclass
class ParaconsistentValue:
    """
    Paraconsistent truth value: can hold both P and ¬P.
    
    Attributes:
        belief: Degree of belief in P [0, 1]
        disbelief: Degree of belief in ¬P [0, 1]
    
    Note: belief + disbelief can exceed 1.0 (contradiction)
          or be less than 1.0 (uncertainty)
    """
    belief: float
    disbelief: float
    
    def is_contradictory(self, threshold: float = 0.5) -> bool:
        """Check if value is contradictory"""
        return self.belief > threshold and self.disbelief > threshold
    
    def is_uncertain(self, threshold: float = 0.5) -> bool:
        """Check if value is uncertain"""
        return self.belief < threshold and self.disbelief < threshold
    
    def certainty(self) -> float:
        """Degree of certainty [0, 1]"""
        return abs(self.belief - self.disbelief)
    
    def contradiction(self) -> float:
        """Degree of contradiction [0, 1]"""
        return min(self.belief, self.disbelief)


def paraconsistent_and(a: ParaconsistentValue, b: ParaconsistentValue) -> ParaconsistentValue:
    """
    Paraconsistent conjunction: ⊓
    
    Combines evidence for and against.
    
    Args:
        a: First paraconsistent value
        b: Second paraconsistent value
    
    Returns:
        Combined paraconsistent value
    
    Example:
        evidence_for ⊓ evidence_against  # Can hold both
    """
    return ParaconsistentValue(
        belief=min(a.belief, b.belief),
        disbelief=min(a.disbelief, b.disbelief)
    )


def paraconsistent_or(a: ParaconsistentValue, b: ParaconsistentValue) -> ParaconsistentValue:
    """
    Paraconsistent disjunction: ⊔
    
    Args:
        a: First paraconsistent value
        b: Second paraconsistent value
    
    Returns:
        Combined paraconsistent value
    """
    return ParaconsistentValue(
        belief=max(a.belief, b.belief),
        disbelief=max(a.disbelief, b.disbelief)
    )


def paraconsistent_to_fuzzy(p: ParaconsistentValue) -> float:
    """
    Convert paraconsistent value to fuzzy truth value.
    
    Uses: (belief - disbelief + 1) / 2
    
    Returns:
        Fuzzy value [0, 1]
    """
    return (p.belief - p.disbelief + 1.0) / 2.0


# ========== Temporal Operators ==========

class TemporalWindow:
    """
    Temporal window for storing recent values.
    
    Used by last(n) operator.
    """
    
    def __init__(self, size: int):
        self.size = size
        self.values: List[float] = []
        self.timestamps: List[float] = []
    
    def add(self, value: float, timestamp: float):
        """Add value to window"""
        self.values.append(value)
        self.timestamps.append(timestamp)
        
        # Keep only last N
        if len(self.values) > self.size:
            self.values.pop(0)
            self.timestamps.pop(0)
    
    def get_values(self) -> List[float]:
        """Get all values in window"""
        return list(self.values)
    
    def mean(self) -> float:
        """Average value in window"""
        return sum(self.values) / len(self.values) if self.values else 0.0
    
    def trend(self) -> float:
        """Trend: positive = increasing, negative = decreasing"""
        if len(self.values) < 2:
            return 0.0
        
        # Simple linear regression slope
        n = len(self.values)
        x = list(range(n))
        y = self.values
        
        x_mean = sum(x) / n
        y_mean = sum(y) / n
        
        numerator = sum((x[i] - x_mean) * (y[i] - y_mean) for i in range(n))
        denominator = sum((x[i] - x_mean) ** 2 for i in range(n))
        
        if denominator == 0:
            return 0.0
        
        return numerator / denominator


def temporal_derivative(window: TemporalWindow) -> float:
    """
    Temporal derivative operator: Δ
    
    Computes rate of change over time.
    
    Args:
        window: Temporal window with recent values
    
    Returns:
        Rate of change (positive = increasing, negative = decreasing)
    
    Example:
        Δdanger > 0  # Danger is increasing
        Δfear < -0.1  # Fear is decreasing rapidly
    """
    return window.trend()


def temporal_last(window: TemporalWindow, n: int) -> List[float]:
    """
    Last N values operator: last(n)
    
    Returns the last N values from temporal window.
    
    Args:
        window: Temporal window
        n: Number of recent values to retrieve
    
    Returns:
        List of last N values
    
    Example:
        last(3)  # Last 3 values
        mean(last(5))  # Average of last 5
    """
    values = window.get_values()
    return values[-n:] if len(values) >= n else values


def temporal_future(current: float, derivative: float, steps: int = 1) -> float:
    """
    Future prediction operator: future(n)
    
    Linear extrapolation based on current trend.
    
    Args:
        current: Current value
        derivative: Rate of change
        steps: Number of steps to predict ahead
    
    Returns:
        Predicted future value
    
    Example:
        future(danger, 3)  # Predicted danger in 3 cycles
    """
    return current + derivative * steps


# ========== Multi-Track Operators ==========

def track_sync(tracks: List['Track'], target_phase: float = 0.0):
    """
    Synchronize multiple tracks: sync(track1, track2, ...)
    
    Aligns track phases to target phase.
    
    Args:
        tracks: List of tracks to synchronize
        target_phase: Target phase [0, 2π]
    
    Example:
        sync(perception, intuition, reflection)  # Align all three
    """
    for track in tracks:
        track.phase = target_phase


def track_interference(track_a: 'Track', track_b: 'Track') -> float:
    """
    Compute interference between tracks: interfere(track1, track2)
    
    Positive = constructive (synchronized)
    Negative = destructive (out of phase)
    
    Args:
        track_a: First track
        track_b: Second track
    
    Returns:
        Interference strength [-1, 1]
    
    Example:
        if interfere(fast, slow) > 0.8:
            # Tracks are synchronized
    """
    # Phase difference
    phase_diff = abs(track_a.phase - track_b.phase)
    
    # Normalize to [0, π]
    phase_diff = phase_diff % (2 * math.pi)
    if phase_diff > math.pi:
        phase_diff = 2 * math.pi - phase_diff
    
    # Convert to interference: 0° = +1, 180° = -1
    interference = math.cos(phase_diff)
    
    return interference


def track_align(track_a: 'Track', track_b: 'Track', strength: float = 0.1):
    """
    Align track_a toward track_b: align(track1, track2, strength)
    
    Gradually adjusts track_a's phase toward track_b.
    
    Args:
        track_a: Track to adjust
        track_b: Target track
        strength: Alignment strength [0, 1]
    
    Example:
        align(intuition, perception, 0.2)  # Intuition follows perception
    """
    # Compute phase difference
    diff = track_b.phase - track_a.phase
    
    # Normalize to [-π, π]
    while diff > math.pi:
        diff -= 2 * math.pi
    while diff < -math.pi:
        diff += 2 * math.pi
    
    # Adjust phase
    track_a.phase += diff * strength


# ========== Probabilistic Operators ==========

def probability(evidence: float, prior: float = 0.5) -> float:
    """
    Probability operator: P(hypothesis | evidence)
    
    Bayesian update with uniform likelihood.
    
    Args:
        evidence: Evidence strength [0, 1]
        prior: Prior probability [0, 1]
    
    Returns:
        Posterior probability [0, 1]
    
    Example:
        P(threat | observations) * prior
    """
    # Simplified Bayesian update
    # P(H|E) ∝ P(E|H) * P(H)
    # Assuming P(E|H) = evidence, P(E|¬H) = 1 - evidence
    
    likelihood_h = evidence
    likelihood_not_h = 1.0 - evidence
    
    numerator = likelihood_h * prior
    denominator = likelihood_h * prior + likelihood_not_h * (1.0 - prior)
    
    if denominator == 0:
        return prior
    
    return numerator / denominator


def uncertainty(value: float, confidence: float = 1.0) -> float:
    """
    Uncertainty operator: ~value
    
    Applies confidence weighting.
    
    Args:
        value: Base value [0, 1]
        confidence: Confidence level [0, 1]
    
    Returns:
        Uncertainty-weighted value [0, 1]
    
    Example:
        ~danger  # Uncertain danger
        danger * confidence(0.8)  # 80% confident
    """
    # Low confidence pulls toward 0.5 (maximum uncertainty)
    return value * confidence + 0.5 * (1.0 - confidence)


# ========== Operator Registry ==========

class OperatorRegistry:
    """
    Registry of all HaackLang operators.
    
    Maps operator symbols to implementation functions.
    """
    
    def __init__(self):
        self.operators: Dict[str, Callable] = {
            # Fuzzy logic
            '⊕': fuzzy_blend,
            '⊗': fuzzy_product,
            '⊞': fuzzy_sum,
            '¬': fuzzy_not,
            
            # Paraconsistent
            '⊓': paraconsistent_and,
            '⊔': paraconsistent_or,
            
            # Temporal
            'Δ': temporal_derivative,
            'last': temporal_last,
            'future': temporal_future,
            
            # Multi-track
            'sync': track_sync,
            'interfere': track_interference,
            'align': track_align,
            
            # Probabilistic
            'P': probability,
            '~': uncertainty,
        }
        
        # Aliases
        self.aliases = {
            'blend': '⊕',
            'and': '⊓',
            'or': '⊔',
            'not': '¬',
            'derivative': 'Δ',
        }
    
    def get(self, operator: str) -> Optional[Callable]:
        """Get operator implementation"""
        # Check direct match
        if operator in self.operators:
            return self.operators[operator]
        
        # Check alias
        if operator in self.aliases:
            return self.operators[self.aliases[operator]]
        
        return None
    
    def register(self, symbol: str, func: Callable):
        """Register custom operator"""
        self.operators[symbol] = func
    
    def list_operators(self) -> List[str]:
        """List all available operators"""
        return list(self.operators.keys())


# ========== Global Registry ==========

OPERATORS = OperatorRegistry()


# ========== Example Usage ==========

if __name__ == "__main__":
    print("HaackLang 2.0 Operators")
    print("=" * 50)
    
    # Fuzzy blend
    print("\n1. Fuzzy Blend (⊕)")
    main = 0.8
    perception = 0.6
    result = fuzzy_blend(main, perception, 0.3)
    print(f"  main={main} ⊕(0.3) perception={perception} = {result:.2f}")
    
    # Paraconsistent
    print("\n2. Paraconsistent And (⊓)")
    evidence_for = ParaconsistentValue(belief=0.8, disbelief=0.2)
    evidence_against = ParaconsistentValue(belief=0.3, disbelief=0.7)
    combined = paraconsistent_and(evidence_for, evidence_against)
    print(f"  Evidence for: belief={evidence_for.belief}, disbelief={evidence_for.disbelief}")
    print(f"  Evidence against: belief={evidence_against.belief}, disbelief={evidence_against.disbelief}")
    print(f"  Combined: belief={combined.belief}, disbelief={combined.disbelief}")
    print(f"  Contradictory: {combined.is_contradictory()}")
    
    # Temporal
    print("\n3. Temporal Derivative (Δ)")
    window = TemporalWindow(size=5)
    for i, val in enumerate([0.2, 0.3, 0.5, 0.6, 0.7]):
        window.add(val, float(i))
    derivative = temporal_derivative(window)
    print(f"  Values: {window.get_values()}")
    print(f"  Δ = {derivative:.3f} (increasing)")
    
    # Probability
    print("\n4. Probability (P)")
    evidence = 0.8
    prior = 0.3
    posterior = probability(evidence, prior)
    print(f"  P(threat | evidence={evidence}) with prior={prior}")
    print(f"  Posterior = {posterior:.2f}")
    
    print("\n" + "=" * 50)
    print(f"Total operators: {len(OPERATORS.list_operators())}")
    print(f"Operators: {', '.join(OPERATORS.list_operators()[:10])}...")


# ========== Mock Track for Type Hints ==========

class Track:
    """Mock track class for type hints"""
    def __init__(self, name: str, period: int, phase: float = 0.0):
        self.name = name
        self.period = period
        self.phase = phase
