# -*- coding: utf-8 -*-
"""Test the full system banner display."""

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

# Import and test
import importlib.util
import sys
from pathlib import Path

# Load the module
spec = importlib.util.spec_from_file_location("run_beta_v2_4_cloud", Path(__file__).parent / "run_beta_v2.4_cloud.py")
module = importlib.util.module_from_spec(spec)
sys.modules["run_beta_v2_4_cloud"] = module
spec.loader.exec_module(module)

print_banner = module.print_banner

print_banner()
print("\n✅ Banner test successful!")
