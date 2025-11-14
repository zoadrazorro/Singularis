# -*- coding: utf-8 -*-
"""
Quick test to verify unicode encoding fix works on Windows.
"""

import sys
import io

# Fix Windows console encoding
if sys.platform == 'win32':
    try:
        if not isinstance(sys.stdout, io.TextIOWrapper) or sys.stdout.encoding != 'utf-8':
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)
        if not isinstance(sys.stderr, io.TextIOWrapper) or sys.stderr.encoding != 'utf-8':
            sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace', line_buffering=True)
    except (AttributeError, io.UnsupportedOperation):
        pass

# Test unicode characters
print("=" * 70)
print("Unicode Encoding Test")
print("=" * 70)
print()

# Test emojis
print("Emojis:")
print("  🎮 Game controller")
print("  🔴 High priority")
print("  🟡 Medium priority")
print("  🟢 Low priority")
print("  🧠 Brain/thinking")
print("  ⚠️ Warning")
print("  ✅ Success/checkmark")
print("  ❌ Failure/X mark")
print("  🚀 Launch/rocket")
print()

# Test special symbols
print("Special Symbols:")
print("  ✓ Check mark")
print("  ✗ X mark")
print("  → Arrow")
print()

# Test mathematical symbols
print("Mathematical Symbols:")
print("  Δ𝒞 = +0.123 (coherence delta)")
print("  ℓₒ = 0.850 (ontical)")
print("  ℓₛ = 0.720 (structural)")
print("  ℓₚ = 0.900 (participatory)")
print()

# Test box drawing
print("Box Drawing:")
print("  ╔════════════════════╗")
print("  ║  Test Box          ║")
print("  ╚════════════════════╝")
print()

print("=" * 70)
print("✅ All unicode characters displayed successfully!")
print("=" * 70)
