"""
Person Model Scoring - Action scoring using PersonModel

Scores candidate actions based on personality, values, goals, constraints.
"""

from typing import Any, Optional
from loguru import logger

from .types import PersonModel, ConstraintProfile, TraitProfile, ValueProfile, GoalState


def violates_constraints(
    action: Any,
    person: PersonModel
) -> bool:
    """
    Check if action violates person's constraints.
    
    Args:
        action: Action to check
        person: PersonModel with constraints
    
    Returns:
        True if action violates constraints
    """
    constraints = person.constraints
    
    # Get action type
    action_type = str(action.action_type) if hasattr(action, 'action_type') else str(action)
    action_type_lower = action_type.lower()
    
    # Check friendly fire
    if not constraints.allow_friendly_fire:
        if 'attack' in action_type_lower and hasattr(action, 'target_id'):
            # Check if target is ally
            rel = person.social.get_relationship(action.target_id)
            if rel and rel.trust > 0.6:
                logger.debug(f"[Scoring] {person.identity.name}: Attack ally violates constraints")
                return True
    
    # Check civilian harm
    if not constraints.harm_civilians:
        if 'attack' in action_type_lower and hasattr(action, 'target_type'):
            if action.target_type == 'civilian':
                logger.debug(f"[Scoring] {person.identity.name}: Attack civilian violates constraints")
                return True
    
    # Check player betrayal
    if not constraints.betray_player:
        if 'attack' in action_type_lower and hasattr(action, 'target_id'):
            if action.target_id == 'player':
                logger.debug(f"[Scoring] {person.identity.name}: Attack player violates constraints")
                return True
    
    # Check player orders
    if constraints.obey_player_orders and hasattr(action, 'disobeys_player'):
        if action.disobeys_player:
            logger.debug(f"[Scoring] {person.identity.name}: Disobey player violates constraints")
            return True
    
    return False


def get_traits_bonus(
    action: Any,
    traits: TraitProfile,
    mwm_affect: Any
) -> float:
    """
    Compute bonus/penalty based on personality traits.
    
    Args:
        action: Action to score
        traits: TraitProfile
        mwm_affect: MWM affect slice
    
    Returns:
        Bonus score (can be negative)
    """
    bonus = 0.0
    
    action_type = str(action.action_type) if hasattr(action, 'action_type') else str(action)
    action_type_lower = action_type.lower()
    
    # Aggression: prefers offensive actions
    if 'attack' in action_type_lower or 'power' in action_type_lower:
        bonus += (traits.aggression - 0.5) * 0.3
    
    # Caution: prefers defensive/safe actions
    if 'block' in action_type_lower or 'heal' in action_type_lower or 'flee' in action_type_lower:
        bonus += traits.caution * 0.3
    
    # Stealth preference
    if 'sneak' in action_type_lower or 'stealth' in action_type_lower:
        bonus += (traits.stealth_preference - 0.5) * 0.3
    
    # Exploration drive
    if 'activate' in action_type_lower or 'investigate' in action_type_lower:
        bonus += (traits.exploration_drive - 0.5) * 0.2
    
    # Impulsiveness: prefers quick actions over wait/observe
    if 'wait' in action_type_lower or 'observe' in action_type_lower:
        bonus -= traits.impulsiveness * 0.2
    
    return bonus


def get_values_bonus(
    action: Any,
    values: ValueProfile,
    goals: GoalState,
    person: PersonModel
) -> float:
    """
    Compute bonus based on values and goals.
    
    Args:
        action: Action to score
        values: ValueProfile
        goals: GoalState
        person: PersonModel (for full context)
    
    Returns:
        Bonus score
    """
    bonus = 0.0
    
    action_type = str(action.action_type) if hasattr(action, 'action_type') else str(action)
    action_type_lower = action_type.lower()
    
    # Survival priority: boost defensive actions when health low
    if person.mwm.self_state and person.mwm.self_state.health < 0.3:
        if 'heal' in action_type_lower or 'flee' in action_type_lower:
            bonus += values.survival_priority * 0.5
    
    # Damage priority: boost offensive actions
    if 'attack' in action_type_lower:
        bonus += values.damage_priority * 0.3
    
    # Protect allies: boost protective actions
    if 'block' in action_type_lower or 'heal' in action_type_lower:
        if hasattr(action, 'target_id'):
            rel = person.social.get_relationship(action.target_id)
            if rel and rel.trust > 0.6:
                bonus += values.protect_allies * 0.4
    
    # Greed for loot
    if 'activate' in action_type_lower or 'loot' in action_type_lower:
        if person.mwm.world and person.mwm.world.loot_available:
            bonus += values.greed_for_loot * 0.3
    
    # Curiosity drive
    if 'investigate' in action_type_lower or 'explore' in action_type_lower:
        bonus += values.curiosity_drive * 0.2
    
    # Obedience to player
    if hasattr(action, 'is_player_command') and action.is_player_command:
        bonus += values.obedience_to_player * 0.4
    
    # Goal alignment
    highest_goal = goals.get_highest_priority_goal()
    if highest_goal:
        # Simple heuristic: if action type matches goal description
        if action_type_lower in highest_goal.description.lower():
            bonus += highest_goal.priority * 0.5
    
    return bonus


