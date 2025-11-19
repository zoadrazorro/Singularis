import time
from typing import Dict, List, Optional
from .types import GameState, SceneType
from .actions import Action

class MockSkyrimEnv:
    """
    A simulated Skyrim environment for offline testing and training.
    
    Mimics the game state transitions and responses to actions without
    requiring the actual game to be running.
    """
    
    def __init__(self):
        self.reset()
        
    def reset(self) -> GameState:
        """Resets the environment to an initial state."""
        self.state = GameState(
            health=100.0,
            magicka=100.0,
            stamina=100.0,
            level=1,
            location_name="Whiterun",
            time_of_day=12.0,
            scene=SceneType.OUTDOOR_CITY,
            in_combat=False,
            gold=100
        )
        self.last_action = None
        self.step_count = 0
        return self.state
        
    def step(self, action: str) -> GameState:
        """
        Executes an action in the mock environment and returns the new state.
        
        Args:
            action: The action name (e.g., 'move_forward', 'attack').
            
        Returns:
            The updated GameState.
        """
        self.last_action = action
        self.step_count += 1
        
        # Simulate state transitions based on action
        if action == "attack":
            if self.state.in_combat:
                # Deal damage to enemy (simulated)
                self.state.enemies_nearby = max(0, self.state.enemies_nearby - 1)
                if self.state.enemies_nearby == 0:
                    self.state.in_combat = False
                    self.state.scene = SceneType.OUTDOOR_WILDERNESS
            else:
                # Attacking air costs stamina
                self.state.stamina = max(0.0, self.state.stamina - 10.0)
                
        elif action == "move_forward":
            # Moving costs a tiny bit of stamina if running?
            # For now, just assume it changes location eventually
            if self.step_count % 10 == 0:
                self.state.location_name = "Riverwood"
                self.state.scene = SceneType.OUTDOOR_WILDERNESS
                
        elif action == "open_inventory":
            self.state.in_menu = True
            self.state.menu_type = "inventory"
            self.state.scene = SceneType.INVENTORY
            
        elif action == "close_menu":
            self.state.in_menu = False
            self.state.menu_type = ""
            self.state.scene = SceneType.OUTDOOR_WILDERNESS
            
        elif action == "wait":
            self.state.health = min(100.0, self.state.health + 5.0)
            self.state.stamina = min(100.0, self.state.stamina + 10.0)
            self.state.magicka = min(100.0, self.state.magicka + 5.0)
            
        # Simulate random events
        if not self.state.in_combat and self.step_count % 20 == 0:
            # Random encounter
            self.state.in_combat = True
            self.state.enemies_nearby = 2
            self.state.scene = SceneType.COMBAT
            
        return self.state

    def render(self):
        """Prints the current state summary."""
        print(f"Step: {self.step_count} | Loc: {self.state.location_name} | Scene: {self.state.scene.value}")
        print(f"HP: {self.state.health:.1f} | SP: {self.state.stamina:.1f} | MP: {self.state.magicka:.1f}")
        if self.state.in_combat:
            print(f"COMBAT! Enemies: {self.state.enemies_nearby}")
