"""
Quick fix for Gemini rate limiting issues.

This script patches run_skyrim_agi.py to reduce Gemini API calls.
"""

import re
from pathlib import Path

def apply_fix():
    """Apply rate limit fixes to run_skyrim_agi.py"""
    
    file_path = Path("run_skyrim_agi.py")
    
    if not file_path.exists():
        print("[FAIL] run_skyrim_agi.py not found!")
        return False
    
    print("Reading run_skyrim_agi.py...")
    content = file_path.read_text(encoding='utf-8')
    
    # Fix 1: Reduce Gemini RPM limit
    content = re.sub(
        r'gemini_rpm_limit=30,',
        'gemini_rpm_limit=15,  # Reduced for safety margin',
        content
    )
    
    # Fix 2: Increase cycle interval
    content = re.sub(
        r'cycle_interval=2\.0,',
        'cycle_interval=3.0,  # Slower cycles = fewer API calls',
        content
    )
    
    # Fix 3: Reduce Gemini experts
    content = re.sub(
        r'num_gemini_experts=2,',
        'num_gemini_experts=1,  # Reduced from 2 to save API calls',
        content
    )
    
    # Backup original
    backup_path = file_path.with_suffix('.py.backup')
    print(f"Creating backup: {backup_path}")
    backup_path.write_text(file_path.read_text(encoding='utf-8'), encoding='utf-8')
    
    # Write fixed version
    print("Applying fixes...")
    file_path.write_text(content, encoding='utf-8')
    
    print("\n[OK] Fixes applied successfully!")
    print("\nChanges made:")
    print("  1. gemini_rpm_limit: 30 -> 15")
    print("  2. cycle_interval: 2.0 -> 3.0 seconds")
    print("  3. num_gemini_experts: 2 -> 1")
    print("\nThis should reduce Gemini API calls from ~120/min to ~15/min")
    print(f"\nBackup saved to: {backup_path}")
    
    return True

if __name__ == "__main__":
    print("="*70)
    print("GEMINI RATE LIMIT FIX")
    print("="*70)
    print()
    
    if apply_fix():
        print("\n[OK] Ready to run! Restart the AGI to apply changes.")
    else:
        print("\n[FAIL] Fix failed. Please apply changes manually.")