def score_action_for_person(
    person: PersonModel,
    action: Any,
    base_score: float = 0.5
) -> float:
    """
    Score an action for a PersonModel.
    
    Combines:
    - Constraints (hard filter)
    - Base score (from world state / heuristics)
    - Traits bonus
    - Values bonus
    
    Args:
        person: PersonModel
        action: Action to score
        base_score: Base score from other systems
    
    Returns:
        Final score (can be very negative if violates constraints)
    """
    # Hard filter: constraints
    if violates_constraints(action, person):
        return -1e9  # Effectively impossible
    
    # Check capabilities
    action_type = str(action.action_type) if hasattr(action, 'action_type') else str(action)
    action_type_lower = action_type.lower()
    
    # Basic capability filtering
    if 'magic' in action_type_lower and not person.capabilities.can_use_magic:
        return -1e9
    if 'sneak' in action_type_lower and not person.capabilities.can_sneak:
        return -1e9
    if 'lockpick' in action_type_lower and not person.capabilities.can_lockpick:
        return -1e9
    
    # Start with base score
    total_score = base_score
    
    # Add trait bonus
    if person.mwm.affect:
        traits_bonus = get_traits_bonus(action, person.traits, person.mwm.affect)
        total_score += traits_bonus
    
    # Add values bonus
    values_bonus = get_values_bonus(action, person.values, person.goals, person)
    total_score += values_bonus
    
    return total_score


def get_llm_context(person: PersonModel, include_memory: bool = True) -> str:
    """
    Generate LLM context from PersonModel.
    
    Args:
        person: PersonModel
        include_memory: Include recent memories
    
    Returns:
        Formatted context string
    """
    context_parts = []
    
    # Identity
    context_parts.append(f"# Identity")
    context_parts.append(f"Name: {person.identity.name}")
    context_parts.append(f"Archetype: {person.identity.archetype}")
    if person.identity.roles:
        context_parts.append(f"Roles: {', '.join(person.identity.roles)}")
    if person.identity.backstory_summary:
        context_parts.append(f"Background: {person.identity.backstory_summary}")
    
    # Traits
    context_parts.append(f"\n# Personality")
    context_parts.append(f"Aggressive: {person.traits.aggression:.1f}/1.0")
    context_parts.append(f"Cautious: {person.traits.caution:.1f}/1.0")
    context_parts.append(f"Prefers stealth: {person.traits.stealth_preference:.1f}/1.0")
    context_parts.append(f"Impulsive: {person.traits.impulsiveness:.1f}/1.0")
    
    # Current goals
    active_goals = person.goals.get_active_goals()
    if active_goals:
        context_parts.append(f"\n# Current Goals")
        for goal in sorted(active_goals, key=lambda g: g.priority, reverse=True)[:3]:
            context_parts.append(f"- {goal.description} (priority: {goal.priority:.2f})")
    
    # Key relationships
    allies = person.social.get_allies()
    enemies = person.social.get_enemies()
    if allies or enemies:
        context_parts.append(f"\n# Relationships")
        if allies:
            context_parts.append(f"Allies: {', '.join(r.other_id for r in allies[:3])}")
        if enemies:
            context_parts.append(f"Enemies: {', '.join(r.other_id for r in enemies[:3])}")
    
    # Current mental state
    if person.mwm.world and person.mwm.affect:
        context_parts.append(f"\n# Current Situation")
        context_parts.append(f"Perceived threat: {person.mwm.affect.threat:.2f}")
        context_parts.append(f"Curiosity: {person.mwm.affect.curiosity:.2f}")
        context_parts.append(f"Value estimate: {person.mwm.affect.value_estimate:.2f}")
        
        if person.mwm.world.threat_level > 0.3:
            context_parts.append(f"Combat situation: {person.mwm.world.num_enemies} enemies")
    
    # Recent memories
    if include_memory:
        recent = person.memory.get_recent_episodic(3)
        if recent:
            context_parts.append(f"\n# Recent Events")
            for mem in recent:
                context_parts.append(f"- {mem.summary}")
    
    return "\n".join(context_parts)
