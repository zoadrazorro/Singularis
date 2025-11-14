# -*- coding: utf-8 -*-
"""
Singularis Utilities

Common utilities for the Singularis AGI system.
"""

from .console_encoding import (
    ensure_utf8_console,
    print_utf8,
    safe_format_unicode,
    replace_emojis_with_ascii,
)

__all__ = [
    'ensure_utf8_console',
    'print_utf8',
    'safe_format_unicode',
    'replace_emojis_with_ascii',
]
