"""
Base Neuron: Hebbian Learning Micro-Agent

From Neuroscience (Donald Hebb, 1949):
"When an axon of cell A is near enough to excite cell B and repeatedly
or persistently takes part in firing it, some growth process or metabolic
change takes place in one or both cells such that A's efficiency, as one
of the cells firing B, is increased."

Mathematical Formulation:
    Δw_ij = η · a_i · a_j

Where:
    - w_ij: connection weight from neuron j to i
    - η: learning rate (typically 0.01-0.1)
    - a_i: activation of neuron i
    - a_j: activation of neuron j

From ETHICA Part II:
The mind and body are one and the same thing, conceived under different
attributes. These neurons embody both:
    - Physical: Activation patterns (Lumen Onticum)
    - Informational: Weights and connections (Lumen Structurale)
    - Experiential: Pattern recognition (Lumen Participatum)
"""

from typing import Dict, List, Optional, Set
from dataclasses import dataclass, field
import numpy as np
from loguru import logger

from singularis.core.types import Lumen


@dataclass
class HebbianState:
    """
    State of Hebbian learning for a neuron.

    From Hebb (1949): Learning occurs through synaptic plasticity.
    """
    total_activations: int = 0
    total_updates: int = 0
    average_activation: float = 0.0
    last_update_time: float = 0.0

    # Connection strengths to other neurons
    # Key: neuron_id, Value: weight
    connection_weights: Dict[str, float] = field(default_factory=dict)

    # Coactivation counts (for Hebbian learning)
    # Key: neuron_id, Value: count
    coactivation_counts: Dict[str, int] = field(default_factory=dict)


