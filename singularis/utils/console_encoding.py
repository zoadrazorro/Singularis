# -*- coding: utf-8 -*-
"""
Console Encoding Utility for Windows UTF-8 Support

This module provides utilities to fix console encoding issues on Windows,
enabling proper display of unicode characters, emojis, and special symbols.

Usage:
    from singularis.utils.console_encoding import ensure_utf8_console
    
    # At the start of your script
    ensure_utf8_console()
"""

import sys
import io


def ensure_utf8_console():
    """
    Ensure console uses UTF-8 encoding on Windows.
    
    This fixes UnicodeEncodeError when printing unicode characters, emojis,
    or special symbols on Windows where the default console encoding is
    often cp1252 instead of UTF-8.
    
    This function:
    - Wraps sys.stdout and sys.stderr with UTF-8 TextIOWrapper on Windows
    - Uses 'replace' error handling to avoid crashes on unprintable characters
    - Is safe to call multiple times (idempotent)
    - Does nothing on non-Windows platforms
    
    Returns:
        bool: True if encoding was changed, False otherwise
    """
    if sys.platform != 'win32':
        return False
    
    try:
        # Check if already wrapped with UTF-8
        if hasattr(sys.stdout, 'encoding') and sys.stdout.encoding.lower() == 'utf-8':
            return False
        
        # Wrap stdout and stderr with UTF-8 encoding
        sys.stdout = io.TextIOWrapper(
            sys.stdout.buffer,
            encoding='utf-8',
            errors='replace',
            line_buffering=True
        )
        sys.stderr = io.TextIOWrapper(
            sys.stderr.buffer,
            encoding='utf-8',
            errors='replace',
            line_buffering=True
        )
        return True
    except (AttributeError, io.UnsupportedOperation):
        # stdout/stderr doesn't have .buffer (e.g., in some IDEs)
        # or operation not supported
        return False


def print_utf8(*args, **kwargs):
    """
    Print with UTF-8 encoding, falling back to ASCII if needed.
    
    This is a safer alternative to print() that handles encoding errors
    gracefully by replacing unprintable characters.
    
    Args:
        *args: Arguments to print
        **kwargs: Keyword arguments to pass to print()
    """
    try:
        print(*args, **kwargs)
    except UnicodeEncodeError:
        # Fallback: encode as UTF-8 and decode with errors='replace'
        try:
            message = ' '.join(str(arg) for arg in args)
            print(message.encode('utf-8', errors='replace').decode('utf-8'), **kwargs)
        except Exception:
            # Last resort: print without unicode
            print('[Unicode encoding error - message suppressed]', **kwargs)


def safe_format_unicode(text: str, fallback: str = '[?]') -> str:
    """
    Safely format unicode text for console output.
    
    Args:
        text: Text containing unicode characters
        fallback: Replacement string for characters that can't be encoded
        
    Returns:
        str: Formatted text safe for console output
    """
    if sys.platform != 'win32':
        return text
    
    try:
        # Try to encode/decode to verify it's safe
        text.encode(sys.stdout.encoding or 'utf-8')
        return text
    except (UnicodeEncodeError, AttributeError):
        # Replace unprintable characters
        return text.encode('utf-8', errors='replace').decode('utf-8')


# Emoji replacements for environments that don't support emoji
ASCII_EMOJI_MAP = {
    '✓': '[OK]',
    '✅': '[OK]',
    '✗': '[X]',
    '❌': '[X]',
    '⚠️': '[!]',
    '🚀': '[>>]',
    '🔄': '[~]',
    '⏳': '[...]',
    '🎮': '[*]',
    '🔴': '[HIGH]',
    '🟡': '[MED]',
    '🟢': '[LOW]',
    '🧠': '[BRAIN]',
    '→': '->',
    '║': '|',
    '═': '=',
    '╔': '+',
    '╚': '+',
    '╗': '+',
    '╝': '+',
}


def replace_emojis_with_ascii(text: str) -> str:
    """
    Replace emojis and special unicode with ASCII equivalents.
    
    Useful for environments that don't support unicode at all.
    
    Args:
        text: Text containing emojis and special characters
        
    Returns:
        str: Text with ASCII replacements
    """
    for emoji, ascii_equiv in ASCII_EMOJI_MAP.items():
        text = text.replace(emoji, ascii_equiv)
    return text


# Auto-configure on import if environment variable is set
if __name__ != '__main__':
    import os
    if os.getenv('SINGULARIS_AUTO_UTF8', '').lower() in ('1', 'true', 'yes'):
        ensure_utf8_console()
