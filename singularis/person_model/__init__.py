"""
Person Model - Top-level agent abstraction

Wraps MWM and adds:
- Identity (who I am)
- Traits (how I behave)
- Values (what I care about)
- Goals (what I'm trying to achieve)
- Social (how I see others)
- Memory (what I remember)
- Capabilities (what I can do)
- Constraints (what I must not do)

The PersonModel is what ActionArbiter and LLM should think of as "the agent".
"""

from .types import (
    IdentityProfile,
    TraitProfile,
    ValueProfile,
    Goal,
    GoalState,
    Relationship,
    SocialModel,
    EpisodicMemoryRef,
    SemanticMemoryRef,
    MemoryProfile,
    CapabilityProfile,
    ConstraintProfile,
    PersonModel
)

from .registry import PersonRegistry

from .scoring import (
    violates_constraints,
    score_action_for_person,
    get_traits_bonus,
    get_values_bonus,
    get_llm_context
)

from .templates import (
    create_person_from_template,
    PERSON_TEMPLATES,
    get_available_templates
)

from .utils import update_person_mwm, save_person, load_person

__all__ = [
    # Types
    'IdentityProfile',
    'TraitProfile',
    'ValueProfile',
    'Goal',
    'GoalState',
    'Relationship',
    'SocialModel',
    'EpisodicMemoryRef',
    'SemanticMemoryRef',
    'MemoryProfile',
    'CapabilityProfile',
    'ConstraintProfile',
    'PersonModel',
    # Registry
    'PersonRegistry',
    # Scoring
    'violates_constraints',
    'score_action_for_person',
    'get_traits_bonus',
    'get_values_bonus',
    'get_llm_context',
    # Templates
    'create_person_from_template',
    'PERSON_TEMPLATES',
    'get_available_templates',
    # Utils
    'update_person_mwm',
    'save_person',
    'load_person',
]