class Neuron:
    """
    Base Neuron with Hebbian learning.

    From ETHICA + Neuroscience:
    A minimal unit of distributed intelligence that learns through
    correlation-based synaptic plasticity.

    Key Features:
    1. Hebbian Learning: Δw = η · a_i · a_j
    2. Activation Function: sigmoid(Σ w_i · x_i)
    3. Weight Decay: Prevents runaway growth
    4. Pattern Recognition: Learns to respond to specific patterns

    From MATHEMATICA SINGULARIS:
    Neurons increase coherence locally through pattern detection,
    contributing to global system coherence.
    """

    def __init__(
        self,
        neuron_id: str,
        lumen_specialization: Lumen,
        learning_rate: float = 0.05,
        activation_threshold: float = 0.5,
        decay_rate: float = 0.001,
    ):
        """
        Initialize neuron.

        Args:
            neuron_id: Unique identifier
            lumen_specialization: Which Lumen this neuron specializes in
            learning_rate: Hebbian learning rate (η)
            activation_threshold: Minimum activation to "fire"
            decay_rate: Weight decay to prevent runaway growth
        """
        self.neuron_id = neuron_id
        self.lumen_specialization = lumen_specialization
        self.learning_rate = learning_rate
        self.activation_threshold = activation_threshold
        self.decay_rate = decay_rate

        # Hebbian state
        self.state = HebbianState()

        # Current activation level [0, 1]
        self.activation = 0.0

        # Pattern memory: patterns this neuron has learned to recognize
        # Key: pattern hash, Value: (pattern, activation strength)
        self.pattern_memory: Dict[str, tuple] = {}

        logger.debug(
            f"Neuron initialized",
            extra={
                "neuron_id": neuron_id,
                "lumen": lumen_specialization.value,
                "learning_rate": learning_rate,
            }
        )

    def activate(
        self,
        inputs: Dict[str, float],
        active_neurons: Optional[Set[str]] = None
    ) -> float:
        """
        Compute activation based on weighted inputs.

        Activation function: sigmoid(Σ w_i · x_i)

        Args:
            inputs: Dict of neuron_id -> activation value
            active_neurons: Set of currently active neuron IDs

        Returns:
            Activation level [0, 1]
        """
        # Compute weighted sum
        weighted_sum = 0.0

        for source_id, source_activation in inputs.items():
            weight = self.state.connection_weights.get(source_id, 0.0)
            weighted_sum += weight * source_activation

        # Apply sigmoid activation
        self.activation = self._sigmoid(weighted_sum)

        # Update statistics
        self.state.total_activations += 1
        self.state.average_activation = (
            (self.state.average_activation * (self.state.total_activations - 1)
             + self.activation)
            / self.state.total_activations
        )

        # Hebbian learning: if we're active AND other neurons are active
        if active_neurons and self.is_firing():
            self._hebbian_update(active_neurons)

        return self.activation

    def _sigmoid(self, x: float) -> float:
        """Sigmoid activation function: σ(x) = 1 / (1 + e^(-x))"""
        return 1.0 / (1.0 + np.exp(-x))

    def is_firing(self) -> bool:
        """Check if neuron is currently firing (activation > threshold)."""
        return self.activation >= self.activation_threshold

    def _hebbian_update(self, active_neurons: Set[str]):
        """
        Apply Hebbian learning rule.

        "Neurons that fire together, wire together."

        For each neuron j that is co-active with this neuron i:
            Δw_ij = η · a_i · a_j

        Args:
            active_neurons: Set of currently firing neuron IDs
        """
        my_activation = self.activation

        for other_id in active_neurons:
            if other_id == self.neuron_id:
                continue  # Don't self-connect

            # Get or initialize weight
            current_weight = self.state.connection_weights.get(other_id, 0.0)

            # Hebbian update: Δw = η · a_i · a_j
            # Assume other neurons also firing at ~threshold level
            other_activation = self.activation_threshold  # Approximation

            weight_change = self.learning_rate * my_activation * other_activation

            # Update weight
            new_weight = current_weight + weight_change

            # Apply weight decay
            new_weight *= (1.0 - self.decay_rate)

            # Clip to reasonable range [-1, 1]
            new_weight = np.clip(new_weight, -1.0, 1.0)

            self.state.connection_weights[other_id] = new_weight

            # Update coactivation count
            self.state.coactivation_counts[other_id] = (
                self.state.coactivation_counts.get(other_id, 0) + 1
            )

        self.state.total_updates += 1

    def learn_pattern(self, pattern: str, strength: float = 1.0):
        """
        Learn to recognize a specific pattern.

        From ETHICA Part II: Memory is formed through repeated
        experiences that strengthen associations.

        Args:
            pattern: Pattern identifier (could be text, hash, etc.)
            strength: Initial association strength
        """
        pattern_hash = str(hash(pattern))

        if pattern_hash in self.pattern_memory:
            # Strengthen existing pattern
            _, current_strength = self.pattern_memory[pattern_hash]
            new_strength = min(1.0, current_strength + self.learning_rate * strength)
            self.pattern_memory[pattern_hash] = (pattern, new_strength)
        else:
            # New pattern
            self.pattern_memory[pattern_hash] = (pattern, strength * self.learning_rate)

        logger.debug(
            f"Pattern learned",
            extra={
                "neuron_id": self.neuron_id,
                "pattern_length": len(pattern),
                "strength": self.pattern_memory[pattern_hash][1],
            }
        )

    def recognize_pattern(self, pattern: str) -> float:
        """
        Check if this neuron recognizes a pattern.

        Returns:
            Recognition strength [0, 1]
        """
        pattern_hash = str(hash(pattern))

        if pattern_hash in self.pattern_memory:
            _, strength = self.pattern_memory[pattern_hash]
            return strength

        # Check for partial matches (substring similarity)
        max_similarity = 0.0
        for stored_hash, (stored_pattern, strength) in self.pattern_memory.items():
            similarity = self._pattern_similarity(pattern, stored_pattern)
            weighted_similarity = similarity * strength
            max_similarity = max(max_similarity, weighted_similarity)

        return max_similarity

    def _pattern_similarity(self, p1: str, p2: str) -> float:
        """
        Compute similarity between two patterns.

        Simple method: Jaccard similarity of words.
        """
        words1 = set(p1.lower().split())
        words2 = set(p2.lower().split())

        if not words1 or not words2:
            return 0.0

        intersection = words1 & words2
        union = words1 | words2

        return len(intersection) / len(union) if union else 0.0

    def get_strongest_connections(self, top_k: int = 5) -> List[tuple]:
        """
        Get strongest outgoing connections.

        Returns:
            List of (neuron_id, weight) tuples, sorted by weight
        """
        connections = [
            (nid, weight)
            for nid, weight in self.state.connection_weights.items()
        ]

        connections.sort(key=lambda x: abs(x[1]), reverse=True)

        return connections[:top_k]

    def reset(self):
        """Reset neuron state (but preserve learned weights)."""
        self.activation = 0.0

    def __repr__(self) -> str:
        return (
            f"Neuron(id={self.neuron_id}, "
            f"lumen={self.lumen_specialization.symbol()}, "
            f"activation={self.activation:.3f}, "
            f"connections={len(self.state.connection_weights)})"
        )
