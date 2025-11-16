"""
Perception systems for the AGI.

Includes streaming video interpretation with real-time audio commentary
and IWM world model integration.
"""

from .streaming_video_interpreter import (
    StreamingVideoInterpreter,
    InterpretationMode,
    VideoFrame,
    StreamingInterpretation
)

from .iwm_perception_integration import IWMPerceptionModule

__all__ = [
    'StreamingVideoInterpreter',
    'InterpretationMode',
    'VideoFrame',
    'StreamingInterpretation',
    'IWMPerceptionModule',
]
