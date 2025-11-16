"""ReflexController: fast emergency overrides that bypass higher reasoning."""

from typing import Optional, Dict, Any
from .action_space import HighLevelAction


class ReflexController:
    """
    Emergency reflex layer that overrides all higher reasoning.
    
    Handles life-threatening situations:
    - Critical health
    - Standing in fire/lava
    - Falling off cliffs
    - Being surrounded
    
    This runs BEFORE RL/LLM and ensures the baby doesn't die
    while thinking about Spinoza.
    """
    
    def __init__(
        self,
        critical_health_threshold: float = 15.0,
        low_health_threshold: float = 30.0,
        danger_enemy_count: int = 4
    ):
        """
        Initialize reflex controller.
        
        Args:
            critical_health_threshold: HP% for emergency actions
            low_health_threshold: HP% for defensive actions
            danger_enemy_count: Enemy count triggering retreat
        """
        self.critical_health = critical_health_threshold
        self.low_health = low_health_threshold
        self.danger_enemies = danger_enemy_count
        
        self.stats = {
            'reflexes_triggered': 0,
            'health_reflexes': 0,
            'combat_reflexes': 0,
        }
    
    def get_reflex_action(self, game_state: Dict[str, Any]) -> Optional[HighLevelAction]:
        """
        Check if any reflex should override normal behavior.
        
        Args:
            game_state: Current game state
            
        Returns:
            Reflex action if triggered, None otherwise
        """
        health = game_state.get('health', 100.0)
        in_combat = game_state.get('in_combat', False)
        enemies = game_state.get('enemies_nearby', 0)
        magicka = game_state.get('magicka', 0.0)
        
        # CRITICAL: Immediate healing if available
        if health < self.critical_health:
            self.stats['reflexes_triggered'] += 1
            self.stats['health_reflexes'] += 1
            
            if magicka > 30:
                print(f"[REFLEX] CRITICAL HEALTH ({health:.0f}%) - EMERGENCY HEAL")
                return HighLevelAction.USE_POTION_HEALTH
            else:
                print(f"[REFLEX] CRITICAL HEALTH ({health:.0f}%) - RETREAT")
                return HighLevelAction.RETREAT_FROM_TARGET
        
        # LOW HEALTH in combat: defensive action
        if in_combat and health < self.low_health:
            self.stats['reflexes_triggered'] += 1
            self.stats['health_reflexes'] += 1
            
            if magicka > 40:
                print(f"[REFLEX] Low health ({health:.0f}%) in combat - healing")
                return HighLevelAction.USE_POTION_HEALTH
            else:
                print(f"[REFLEX] Low health ({health:.0f}%) in combat - blocking")
                return HighLevelAction.BLOCK
        
        # SURROUNDED: retreat immediately
        if in_combat and enemies >= self.danger_enemies:
            self.stats['reflexes_triggered'] += 1
            self.stats['combat_reflexes'] += 1
            print(f"[REFLEX] Surrounded by {enemies} enemies - retreating")
            return HighLevelAction.RETREAT_FROM_TARGET
        
        # STANDING IN FIRE: move away immediately
        in_fire = game_state.get('standing_in_fire', False)
        if in_fire:
            self.stats['reflexes_triggered'] += 1
            self.stats['environmental_reflexes'] = self.stats.get('environmental_reflexes', 0) + 1
            print(f"[REFLEX] Standing in fire - moving away")
            return HighLevelAction.RETREAT_FROM_TARGET
        
        # FALLING: attempt to recover or brace
        velocity_z = game_state.get('velocity_z', 0.0)
        if velocity_z < -10.0:  # Falling fast
            self.stats['reflexes_triggered'] += 1
            self.stats['environmental_reflexes'] = self.stats.get('environmental_reflexes', 0) + 1
            print(f"[REFLEX] Falling detected (velocity: {velocity_z:.1f}) - attempting recovery")
            # In Skyrim, can't do much while falling, but prepare for landing
            return None  # No action available while falling
        
        # STAGGERED: recover stance
        is_staggered = game_state.get('is_staggered', False)
        if is_staggered:
            self.stats['reflexes_triggered'] += 1
            self.stats['combat_reflexes'] += 1
            print(f"[REFLEX] Staggered - recovering stance")
            return HighLevelAction.BLOCK  # Block to recover
        
        # DRAGON OVERHEAD: take cover or use shout
        dragon_overhead = game_state.get('dragon_overhead', False)
        if dragon_overhead:
            self.stats['reflexes_triggered'] += 1
            self.stats['combat_reflexes'] += 1
            print(f"[REFLEX] Dragon overhead - taking defensive action")
            # Could use Dragonrend shout or take cover
            return HighLevelAction.BLOCK  # Defensive stance
        
        return None
    
    def get_stats(self) -> Dict[str, Any]:
        """Get reflex statistics."""
        return self.stats.copy()
