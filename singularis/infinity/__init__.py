"""
Singularis Infinity Engine - Phase 2 Innovations

Next-generation cognitive systems built on HaackLang + SCCE foundation.
"""

from .coherence_engine_v2 import CoherenceEngineV2, CoherenceReport, CognitiveAdjustments
from .meta_context import MetaContextSystem, Context, ContextLevel, ConditionalRule
from .polyrhythmic_learning import (
    PolyrhythmicLearner,
    AdaptationStrategy,
    RhythmProfile,
    TrackRhythmState,
    create_exploration_profile,
    create_survival_profile,
    create_learning_profile
)
from .memory_engine_v2 import (
    MemoryEngineV2,
    MemoryTrace,
    MemoryType,
    RhythmSignature,
    SemanticPattern
)

__all__ = [
    # Phase 2A
    'CoherenceEngineV2',
    'CoherenceReport',
    'CognitiveAdjustments',
    'MetaContextSystem',
    'Context',
    'ContextLevel',
    'ConditionalRule',
    # Phase 2B
    'PolyrhythmicLearner',
    'AdaptationStrategy',
    'RhythmProfile',
    'TrackRhythmState',
    'create_exploration_profile',
    'create_survival_profile',
    'create_learning_profile',
    'MemoryEngineV2',
    'MemoryTrace',
    'MemoryType',
    'RhythmSignature',
    'SemanticPattern',
]
