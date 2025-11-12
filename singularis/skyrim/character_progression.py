"""
Character progression planner for Skyrim AGI.

Determines preferred playstyle, suggests perk allocation, and tracks skill
growth to ensure the agent focuses on effective builds.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


PLAYSTYLE_THRESHOLDS = {
    "warrior": {"melee": 0.55},
    "mage": {"magic": 0.55},
    "thief": {"stealth": 0.55},
    "hybrid": {},
}


@dataclass
class PerkPlan:
    perks: List[str] = field(default_factory=list)
    reasoning: str = ""


class CharacterProgression:
    """Track and plan character growth."""

    def __init__(self) -> None:
        self.current_skills: Dict[str, int] = {}
        self.playstyle_stats: Dict[str, float] = {"melee": 0.0, "magic": 0.0, "stealth": 0.0}
        self.build: str = "hybrid"
        self.level: int = 1
        self.pending_perks: int = 0
        self.perk_history: List[str] = []

    def update_from_state(self, state: Dict[str, any]) -> None:
        self.level = state.get("player_level", self.level)
        skills = state.get("skills", {})
        if isinstance(skills, dict):
            for name, value in skills.items():
                if isinstance(value, (int, float)):
                    self.current_skills[name] = int(value)
        playstyle = state.get("action_counts", {})
        if isinstance(playstyle, dict):
            for key in ("melee", "magic", "stealth"):
                if key in playstyle:
                    self.playstyle_stats[key] = playstyle[key]
        self.pending_perks = state.get("available_perks", self.pending_perks)
        self._determine_build()

    def _determine_build(self) -> None:
        for build, thresholds in PLAYSTYLE_THRESHOLDS.items():
            if all(self.playstyle_stats.get(cat, 0.0) >= value for cat, value in thresholds.items()):
                self.build = build
                return
        self.build = "hybrid"

    def plan_perk_allocation(self) -> PerkPlan:
        if self.pending_perks <= 0:
            return PerkPlan()
        perks: List[str] = []
        reasoning: List[str] = []
        if self.build == "warrior":
            perks.append("Armsman")
            reasoning.append("Increase melee damage for warrior build.")
        elif self.build == "mage":
            perks.append("Destruction Novice")
            reasoning.append("Reduce spell cost for mage build.")
        elif self.build == "thief":
            perks.append("Stealth")
            reasoning.append("Improve stealth effectiveness.")
        else:
            perks.append("Haggling")
            reasoning.append("Hybrid build benefits from general utility.")
        return PerkPlan(perks=perks[: self.pending_perks], reasoning=" ".join(reasoning))

    def record_perk_choice(self, perk_name: str) -> None:
        self.perk_history.append(perk_name)
        if self.pending_perks > 0:
            self.pending_perks -= 1

    def describe_progress(self) -> Dict[str, any]:
        return {
            "build": self.build,
            "level": self.level,
            "pending_perks": self.pending_perks,
            "perk_history": list(self.perk_history),
        }
