"""
Gameplay analytics for Skyrim AGI.

Aggregates metrics about exploration, combat, quests, and resource
management. Useful for progress dashboards and debugging learning signals.
"""

from __future__ import annotations

from collections import defaultdict
from typing import Any, Dict, Optional


class GameplayAnalytics:
    """Collect high-level metrics."""

    def __init__(self) -> None:
        self.session_start_time: Optional[float] = None
        self.metrics: Dict[str, Any] = defaultdict(float)
        self.counters: Dict[str, int] = defaultdict(int)
        self.last_action: Optional[str] = None

    def update_state(self, state: Dict[str, Any]) -> None:
        if state.get("location"):
            self.metrics["last_location"] = state["location"]
        if state.get("health") is not None:
            self.metrics["avg_health"] = self._running_average(
                self.metrics.get("avg_health", state["health"]), state["health"], self.counters["health_samples"]
            )
            self.counters["health_samples"] += 1
        if state.get("quest_count"):
            self.metrics["quest_updates"] += 1

    def record_action(self, action: str) -> None:
        self.counters[f"action_{action}"] += 1
        self.last_action = action

    def record_reward(self, reward: float) -> None:
        self.metrics["avg_reward"] = self._running_average(
            self.metrics.get("avg_reward", reward), reward, self.counters["reward_samples"]
        )
        self.counters["reward_samples"] += 1

    def session_report(self) -> Dict[str, Any]:
        return {
            "actions_taken": sum(v for k, v in self.counters.items() if k.startswith("action_")),
            "avg_health": self.metrics.get("avg_health"),
            "avg_reward": self.metrics.get("avg_reward"),
            "quest_updates": self.metrics.get("quest_updates", 0),
            "last_action": self.last_action,
        }

    def _running_average(self, current: float, new_value: float, n: int) -> float:
        return (current * n + new_value) / (n + 1) if n >= 0 else new_value
