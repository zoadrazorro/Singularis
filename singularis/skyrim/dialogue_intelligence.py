"""
Dialogue intelligence utilities for Skyrim AGI.

Analyzes dialogue options, tracks NPC relationships, and supplies
recommendations that balance quest progress with relationship gains.
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass
class RelationshipRecord:
    disposition: float = 0.0
    interactions: int = 0
    preferred_topics: List[str] = None

    def __post_init__(self) -> None:
        if self.preferred_topics is None:
            self.preferred_topics = []


class DialogueIntelligence:
    """Dialogue decision helper."""

    def __init__(self) -> None:
        self.relationships: Dict[str, RelationshipRecord] = {}
        self._llm_interface: Optional[Any] = None

    def set_llm_interface(self, llm_interface: Any) -> None:
        self._llm_interface = llm_interface

    async def analyze_dialogue_options(
        self,
        npc_name: str,
        options: List[str],
        context: Optional[str] = None,
    ) -> Optional[str]:
        if not options:
            return None

        # Heuristic preference: choose options that progress quests or improve relations.
        relationship = self.relationships.get(npc_name, RelationshipRecord())
        best_option = max(options, key=lambda opt: self._score_option(opt, relationship))

        if self._llm_interface:
            prompt = (
                f"NPC: {npc_name}\n"
                f"Context: {context or 'None'}\n"
                "Options:\n" + "\n".join(f"- {opt}" for opt in options) + "\n\n"
                "Recommend the option that provides the best outcome for quest progression "
                "or relationship building. Respond with the exact option text."
            )
            try:
                response = await asyncio.wait_for(
                    self._llm_interface.generate(prompt=prompt, max_tokens=64),
                    timeout=6.0,
                )
                suggestion = response.get("content", "").strip()
                for option in options:
                    if option.lower() in suggestion.lower():
                        best_option = option
                        break
            except asyncio.TimeoutError:
                pass
            except Exception:
                pass

        return best_option

    def _score_option(self, option: str, relationship: RelationshipRecord) -> float:
        score = 0.0
        lower = option.lower()
        if "help" in lower or "quest" in lower:
            score += 0.6
        if "thank" in lower or "friend" in lower:
            score += 0.3
        for topic in relationship.preferred_topics:
            if topic in lower:
                score += 0.2
        return score

    def update_relationship(self, npc_name: str, outcome: str) -> None:
        record = self.relationships.setdefault(npc_name, RelationshipRecord())
        record.interactions += 1
        if outcome == "positive":
            record.disposition = min(1.0, record.disposition + 0.1)
        elif outcome == "negative":
            record.disposition = max(-1.0, record.disposition - 0.1)

    def get_relationship_status(self, npc_name: str) -> RelationshipRecord:
        return self.relationships.get(npc_name, RelationshipRecord())
