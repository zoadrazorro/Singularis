"""Tier-3 Swarm Neurons: Hebbian Learning Network

From ETHICA Part II Proposition XIII:
"The object of the idea constituting the human Mind is the Body."

From Neuroscience (Hebb's Postulate):
"Neurons that fire together, wire together."

This tier implements a swarm of 18 micro-agents (neurons) that learn
through Hebbian mechanisms, enabling distributed pattern recognition
and emergent collective intelligence.
"""

from .base import Neuron
from .swarm import NeuronSwarm
from singularis.core.types import Lumen

__all__ = [
    "Neuron",
    "NeuronSwarm",
    "Lumen",
]
