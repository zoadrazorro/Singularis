"""
Neuron Swarm: Distributed Intelligence through Hebbian Learning

From ETHICA Part II Proposition XVIII Scholium:
"The human Mind is capable of perceiving a great many things, and is
the more capable, the more its body can be disposed in a great many ways."

From Swarm Intelligence Theory:
Collective behavior emerges from simple local interactions between
agents (neurons), without centralized control.

Architecture:
- 18 Neurons arranged in 3 layers of 6 neurons each
- Each layer specializes in one of the Three Lumina:
  * Layer 1: Lumen Onticum (6 neurons)
  * Layer 2: Lumen Structurale (6 neurons)
  * Layer 3: Lumen Participatum (6 neurons)

Learning Dynamics:
- Hebbian: "Fire together, wire together"
- Emergent patterns through distributed activation
- Self-organization without explicit supervision
"""

from typing import List, Dict, Set, Optional, Tuple
import numpy as np
from loguru import logger

from singularis.tier3_neurons.base import Neuron
from singularis.core.types import Lumen


class NeuronSwarm:
    """
    Swarm of 18 Hebbian neurons organized in 3 luminal layers.

    From MATHEMATICA SINGULARIS:
    Intelligence emerges from the interaction of many simple units,
    each following local rules (Hebbian learning) that produce
    global coherence through self-organization.

    Architecture:
    - Layer 1 (Ontical): 6 neurons sensitive to ontological patterns
    - Layer 2 (Structural): 6 neurons sensitive to logical/formal patterns
    - Layer 3 (Participatory): 6 neurons sensitive to experiential patterns

    Key Features:
    1. Distributed pattern recognition
    2. Emergent collective behavior
    3. Hebbian learning across all connections
    4. Self-organization through activation dynamics
    """

    def __init__(
        self,
        neurons_per_layer: int = 6,
        learning_rate: float = 0.05,
        activation_threshold: float = 0.5,
    ):
        """
        Initialize neuron swarm.

        Args:
            neurons_per_layer: Number of neurons per luminal layer (default: 6)
            learning_rate: Hebbian learning rate for all neurons
            activation_threshold: Firing threshold for all neurons
        """
        self.neurons_per_layer = neurons_per_layer
        self.learning_rate = learning_rate
        self.activation_threshold = activation_threshold

        # Initialize neurons
        self.neurons: Dict[str, Neuron] = {}
        self._initialize_neurons()

        # Activation history for temporal patterns
        self.activation_history: List[Dict[str, float]] = []

        # Global swarm statistics
        self.total_activations = 0
        self.total_patterns_learned = 0

        logger.info(
            "NeuronSwarm initialized",
            extra={
                "total_neurons": len(self.neurons),
                "neurons_per_layer": neurons_per_layer,
                "learning_rate": learning_rate,
            }
        )

    def _initialize_neurons(self):
        """
        Initialize 18 neurons across 3 luminal layers.

        Distribution:
        - Ontical (ℓₒ): 6 neurons (n0-n5)
        - Structural (ℓₛ): 6 neurons (n6-n11)
        - Participatory (ℓₚ): 6 neurons (n12-n17)
        """
        # Layer 1: Lumen Onticum (Being/Energy/Power)
        for i in range(self.neurons_per_layer):
            neuron_id = f"ontical_n{i}"
            self.neurons[neuron_id] = Neuron(
                neuron_id=neuron_id,
                lumen_specialization=Lumen.ONTICUM,
                learning_rate=self.learning_rate,
                activation_threshold=self.activation_threshold,
            )

        # Layer 2: Lumen Structurale (Form/Information/Logic)
        for i in range(self.neurons_per_layer):
            neuron_id = f"structural_n{i}"
            self.neurons[neuron_id] = Neuron(
                neuron_id=neuron_id,
                lumen_specialization=Lumen.STRUCTURALE,
                learning_rate=self.learning_rate,
                activation_threshold=self.activation_threshold,
            )

        # Layer 3: Lumen Participatum (Consciousness/Awareness)
        for i in range(self.neurons_per_layer):
            neuron_id = f"participatory_n{i}"
            self.neurons[neuron_id] = Neuron(
                neuron_id=neuron_id,
                lumen_specialization=Lumen.PARTICIPATUM,
                learning_rate=self.learning_rate,
                activation_threshold=self.activation_threshold,
            )

    def process_pattern(
        self,
        pattern: str,
        lumen_focus: Optional[Lumen] = None,
        iterations: int = 3
    ) -> Dict[str, any]:
        """
        Process a pattern through the swarm.

        Dynamics:
        1. Present pattern to relevant neurons
        2. Neurons activate based on pattern recognition
        3. Activation spreads through Hebbian connections
        4. Iterate for multiple cycles (allows reverberations)
        5. Learn from co-activations

        Args:
            pattern: Input pattern to process
            lumen_focus: Optional focus on specific Lumen layer
            iterations: Number of activation cycles (default: 3)

        Returns:
            Dict with activation results and learned patterns
        """
        logger.info(
            "Processing pattern through swarm",
            extra={
                "pattern_length": len(pattern),
                "lumen_focus": lumen_focus.value if lumen_focus else "all",
                "iterations": iterations,
            }
        )

        # Reset all neurons
        for neuron in self.neurons.values():
            neuron.reset()

        # Iteration loop (allows activation to propagate)
        for iteration in range(iterations):
            # Step 1: Get initial activations from pattern recognition
            initial_activations = self._get_pattern_activations(pattern, lumen_focus)

            # Step 2: Propagate activations through network
            active_neurons = self._propagate_activations(
                initial_activations,
                iteration
            )

            # Step 3: Learn patterns if this is the first iteration
            if iteration == 0:
                self._learn_from_pattern(pattern, active_neurons)

        # Collect results
        result = self._collect_results(pattern)

        self.total_activations += 1

        return result

    def _get_pattern_activations(
        self,
        pattern: str,
        lumen_focus: Optional[Lumen]
    ) -> Dict[str, float]:
        """
        Get initial activations based on pattern recognition.

        Each neuron checks if it recognizes the pattern.
        """
        activations = {}

        for neuron_id, neuron in self.neurons.items():
            # Skip if focusing on different lumen
            if lumen_focus and neuron.lumen_specialization != lumen_focus:
                continue

            # Check pattern recognition
            recognition = neuron.recognize_pattern(pattern)

            if recognition > 0.0:
                activations[neuron_id] = recognition

        return activations

    def _propagate_activations(
        self,
        initial_activations: Dict[str, float],
        iteration: int
    ) -> Set[str]:
        """
        Propagate activations through Hebbian connections.

        For each neuron:
        1. Receive weighted inputs from other neurons
        2. Compute activation
        3. If activation > threshold, neuron "fires"
        4. Hebbian learning strengthens co-active connections

        Returns:
            Set of neurons that are currently firing
        """
        active_neurons = set()

        # Build input dict for each neuron
        for neuron_id, neuron in self.neurons.items():
            # Collect inputs from all other neurons
            inputs = {}

            # Add initial activation (if any)
            if neuron_id in initial_activations:
                inputs[neuron_id] = initial_activations[neuron_id]

            # Add activations from other neurons (weighted by connections)
            for other_id, other_neuron in self.neurons.items():
                if other_id == neuron_id:
                    continue

                # Only include if other neuron is active
                if other_neuron.activation > 0.0:
                    inputs[other_id] = other_neuron.activation

            # Activate neuron (includes Hebbian learning)
            activation = neuron.activate(inputs, active_neurons)

            # Track if firing
            if neuron.is_firing():
                active_neurons.add(neuron_id)

        logger.debug(
            f"Activation propagation iteration {iteration}",
            extra={
                "active_neurons": len(active_neurons),
                "total_neurons": len(self.neurons),
            }
        )

        return active_neurons

    def _learn_from_pattern(self, pattern: str, active_neurons: Set[str]):
        """
        Have active neurons learn the pattern.

        From ETHICA Part II: Memory is strengthened through
        repeated co-activation of ideas.
        """
        for neuron_id in active_neurons:
            neuron = self.neurons[neuron_id]
            neuron.learn_pattern(pattern)

        self.total_patterns_learned += len(active_neurons)

    def _collect_results(self, pattern: str) -> Dict[str, any]:
        """
        Collect activation results from swarm.

        Returns comprehensive statistics about the swarm's response.
        """
        # Get all activations
        activations = {
            neuron_id: neuron.activation
            for neuron_id, neuron in self.neurons.items()
        }

        # Find active neurons
        active_neurons = [
            neuron_id
            for neuron_id, neuron in self.neurons.items()
            if neuron.is_firing()
        ]

        # Get activations by lumen layer
        ontical_activations = [
            neuron.activation
            for neuron in self.neurons.values()
            if neuron.lumen_specialization == Lumen.ONTICUM
        ]
        structural_activations = [
            neuron.activation
            for neuron in self.neurons.values()
            if neuron.lumen_specialization == Lumen.STRUCTURALE
        ]
        participatory_activations = [
            neuron.activation
            for neuron in self.neurons.values()
            if neuron.lumen_specialization == Lumen.PARTICIPATUM
        ]

        # Compute statistics
        result = {
            "pattern": pattern,
            "total_neurons": len(self.neurons),
            "active_neurons": len(active_neurons),
            "active_neuron_ids": active_neurons,
            "activations": activations,
            "average_activation": np.mean(list(activations.values())),
            "max_activation": np.max(list(activations.values())),
            "lumen_statistics": {
                "ontical": {
                    "mean": np.mean(ontical_activations),
                    "max": np.max(ontical_activations),
                },
                "structural": {
                    "mean": np.mean(structural_activations),
                    "max": np.max(structural_activations),
                },
                "participatory": {
                    "mean": np.mean(participatory_activations),
                    "max": np.max(participatory_activations),
                },
            },
            "emergent_coherence": self._compute_emergent_coherence(),
        }

        # Save to history
        self.activation_history.append(activations)

        return result

    def _compute_emergent_coherence(self) -> float:
        """
        Compute emergent coherence of the swarm.

        Coherence = geometric mean of:
        1. Ontical layer average activation
        2. Structural layer average activation
        3. Participatory layer average activation

        This mirrors the Three Lumina coherence at the swarm level.
        """
        ontical_mean = np.mean([
            n.activation for n in self.neurons.values()
            if n.lumen_specialization == Lumen.ONTICUM
        ])

        structural_mean = np.mean([
            n.activation for n in self.neurons.values()
            if n.lumen_specialization == Lumen.STRUCTURALE
        ])

        participatory_mean = np.mean([
            n.activation for n in self.neurons.values()
            if n.lumen_specialization == Lumen.PARTICIPATUM
        ])

        # Geometric mean (same as coherentia calculation)
        coherence = (ontical_mean * structural_mean * participatory_mean) ** (1/3)

        return coherence

    def get_connection_matrix(self) -> np.ndarray:
        """
        Get the full connection weight matrix.

        Returns:
            N x N matrix where M[i][j] = weight from neuron j to neuron i
        """
        n = len(self.neurons)
        matrix = np.zeros((n, n))

        neuron_ids = list(self.neurons.keys())

        for i, target_id in enumerate(neuron_ids):
            target = self.neurons[target_id]

            for j, source_id in enumerate(neuron_ids):
                if source_id in target.state.connection_weights:
                    matrix[i][j] = target.state.connection_weights[source_id]

        return matrix

    def visualize_connections(self, top_k: int = 3) -> str:
        """
        Visualize strongest connections in the swarm.

        Returns:
            String representation of connection graph
        """
        lines = ["NEURON SWARM CONNECTIONS\n", "=" * 60, "\n"]

        for neuron_id, neuron in self.neurons.items():
            strongest = neuron.get_strongest_connections(top_k)

            if strongest:
                lines.append(f"{neuron_id} ({neuron.lumen_specialization.symbol()}):\n")
                for target_id, weight in strongest:
                    target = self.neurons[target_id]
                    lines.append(
                        f"  → {target_id} ({target.lumen_specialization.symbol()}): "
                        f"w={weight:.3f}\n"
                    )
                lines.append("\n")

        return "".join(lines)

    def get_swarm_summary(self) -> Dict[str, any]:
        """Get summary statistics for the swarm."""
        return {
            "total_neurons": len(self.neurons),
            "neurons_per_layer": self.neurons_per_layer,
            "total_activations": self.total_activations,
            "total_patterns_learned": self.total_patterns_learned,
            "average_connections_per_neuron": np.mean([
                len(n.state.connection_weights)
                for n in self.neurons.values()
            ]),
            "total_connections": sum(
                len(n.state.connection_weights)
                for n in self.neurons.values()
            ),
        }
