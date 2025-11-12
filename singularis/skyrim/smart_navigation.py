"""
Navigation support for Skyrim AGI.

Maintains a lightweight spatial memory and produces context-aware movement
recommendations. Designed to operate without direct access to in-game pathing
APIs while still providing meaningful guidance.
"""

from __future__ import annotations

import math
from collections import defaultdict, deque
from dataclasses import dataclass
from typing import Any, Deque, Dict, List, Optional, Tuple


@dataclass
class Waypoint:
    location: str
    context: Dict[str, Any]


class SmartNavigator:
    """Learned navigation helper."""

    def __init__(self) -> None:
        self.map_memory: Dict[str, Dict[str, Any]] = {}
        self.fast_travel_points: set[str] = set()
        self.discovered_locations: set[str] = set()
        self.recent_routes: Deque[List[str]] = deque(maxlen=25)
        self._location_graph: Dict[str, Dict[str, float]] = defaultdict(dict)
        self._last_known_location: Optional[str] = None

    def learn_location(self, location: str, context: Optional[Dict[str, Any]] = None) -> None:
        if not location:
            return
        self.discovered_locations.add(location)
        if location not in self.map_memory:
            self.map_memory[location] = {}
        if context:
            self.map_memory[location].update(context)
        self._last_known_location = location

    def record_transition(self, source: str, destination: str, distance: float = 1.0) -> None:
        if not source or not destination or source == destination:
            return
        self._location_graph[source][destination] = min(
            distance, self._location_graph[source].get(destination, float("inf"))
        )
        self._location_graph[destination][source] = min(
            distance, self._location_graph[destination].get(source, float("inf"))
        )

    def suggest_exploration_action(self, context: Dict[str, Any]) -> str:
        nearby = context.get("nearby_points", [])
        if not nearby:
            return "move_forward"
        unexplored = [point for point in nearby if point not in self.discovered_locations]
        if unexplored:
            target = unexplored[0]
        else:
            target = nearby[0]
        self.recent_routes.appendleft([self._last_known_location or "Unknown", target])
        return "navigate"

    def plan_route(self, target_location: str) -> List[str]:
        start = self._last_known_location
        if not start or start == target_location:
            return []
        visited = {start}
        frontier: List[Tuple[float, str, List[str]]] = [(0.0, start, [start])]
        best_route: List[str] = []
        best_score = float("inf")

        while frontier:
            distance, current, path = frontier.pop(0)
            if current == target_location:
                if distance < best_score:
                    best_score = distance
                    best_route = path
                continue
            for neighbor, weight in self._location_graph.get(current, {}).items():
                if neighbor in visited:
                    continue
                visited.add(neighbor)
                new_distance = distance + weight
                heuristic = self._heuristic_cost(neighbor, target_location)
                frontier.append((new_distance + heuristic, neighbor, path + [neighbor]))
                frontier.sort(key=lambda item: item[0])
        return best_route

    def _heuristic_cost(self, location: str, target: str) -> float:
        if location == target:
            return 0.0
        loc_info = self.map_memory.get(location, {})
        target_info = self.map_memory.get(target, {})
        loc_pos = loc_info.get("position")
        target_pos = target_info.get("position")
        if not loc_pos or not target_pos:
            return 1.0
        return math.dist(loc_pos, target_pos)

    def snapshot(self) -> Dict[str, Any]:
        return {
            "discovered_locations": len(self.discovered_locations),
            "known_routes": len(self.recent_routes),
            "fast_travel_points": len(self.fast_travel_points),
        }
