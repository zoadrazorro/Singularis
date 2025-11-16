"""
Person Model Templates - Predefined PersonModel configurations

Templates for common agent archetypes.
"""

from .types import (
    PersonModel,
    IdentityProfile,
    TraitProfile,
    ValueProfile,
    CapabilityProfile,
    ConstraintProfile,
    GoalState,
    Goal
)
from ..mwm.types import MentalWorldModelState


def create_person_from_template(
    template_name: str,
    person_id: str,
    name: str,
    **overrides
) -> PersonModel:
    """
    Create PersonModel from template.
    
    Args:
        template_name: Template name (e.g., "loyal_companion", "bandit")
        person_id: Unique person ID
        name: Display name
        **overrides: Field overrides
    
    Returns:
        PersonModel instance
    """
    if template_name not in PERSON_TEMPLATES:
        raise ValueError(f"Unknown template: {template_name}")
    
    template = PERSON_TEMPLATES[template_name]
    
    # Create identity
    identity = IdentityProfile(
        person_id=person_id,
        name=name,
        archetype=template['archetype'],
        roles=template['roles'],
        backstory_summary=template.get('backstory', '')
    )
    
    # Create PersonModel
    person = PersonModel(
        identity=identity,
        mwm=MentalWorldModelState(),
        traits=TraitProfile(**template['traits']),
        values=ValueProfile(**template['values']),
        capabilities=CapabilityProfile(**template['capabilities']),
        constraints=ConstraintProfile(**template['constraints']),
        goals=GoalState()
    )
    
    # Add initial goals
    for goal_data in template.get('initial_goals', []):
        goal = Goal(**goal_data)
        person.goals.add_goal(goal, scope=goal_data.get('scope', 'current'))
    
    # Apply overrides
    for key, value in overrides.items():
        if hasattr(person, key):
            setattr(person, key, value)
    
    return person


# ========================================
# Template Definitions
# ========================================

