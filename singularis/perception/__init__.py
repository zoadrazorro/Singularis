"""
Perception systems for the AGI.

Includes streaming video interpretation with real-time audio commentary.
"""

from .streaming_video_interpreter import (
    StreamingVideoInterpreter,
    InterpretationMode,
    VideoFrame,
    StreamingInterpretation
)

__all__ = [
    'StreamingVideoInterpreter',
    'InterpretationMode',
    'VideoFrame',
    'StreamingInterpretation',
]
