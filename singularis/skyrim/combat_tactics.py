"""
Adaptive combat tactics for Skyrim AGI.

Provides context-aware combat recommendations tailored to enemy archetypes
and the agent's preferred combat style. Tracks performance of previously
executed tactics so future decisions can be informed by empirical results.
"""

from __future__ import annotations

from collections import defaultdict, deque
from dataclasses import dataclass
from typing import Any, Deque, Dict, Iterable, List, Optional


@dataclass
class CombatOutcome:
    """Store outcome statistics for a given tactic."""

    successes: int = 0
    attempts: int = 0

    @property
    def success_rate(self) -> float:
        if self.attempts == 0:
            return 0.5
        return self.successes / self.attempts

    def record(self, success: bool) -> None:
        self.attempts += 1
        if success:
            self.successes += 1


class SkyrimCombatTactics:
    """Context-aware combat tactics manager."""

    def __init__(self) -> None:
        self.enemy_patterns: Dict[str, Dict[str, List[str]]] = {
            "dragon": {
                "grounded": ["power_attack", "shout", "block", "heal"],
                "flying": ["bow_attack", "take_cover", "wait_for_opening"],
                "breath_attack": ["dodge", "block", "heal"],
            },
            "mage": {
                "default": ["close_distance", "bash", "power_attack", "block"],
            },
            "warrior": {
                "default": ["block", "bash", "power_attack", "dodge"],
            },
            "archer": {
                "default": ["close_distance", "block", "attack", "dodge"],
            },
        }

        self.combat_styles: Dict[str, Iterable[str]] = {
            "warrior": ["block", "bash", "power_attack", "attack"],
            "mage": ["shout", "heal", "keep_distance", "kite"],
            "thief": ["sneak", "backstab", "dodge", "retreat"],
            "ranged": ["bow_attack", "take_cover", "dodge", "poison_weapon"],
            "hybrid": ["attack", "power_attack", "block", "heal"],
        }

        self._tactic_stats: Dict[str, Dict[str, CombatOutcome]] = defaultdict(
            lambda: defaultdict(CombatOutcome)
        )
        self._recent_context: Deque[Dict[str, Any]] = deque(maxlen=200)
        self._player_build: str = "hybrid"

    def update_player_build(self, build: str) -> None:
        """Update the inferred combat build."""

        if build not in self.combat_styles:
            build = "hybrid"
        self._player_build = build

    def record_action_outcome(
        self,
        enemy_type: str,
        tactic: str,
        success: bool,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Persist the outcome of a combat tactic."""

        enemy_key = enemy_type.lower() or "unknown"
        self._tactic_stats[enemy_key][tactic].record(success)
        if context:
            self._recent_context.appendleft(context)

    def get_optimal_tactic(
        self,
        enemy_type: Optional[str],
        player_build: Optional[str] = None,
        health_percent: float = 100.0,
        stamina_percent: float = 100.0,
        context: Optional[Dict[str, Any]] = None,
    ) -> List[str]:
        """Return a ranked list of tactic suggestions."""

        enemy_key = (enemy_type or "unknown").lower()
        build = player_build or self._player_build
        if build not in self.combat_styles:
            build = "hybrid"

        ranked: List[str] = []

        # Start with tactics tailored to the enemy archetype.
        if enemy_key in self.enemy_patterns:
            pattern = self.enemy_patterns[enemy_key]
            posture = self._determine_enemy_posture(context)
            ranked.extend(pattern.get(posture, pattern.get("default", [])))
        else:
            ranked.extend(["attack", "block", "dodge"])

        # Blend in tactics that match the agent's preferred style.
        style_actions = list(self.combat_styles.get(build, []))
        for action in style_actions:
            if action not in ranked:
                ranked.append(action)

        # Fallback to a small set of universal options.
        for fallback in ("attack", "block", "dodge", "retreat"):
            if fallback not in ranked:
                ranked.append(fallback)

        # Adjust order based on current resources.
        if health_percent < 35 and "heal" in ranked:
            ranked.remove("heal")
            ranked.insert(0, "heal")
        if stamina_percent < 25:
            for heavy_move in ("power_attack", "bash"):
                if heavy_move in ranked:
                    ranked.remove(heavy_move)
                    ranked.append(heavy_move)

        # Reorder using historical success metrics.
        ranked.sort(key=lambda action: self._tactic_stats[enemy_key][action].success_rate, reverse=True)
        return ranked

    def _determine_enemy_posture(self, context: Optional[Dict[str, Any]]) -> str:
        if not context:
            return "default"
        if context.get("enemy_airborne"):
            return "flying"
        if context.get("enemy_preparing_breath"):
            return "breath_attack"
        if context.get("enemy_grounded"):
            return "grounded"
        return "default"

    def describe_recent_performance(self) -> Dict[str, Any]:
        """Return a lightweight snapshot of recent combat trends."""

        summary: Dict[str, Any] = {"recent_encounters": len(self._recent_context)}
        for enemy, action_stats in self._tactic_stats.items():
            summary[enemy] = {
                action: outcome.success_rate for action, outcome in action_stats.items()
            }
        return summary
