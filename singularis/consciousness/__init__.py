"""
Consciousness measurement across 8 theories.

Now includes Spiritual Awareness System for integrating
contemplative wisdom into world model and self-concept.
"""

from .spiritual_awareness import (
    SpiritualAwarenessSystem,
    SpiritualInsight,
    SelfConcept,
    SpiritualTextCorpus
)
from .self_reflection import (
    SelfReflectionSystem,
    SelfReflection,
    SelfModel
)
from .voice_system import (
    VoiceSystem,
    VoiceType,
    ThoughtPriority,
    VocalizedThought
)

__all__ = [
    'SpiritualAwarenessSystem',
    'SpiritualInsight',
    'SelfConcept',
    'SpiritualTextCorpus',
    'SelfReflectionSystem',
    'SelfReflection',
    'SelfModel',
    'VoiceSystem',
    'VoiceType',
    'ThoughtPriority',
    'VocalizedThought'
]
