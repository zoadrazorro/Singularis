"""
Hierarchical goal planner for Skyrim AGI.

Maintains strategic, tactical, and immediate objectives so the agent can
balance long-term quest progress with short-term survival and exploration.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class GoalTier:
    goals: List[str] = field(default_factory=list)
    active_goal: Optional[str] = None

    def promote(self) -> Optional[str]:
        if not self.goals:
            return None
        self.active_goal = self.goals.pop(0)
        return self.active_goal


class HierarchicalGoalPlanner:
    """Three-tiered goal planner."""

    def __init__(self) -> None:
        self.strategic = GoalTier()
        self.tactical = GoalTier()
        self.immediate = GoalTier()
        self.last_scene: Optional[str] = None

    def update_state(self, state: Dict[str, Any], scene: str) -> None:
        self.last_scene = scene
        self._refresh_goals(state)

    def _refresh_goals(self, state: Dict[str, Any]) -> None:
        if not self.strategic.goals:
            self.strategic.goals.extend(self._infer_strategic_goals(state))
        if not self.strategic.active_goal:
            self.strategic.promote()
        if not self.tactical.goals:
            self.tactical.goals.extend(self._infer_tactical_goals(state))
        if not self.tactical.active_goal:
            self.tactical.promote()
        if not self.immediate.goals:
            self.immediate.goals.extend(self._infer_immediate_goals(state))
        if not self.immediate.active_goal:
            self.immediate.promote()

    def _infer_strategic_goals(self, state: Dict[str, Any]) -> List[str]:
        goals: List[str] = []
        if state.get("story_progress", 0) < 0.3:
            goals.append("Advance main quest")
        if state.get("skills", {}).get("Smithing", 0) < 40:
            goals.append("Improve crafting skills")
        return goals or ["Strengthen character build"]

    def _infer_tactical_goals(self, state: Dict[str, Any]) -> List[str]:
        goals: List[str] = []
        if state.get("health", 100) < 50:
            goals.append("Recover health")
        if state.get("enemies_nearby", 0) > 0:
            goals.append("Survive current encounter")
        if state.get("quest_count", 0) > 0:
            goals.append("Progress active quest")
        return goals or ["Explore nearby area"]

    def _infer_immediate_goals(self, state: Dict[str, Any]) -> List[str]:
        goals: List[str] = []
        if state.get("in_combat"):
            goals.append("Win combat")
        elif state.get("in_menu"):
            goals.append("Manage inventory")
        else:
            goals.append("Scout surroundings")
        return goals

    def consume_immediate_goal(self) -> Optional[str]:
        goal = self.immediate.promote()
        if goal is None:
            self.immediate.goals = self._infer_immediate_goals({})
            goal = self.immediate.promote()
        return goal

    def snapshot(self) -> Dict[str, Any]:
        return {
            "strategic": self.strategic.active_goal,
            "tactical": self.tactical.active_goal,
            "immediate": self.immediate.active_goal,
        }
