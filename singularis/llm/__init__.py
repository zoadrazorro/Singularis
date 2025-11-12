"""LLM integration module for Singularis."""

from .lmstudio_client import (
    LMStudioClient,
    LMStudioConfig,
    ExpertLLMInterface,
)
from .claude_client import ClaudeClient
from .gemini_client import GeminiClient

__all__ = [
    "LMStudioClient",
    "LMStudioConfig",
    "ExpertLLMInterface",
    "ClaudeClient",
    "GeminiClient",
]
