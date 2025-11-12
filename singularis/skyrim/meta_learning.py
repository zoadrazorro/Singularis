"""
Meta-learning utilities for Skyrim AGI.

Tracks effectiveness of different playstyles so the agent can gradually bias
future decisions toward strategies that yield higher rewards.
"""

from __future__ import annotations

from collections import defaultdict
from typing import Dict


class MetaLearner:
    """Analyze playstyle effectiveness over time."""

    def __init__(self) -> None:
        self.coherence_by_style: Dict[str, float] = defaultdict(float)
        self.success_by_style: Dict[str, int] = defaultdict(int)
        self.samples_by_style: Dict[str, int] = defaultdict(int)

    def record_experience(self, style: str, coherence_gain: float, success: bool) -> None:
        self.coherence_by_style[style] += coherence_gain
        self.success_by_style[style] += int(success)
        self.samples_by_style[style] += 1

    def evaluate(self) -> Dict[str, float]:
        results: Dict[str, float] = {}
        for style, total_gain in self.coherence_by_style.items():
            samples = max(1, self.samples_by_style[style])
            success_rate = self.success_by_style[style] / samples
            results[style] = total_gain / samples + 0.2 * success_rate
        return results