PERSON_TEMPLATES = {
    # ========================================
    # Companions
    # ========================================
    
    "loyal_companion": {
        "archetype": "loyal_warrior",
        "roles": ["companion", "warrior", "follower"],
        "backstory": "A trusted ally who will stand by your side",
        "traits": {
            "aggression": 0.6,
            "caution": 0.5,
            "stealth_preference": 0.3,
            "exploration_drive": 0.5,
            "impulsiveness": 0.4,
            "sociability": 0.7
        },
        "values": {
            "survival_priority": 0.7,
            "damage_priority": 0.6,
            "protect_allies": 0.9,
            "care_for_civilians": 0.7,
            "obedience_to_player": 0.9,
            "greed_for_loot": 0.3,
            "curiosity_drive": 0.5
        },
        "capabilities": {
            "can_use_melee": True,
            "can_use_ranged": True,
            "can_use_magic": False,
            "can_sneak": True,
            "combat_skill": 0.7,
            "stealth_skill": 0.4
        },
        "constraints": {
            "allow_friendly_fire": False,
            "harm_civilians": False,
            "betray_player": False,
            "break_law": True,
            "obey_player_orders": True,
            "risk_self_sacrifice": True
        },
        "initial_goals": [
            {
                "id": "protect_player",
                "description": "Keep the player alive",
                "priority": 0.9,
                "status": "active",
                "scope": "long_term"
            }
        ]
    },
    
    "stealth_companion": {
        "archetype": "sneaky_assassin",
        "roles": ["companion", "rogue", "assassin"],
        "backstory": "A skilled infiltrator who prefers shadows to steel",
        "traits": {
            "aggression": 0.5,
            "caution": 0.7,
            "stealth_preference": 0.9,
            "exploration_drive": 0.6,
            "impulsiveness": 0.3,
            "sociability": 0.4
        },
        "values": {
            "survival_priority": 0.8,
            "damage_priority": 0.7,
            "protect_allies": 0.7,
            "care_for_civilians": 0.5,
            "obedience_to_player": 0.8,
            "greed_for_loot": 0.6,
            "curiosity_drive": 0.7
        },
        "capabilities": {
            "can_use_melee": True,
            "can_use_ranged": True,
            "can_use_magic": False,
            "can_sneak": True,
            "can_pickpocket": True,
            "can_lockpick": True,
            "combat_skill": 0.6,
            "stealth_skill": 0.9
        },
        "constraints": {
            "allow_friendly_fire": False,
            "harm_civilians": False,
            "betray_player": False,
            "break_law": True,
            "obey_player_orders": True,
            "risk_self_sacrifice": False
        },
        "initial_goals": [
            {
                "id": "assist_player",
                "description": "Help player achieve objectives",
                "priority": 0.8,
                "status": "active",
                "scope": "long_term"
            }
        ]
    },
    
    # ========================================
    # Enemies
    # ========================================
    
    "bandit": {
        "archetype": "aggressive_bandit",
        "roles": ["enemy", "bandit", "hostile"],
        "backstory": "A ruthless outlaw who preys on travelers",
        "traits": {
            "aggression": 0.8,
            "caution": 0.3,
            "stealth_preference": 0.2,
            "exploration_drive": 0.4,
            "impulsiveness": 0.7,
            "sociability": 0.5
        },
        "values": {
            "survival_priority": 0.7,
            "damage_priority": 0.8,
            "protect_allies": 0.4,
            "care_for_civilians": 0.1,
            "obedience_to_player": 0.0,
            "greed_for_loot": 0.9,
            "curiosity_drive": 0.3
        },
        "capabilities": {
            "can_use_melee": True,
            "can_use_ranged": True,
            "can_use_magic": False,
            "can_sneak": False,
            "combat_skill": 0.5,
            "stealth_skill": 0.3
        },
        "constraints": {
            "allow_friendly_fire": False,
            "harm_civilians": True,
            "betray_player": True,
            "break_law": True,
            "obey_player_orders": False,
            "risk_self_sacrifice": False
        },
        "initial_goals": [
            {
                "id": "defeat_player",
                "description": "Defeat the player and take their loot",
                "priority": 0.8,
                "status": "active",
                "scope": "current"
            }
        ]
    },
    
    "cautious_guard": {
        "archetype": "lawful_guard",
        "roles": ["guard", "law_enforcement"],
        "backstory": "A city guard sworn to protect civilians",
        "traits": {
            "aggression": 0.4,
            "caution": 0.7,
            "stealth_preference": 0.1,
            "exploration_drive": 0.3,
            "impulsiveness": 0.2,
            "sociability": 0.6
        },
        "values": {
            "survival_priority": 0.8,
            "damage_priority": 0.4,
            "protect_allies": 0.7,
            "care_for_civilians": 0.9,
            "obedience_to_player": 0.3,
            "greed_for_loot": 0.1,
            "curiosity_drive": 0.3
        },
        "capabilities": {
            "can_use_melee": True,
            "can_use_ranged": False,
            "can_use_magic": False,
            "can_sneak": False,
            "combat_skill": 0.6,
            "stealth_skill": 0.2
        },
        "constraints": {
            "allow_friendly_fire": False,
            "harm_civilians": False,
            "betray_player": False,
            "break_law": False,
            "obey_player_orders": False,
            "risk_self_sacrifice": True
        },
        "initial_goals": [
            {
                "id": "maintain_order",
                "description": "Keep the peace and protect civilians",
                "priority": 0.8,
                "status": "active",
                "scope": "long_term"
            }
        ]
    },
    
    # ========================================
    # NPCs
    # ========================================
    
    "merchant": {
        "archetype": "peaceful_merchant",
        "roles": ["merchant", "trader", "civilian"],
        "backstory": "A trader looking to make an honest living",
        "traits": {
            "aggression": 0.1,
            "caution": 0.8,
            "stealth_preference": 0.2,
            "exploration_drive": 0.4,
            "impulsiveness": 0.3,
            "sociability": 0.9
        },
        "values": {
            "survival_priority": 0.9,
            "damage_priority": 0.1,
            "protect_allies": 0.5,
            "care_for_civilians": 0.6,
            "obedience_to_player": 0.5,
            "greed_for_loot": 0.7,
            "curiosity_drive": 0.5
        },
        "capabilities": {
            "can_use_melee": False,
            "can_use_ranged": False,
            "can_use_magic": False,
            "can_sneak": False,
            "combat_skill": 0.2,
            "stealth_skill": 0.3
        },
        "constraints": {
            "allow_friendly_fire": False,
            "harm_civilians": False,
            "betray_player": False,
            "break_law": False,
            "obey_player_orders": False,
            "risk_self_sacrifice": False
        },
        "initial_goals": [
            {
                "id": "make_profit",
                "description": "Buy low, sell high",
                "priority": 0.7,
                "status": "active",
                "scope": "long_term"
            }
        ]
    },
    
    # ========================================
    # Special
    # ========================================
    
    "player_agent": {
        "archetype": "player_controlled",
        "roles": ["player", "protagonist"],
        "backstory": "The player character",
        "traits": {
            "aggression": 0.5,
            "caution": 0.5,
            "stealth_preference": 0.5,
            "exploration_drive": 0.7,
            "impulsiveness": 0.5,
            "sociability": 0.6
        },
        "values": {
            "survival_priority": 0.8,
            "damage_priority": 0.6,
            "protect_allies": 0.7,
            "care_for_civilians": 0.6,
            "obedience_to_player": 1.0,
            "greed_for_loot": 0.6,
            "curiosity_drive": 0.8
        },
        "capabilities": {
            "can_use_melee": True,
            "can_use_ranged": True,
            "can_use_magic": True,
            "can_sneak": True,
            "can_pickpocket": True,
            "can_lockpick": True,
            "combat_skill": 0.7,
            "stealth_skill": 0.7,
            "magic_skill": 0.7
        },
        "constraints": {
            "allow_friendly_fire": False,
            "harm_civilians": False,
            "betray_player": False,
            "break_law": True,
            "obey_player_orders": True,
            "risk_self_sacrifice": False
        },
        "initial_goals": []
    }
}


def get_available_templates() -> list[str]:
    """Get list of available template names."""
    return list(PERSON_TEMPLATES.keys())
