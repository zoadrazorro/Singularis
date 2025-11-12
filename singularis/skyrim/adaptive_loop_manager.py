"""
Adaptive loop scheduling for Skyrim AGI.

Dynamically adjusts perception, reasoning, and fast-loop intervals based on
current situation to balance responsiveness with computational cost.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict


@dataclass
class LoopSettings:
    perception_interval: float
    reasoning_throttle: float
    fast_loop_interval: float


class AdaptiveLoopManager:
    """Maintain loop timing settings based on situational context."""

    def __init__(self, default_settings: LoopSettings) -> None:
        self.default = default_settings
        self.current = LoopSettings(
            perception_interval=default_settings.perception_interval,
            reasoning_throttle=default_settings.reasoning_throttle,
            fast_loop_interval=default_settings.fast_loop_interval,
        )

    def update_for_state(self, scene: str, game_state: Dict[str, any]) -> LoopSettings:
        if scene == "combat" or game_state.get("in_combat"):
            self.current.perception_interval = max(0.15, self.default.perception_interval * 0.6)
            self.current.reasoning_throttle = max(0.05, self.default.reasoning_throttle * 0.5)
            self.current.fast_loop_interval = max(0.2, self.default.fast_loop_interval * 0.6)
        elif scene in {"inventory", "map", "dialogue"}:
            self.current.perception_interval = self.default.perception_interval * 1.5
            self.current.reasoning_throttle = self.default.reasoning_throttle * 1.8
            self.current.fast_loop_interval = self.default.fast_loop_interval * 2.0
        else:
            self.current = LoopSettings(
                perception_interval=self.default.perception_interval,
                reasoning_throttle=self.default.reasoning_throttle,
                fast_loop_interval=self.default.fast_loop_interval,
            )
        return self.current

    def get_interval(self, name: str) -> float:
        if name == "perception":
            return self.current.perception_interval
        if name == "reasoning":
            return self.current.reasoning_throttle
        if name == "fast_loop":
            return self.current.fast_loop_interval
        raise ValueError(f"Unknown loop interval '{name}'")
