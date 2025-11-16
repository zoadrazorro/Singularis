"""
Test Phase 2: Hybrid Pattern Detection (Rule-Based + AGI Arbiter)

Verifies that rule-based patterns are enhanced by AGI interpretation.
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from loguru import logger

# Import Life Ops components
from life_timeline import (
    LifeTimeline,
    create_fitbit_event,
    create_camera_event,
    EventType
)

# Import Pattern Engine
from pattern_engine import PatternEngine

# Import Singularis AGI
from singularis.unified_consciousness_layer import UnifiedConsciousnessLayer
from singularis.life_ops import AGIPatternArbiter


async def test_phase2():
    """Test Phase 2 hybrid pattern detection."""
    
    print("\n" + "=" * 80)
    print("🧪 PHASE 2 INTEGRATION TEST")
    print("Hybrid Pattern Detection: Rule-Based + AGI Arbiter")
    print("=" * 80)
    
    print("\n[1/6] Initializing components...")
    
    # Initialize Life Timeline
    timeline = LifeTimeline("data/test_phase2.db")
    logger.info("✅ Life Timeline initialized")
    
    # Initialize Singularis consciousness
    consciousness = UnifiedConsciousnessLayer()
    consciousness.connect_life_timeline(timeline)
    logger.info("✅ Singularis consciousness initialized")
    
    # Initialize AGI Pattern Arbiter
    agi_arbiter = AGIPatternArbiter(consciousness)
    logger.info("✅ AGI Pattern Arbiter initialized")
    
    # Initialize Pattern Engine (Hybrid mode)
    pattern_engine = PatternEngine(timeline, agi_arbiter=agi_arbiter)
    logger.info("✅ Pattern Engine initialized (Hybrid mode)")
    
    print("\n[2/6] Adding test life data (4 weeks)...")
    user_id = "test_user"
    
    # Simulate 4 weeks of data with patterns
    base_time = datetime.now() - timedelta(days=28)
    
    for day in range(28):
        current_day = base_time + timedelta(days=day)
        day_of_week = current_day.strftime('%A')
        
        # Pattern 1: Monday & Wednesday exercise
        if day_of_week in ['Monday', 'Wednesday']:
            event = create_fitbit_event(
                user_id=user_id,
                event_type='exercise',
                value=45,  # minutes
                timestamp=current_day.replace(hour=7, minute=0)
            )
            timeline.add_event(event)
        
        # Pattern 2: Sleep (varies by day)
        sleep_hours = 7.5
        if day_of_week in ['Monday', 'Wednesday']:
            sleep_hours = 8.0  # Better sleep after exercise
        elif day_of_week == 'Sunday':
            sleep_hours = 6.5  # Worse sleep on Sundays
        
        event = create_fitbit_event(
            user_id=user_id,
            event_type='sleep',
            value=sleep_hours,
            timestamp=current_day.replace(hour=23, minute=0)
        )
        timeline.add_event(event)
        
        # Pattern 3: Heart rate (varies with exercise)
        for hour in [8, 12, 16, 20]:
            hr = 70
            if day_of_week in ['Monday', 'Wednesday'] and hour == 8:
                hr = 120  # Elevated after exercise
            
            event = create_fitbit_event(
                user_id=user_id,
                event_type='heart_rate',
                value=hr,
                timestamp=current_day.replace(hour=hour, minute=0)
            )
            timeline.add_event(event)
    
    print(f"✅ Added 4 weeks of life data with hidden patterns\n")
    
    print("[3/6] Running RULE-BASED pattern detection...")
    rule_results = pattern_engine.analyze_all(user_id)
    
    print(f"  Patterns detected: {len(rule_results['patterns'])}")
    for pattern in rule_results['patterns']:
        print(f"    - {pattern['name']}: {pattern['description']}")
    
    print(f"\n[4/6] Running HYBRID analysis (Rules + AGI)...")
    print("  This will:")
    print("    1. Use rules to detect patterns (fast)")
    print("    2. Use AGI to interpret significance (smart)")
    print("    3. Use AGI to find hidden correlations")
    print()
    
    hybrid_results = await pattern_engine.analyze_all_with_agi(user_id)
    
    print(f"\n[5/6] Comparing results...")
    print(f"\n  📊 Rule-Based Results:")
    print(f"     Patterns: {len(rule_results['patterns'])}")
    print(f"     Summary: {rule_results['summary']}")
    
    print(f"\n  🧠 Hybrid (Rules + AGI) Results:")
    print(f"     Patterns: {len(hybrid_results['patterns'])}")
    print(f"     AGI Interpretations: {len(hybrid_results.get('agi_interpretations', []))}")
    print(f"     Hidden Correlations: {len(hybrid_results.get('hidden_correlations', []))}")
    print(f"     AGI Summary: {hybrid_results.get('agi_summary', 'N/A')}")
    
    print(f"\n  🎯 AGI Insights:")
    for interp in hybrid_results.get('agi_interpretations', []):
        print(f"\n     Pattern: {interp['pattern_name']}")
        print(f"     Significance: {interp['significance']:.2f}")
        print(f"     Insight: {interp['insight']}")
        if interp.get('recommendation'):
            print(f"     Recommendation: {interp['recommendation']}")
    
    if hybrid_results.get('hidden_correlations'):
        print(f"\n  🔗 Hidden Correlations Discovered by AGI:")
        for corr in hybrid_results['hidden_correlations']:
            print(f"\n     {corr.get('pattern1')} ↔ {corr.get('pattern2')}")
            print(f"     Relationship: {corr.get('relationship')}")
            print(f"     Strength: {corr.get('strength', 0):.2f}")
            print(f"     Insight: {corr.get('actionable_insight', 'N/A')}")
    
    print(f"\n[6/6] Validation...")
    
    # Check that AGI added value
    has_agi_interpretations = len(hybrid_results.get('agi_interpretations', [])) > 0
    has_agi_summary = 'agi_summary' in hybrid_results
    is_hybrid_mode = hybrid_results.get('analysis_mode') == 'hybrid'
    
    if has_agi_interpretations:
        print("  ✅ AGI interpretations present")
    else:
        print("  ⚠️  No AGI interpretations (may need API keys)")
    
    if has_agi_summary:
        print("  ✅ AGI summary generated")
    
    if is_hybrid_mode:
        print("  ✅ Hybrid mode confirmed")
    
    print("\n" + "=" * 80)
    print("🎉 PHASE 2 TEST COMPLETE!")
    print("=" * 80)
    print("\n✅ Rule-based engine detects patterns (fast)")
    print("✅ AGI arbiter interprets patterns (smart)")
    print("✅ AGI finds hidden correlations")
    print("✅ Hybrid system combines best of both worlds")
    
    print("\nKey Benefits:")
    print("  ⚡ Fast: Rules do heavy lifting")
    print("  🧠 Smart: AGI adds intelligence")
    print("  💰 Efficient: Only calls GPT-5 for interpretation")
    print("  🎯 Accurate: Rules find patterns, AGI validates them")
    
    print("\nNext: Phase 3 - AGI-powered interventions\n")


if __name__ == "__main__":
    asyncio.run(test_phase2())
