"""
Menu Interaction Learner

Learns how to navigate and interact with game menus through experience:
1. Tracks menu states and transitions
2. Learns which actions work in which menus
3. Builds a mental model of menu structure
4. Optimizes menu navigation paths

Philosophical grounding:
- Learning through interaction (enactive cognition)
- Building adequate ideas of menu affordances
- Increasing agency through understanding
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from collections import defaultdict
import time


@dataclass
class MenuState:
    """Represents a menu state."""
    menu_type: str  # 'inventory', 'map', 'skills', 'magic', etc.
    timestamp: float
    actions_available: List[str]
    successful_actions: List[str]


@dataclass
class MenuTransition:
    """Represents a transition between menu states."""
    from_menu: str
    to_menu: str
    action: str
    success: bool
    duration: float


class MenuLearner:
    """
    Learns menu navigation through experience.
    
    Builds a graph of menu states and transitions,
    learning optimal paths through menu systems.
    """
    
    def __init__(self):
        """Initialize menu learner."""
        # Menu state history
        self.menu_history: List[MenuState] = []
        
        # Transition graph: {from_menu: {action: to_menu}}
        self.transition_graph: Dict[str, Dict[str, str]] = defaultdict(dict)
        
        # Action success rates: {menu_type: {action: success_rate}}
        self.action_success: Dict[str, Dict[str, float]] = defaultdict(
            lambda: defaultdict(float)
        )
        
        # Action attempt counts: {menu_type: {action: count}}
        self.action_attempts: Dict[str, Dict[str, int]] = defaultdict(
            lambda: defaultdict(int)
        )
        
        # Current menu state
        self.current_menu: Optional[str] = None
        self.menu_entry_time: float = 0.0
        
        # Learned menu structures
        self.menu_structures: Dict[str, Dict[str, Any]] = {
            'inventory': {
                'purpose': 'Manage items and equipment',
                'common_actions': ['equip', 'drop', 'use', 'exit'],
                'navigation': []
            },
            'map': {
                'purpose': 'View world and set markers',
                'common_actions': ['zoom', 'marker', 'fast_travel', 'exit'],
                'navigation': []
            },
            'skills': {
                'purpose': 'Level up and manage perks',
                'common_actions': ['select_perk', 'exit'],
                'navigation': []
            },
            'magic': {
                'purpose': 'Equip spells',
                'common_actions': ['equip_spell', 'exit'],
                'navigation': []
            }
        }
        
        print("[MENU] Menu Learner initialized")
    
    def enter_menu(self, menu_type: str, available_actions: List[str]):
        """
        Record entering a menu.
        
        Args:
            menu_type: Type of menu entered
            available_actions: Actions available in this menu
        """
        self.current_menu = menu_type
        self.menu_entry_time = time.time()
        
        menu_state = MenuState(
            menu_type=menu_type,
            timestamp=self.menu_entry_time,
            actions_available=available_actions,
            successful_actions=[]
        )
        self.menu_history.append(menu_state)
        
        print(f"[MENU] Entered {menu_type} menu")
        print(f"[MENU] Available actions: {available_actions}")
    
    def record_action(
        self,
        action: str,
        success: bool,
        resulted_in_menu: Optional[str] = None
    ):
        """
        Record an action taken in a menu.
        
        Args:
            action: Action taken
            success: Whether action succeeded
            resulted_in_menu: Menu state after action (if changed)
        """
        if not self.current_menu:
            return
        
        # Update action statistics
        self.action_attempts[self.current_menu][action] += 1
        
        current_success = self.action_success[self.current_menu][action]
        attempts = self.action_attempts[self.current_menu][action]
        
        # Update success rate (running average)
        new_success = (current_success * (attempts - 1) + (1.0 if success else 0.0)) / attempts
        self.action_success[self.current_menu][action] = new_success
        
        # Record successful action in current menu state
        if success and self.menu_history:
            self.menu_history[-1].successful_actions.append(action)
        
        # Record transition if menu changed
        if resulted_in_menu and resulted_in_menu != self.current_menu:
            duration = time.time() - self.menu_entry_time
            
            transition = MenuTransition(
                from_menu=self.current_menu,
                to_menu=resulted_in_menu,
                action=action,
                success=success,
                duration=duration
            )
            
            # Update transition graph
            self.transition_graph[self.current_menu][action] = resulted_in_menu
            
            print(f"[MENU] Learned transition: {self.current_menu} --[{action}]--> {resulted_in_menu}")
            
            # Update current menu
            self.current_menu = resulted_in_menu
            self.menu_entry_time = time.time()
    
    def exit_menu(self):
        """Record exiting menu system."""
        if self.current_menu:
            duration = time.time() - self.menu_entry_time
            print(f"[MENU] Exited {self.current_menu} (duration: {duration:.1f}s)")
            self.current_menu = None
    
    def get_recommended_actions(self, menu_type: str) -> List[Tuple[str, float]]:
        """
        Get recommended actions for a menu based on learned success rates.
        
        Args:
            menu_type: Menu type
            
        Returns:
            List of (action, success_rate) tuples, sorted by success rate
        """
        if menu_type not in self.action_success:
            # No experience with this menu, return common actions
            if menu_type in self.menu_structures:
                common = self.menu_structures[menu_type]['common_actions']
                return [(action, 0.5) for action in common]
            return []
        
        # Sort actions by success rate
        actions = self.action_success[menu_type]
        sorted_actions = sorted(
            actions.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        return sorted_actions
    
    def get_menu_path(self, from_menu: str, to_menu: str) -> Optional[List[str]]:
        """
        Find path from one menu to another using learned transitions.
        
        Args:
            from_menu: Starting menu
            to_menu: Target menu
            
        Returns:
            List of actions to take, or None if no path found
        """
        # Simple BFS to find path
        from collections import deque
        
        queue = deque([(from_menu, [])])
        visited = {from_menu}
        
        while queue:
            current, path = queue.popleft()
            
            if current == to_menu:
                return path
            
            # Explore transitions from current menu
            if current in self.transition_graph:
                for action, next_menu in self.transition_graph[current].items():
                    if next_menu not in visited:
                        visited.add(next_menu)
                        queue.append((next_menu, path + [action]))
        
        return None  # No path found
    
    def suggest_menu_action(
        self,
        menu_type: str,
        goal: str = 'explore'
    ) -> Optional[str]:
        """
        Suggest best action to take in current menu.
        
        Args:
            menu_type: Current menu type
            goal: High-level goal ('explore', 'equip', 'navigate', 'exit')
            
        Returns:
            Suggested action, or None
        """
        # Get recommended actions
        recommendations = self.get_recommended_actions(menu_type)
        
        if not recommendations:
            return None
        
        # Filter by goal
        if goal == 'exit':
            # Prioritize exit actions
            for action, rate in recommendations:
                if 'exit' in action.lower() or 'back' in action.lower():
                    return action
        elif goal == 'explore':
            # Try actions we haven't tried much
            for action, rate in recommendations:
                attempts = self.action_attempts[menu_type][action]
                if attempts < 3:  # Explore less-tried actions
                    return action
        
        # Default: return highest success rate action
        return recommendations[0][0]
    
    def get_menu_knowledge(self, menu_type: str) -> Dict[str, Any]:
        """
        Get learned knowledge about a specific menu.
        
        Args:
            menu_type: Menu type
            
        Returns:
            Dict of learned knowledge
        """
        knowledge = {
            'menu_type': menu_type,
            'times_visited': len([m for m in self.menu_history if m.menu_type == menu_type]),
            'actions_learned': len(self.action_success.get(menu_type, {})),
            'successful_actions': [],
            'transitions_from': {},
            'average_success_rate': 0.0
        }
        
        # Get successful actions
        if menu_type in self.action_success:
            for action, rate in self.action_success[menu_type].items():
                if rate > 0.7:  # Consider >70% success as "learned"
                    knowledge['successful_actions'].append(action)
        
        # Get transitions
        if menu_type in self.transition_graph:
            knowledge['transitions_from'] = dict(self.transition_graph[menu_type])
        
        # Calculate average success rate
        if menu_type in self.action_success:
            rates = list(self.action_success[menu_type].values())
            if rates:
                knowledge['average_success_rate'] = sum(rates) / len(rates)
        
        return knowledge
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get menu learner statistics.
        
        Returns:
            Dict of statistics
        """
        total_actions = sum(
            sum(attempts.values())
            for attempts in self.action_attempts.values()
        )
        
        menus_explored = len(self.action_success)
        
        return {
            'menus_explored': menus_explored,
            'total_menu_actions': total_actions,
            'menu_visits': len(self.menu_history),
            'transitions_learned': sum(
                len(transitions) for transitions in self.transition_graph.values()
            ),
            'current_menu': self.current_menu
        }
    
    def print_menu_graph(self):
        """Print learned menu transition graph."""
        print("\n[MENU] Learned Menu Transition Graph:")
        for from_menu, transitions in self.transition_graph.items():
            for action, to_menu in transitions.items():
                success_rate = self.action_success[from_menu].get(action, 0.0)
                print(f"  {from_menu} --[{action} ({success_rate:.0%})]--> {to_menu}")
