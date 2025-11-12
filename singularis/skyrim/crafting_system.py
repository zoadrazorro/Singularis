"""
Crafting and enchanting helper for Skyrim AGI.

Provides lightweight heuristics for determining when crafting is worthwhile
and which enchantments best suit the agent's current build.
"""

from __future__ import annotations

from typing import Dict, Optional


class CraftingSystem:
    """Evaluate crafting and enchanting decisions."""

    def __init__(self) -> None:
        self.known_recipes: Dict[str, Dict[str, float]] = {
            "steel_ingot": {"value": 25.0},
            "iron_dagger": {"value": 20.0},
        }
        self.enchantment_preferences: Dict[str, Dict[str, float]] = {
            "warrior": {"Fortify One-Handed": 0.8, "Fortify Stamina": 0.6},
            "mage": {"Fortify Destruction": 0.8, "Fortify Magicka": 0.7},
            "thief": {"Fortify Sneak": 0.8, "Fortify Carry Weight": 0.5},
            "hybrid": {"Fortify Health": 0.6, "Fortify Stamina": 0.6},
        }

    def should_craft_item(self, recipe: Dict[str, any], materials: Dict[str, int]) -> bool:
        value = self._estimate_item_value(recipe)
        cost = self._estimate_material_cost(recipe, materials)
        if cost == 0:
            return False
        return value > cost * 1.3

    def _estimate_item_value(self, recipe: Dict[str, any]) -> float:
        name = recipe.get("name")
        if name and name in self.known_recipes:
            return self.known_recipes[name].get("value", 0.0)
        return recipe.get("base_value", 0.0)

    def _estimate_material_cost(self, recipe: Dict[str, any], materials: Dict[str, int]) -> float:
        cost = 0.0
        for material, qty in recipe.get("materials", {}).items():
            stock = materials.get(material, 0)
            if stock < qty:
                return float("inf")
            cost += qty * 5.0
        return cost

    def select_enchantment(self, item_type: str, build: str) -> Optional[str]:
        build_preferences = self.enchantment_preferences.get(build, {})
        best_enchantment = None
        best_score = -1.0
        for enchantment, score in build_preferences.items():
            if score > best_score:
                best_score = score
                best_enchantment = enchantment
        return best_enchantment
