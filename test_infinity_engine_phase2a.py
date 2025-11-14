"""
Test Infinity Engine Phase 2A

Tests the three core Phase 2A innovations:
1. Coherence Engine V2 (Meta-Logic)
2. Meta-Context System
3. HaackLang Operators

This demonstrates how they integrate with existing SCCE + Track architecture.
"""

import sys
import time
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

from singularis.infinity import (
    CoherenceEngineV2,
    CoherenceReport,
    CognitiveAdjustments,
    MetaContextSystem,
    Context,
    ContextLevel,
    ConditionalRule,
)

from singularis.infinity.haacklang_operators import (
    fuzzy_blend,
    paraconsistent_and,
    ParaconsistentValue,
    temporal_derivative,
    TemporalWindow,
    track_interference,
    probability,
    OPERATORS,
)

from singularis.infinity.meta_context import (
    create_survival_context,
    create_creative_context,
    create_learning_context,
    create_threat_evaluation_context,
)


# ========== Mock Cognitive State ==========

class MockTruthValue:
    """Mock TruthValue for testing"""
    def __init__(self, name: str):
        self.name = name
        self.tracks = {
            'main': 0.5,
            'slow': 0.5,
            'fast': 0.5,
        }
    
    def get(self, track: str) -> float:
        return self.tracks.get(track, 0.0)
    
    def set(self, track: str, value: float):
        self.tracks[track] = max(0.0, min(1.0, value))


class MockTrack:
    """Mock Track for testing"""
    def __init__(self, name: str, period: int, phase: float = 0.0):
        self.name = name
        self.period = period
        self.phase = phase


class MockCognitiveState:
    """Mock cognitive state for testing"""
    def __init__(self):
        self.truth_values = {
            'danger': MockTruthValue('danger'),
            'fear': MockTruthValue('fear'),
            'trust': MockTruthValue('trust'),
        }
        
        self.tracks = [
            MockTrack('perception', 100, 0.0),
            MockTrack('intuition', 500, 0.0),
            MockTrack('reflection', 2000, 0.0),
        ]
        
        self.context = 'exploration'
        self.goals = ['explore', 'learn']
        self.emotions = {'fear': 0.3, 'trust': 0.6}
    
    def set_contradiction(self):
        """Create a contradiction for testing"""
        self.truth_values['danger'].set('main', 0.9)
        self.truth_values['danger'].set('slow', 0.1)
    
    def set_high_tension(self):
        """Create high cognitive tension"""
        self.emotions['fear'] = 0.8
        self.emotions['trust'] = 0.7
        self.goals = ['attack', 'flee']  # Conflicting goals


# ========== Test Functions ==========

def test_coherence_engine_v2():
    """Test Coherence Engine V2"""
    print("\n" + "=" * 70)
    print("TEST 1: Coherence Engine V2 (Meta-Logic)")
    print("=" * 70)
    
    engine = CoherenceEngineV2(verbose=True)
    state = MockCognitiveState()
    
    # Test 1: Normal state
    print("\n--- Test 1a: Normal State ---")
    report = engine.evaluate_coherence(state)
    print(f"Contradiction: {report.contradiction_level:.2f}")
    print(f"Tension: {report.cognitive_tension:.2f}")
    print(f"Coherence: {report.coherence_ratio:.2f}")
    print(f"Severity: {report.severity():.2f}")
    
    # Test 2: Contradictory state
    print("\n--- Test 1b: Contradictory State ---")
    state.set_contradiction()
    report = engine.evaluate_coherence(state)
    print(f"Contradiction: {report.contradiction_level:.2f}")
    print(f"Contradictions found: {len(report.contradictions)}")
    
    if report.contradictions:
        c = report.contradictions[0]
        print(f"  Example: {c['truthvalue']}.{c['track1']}={c['val1']:.2f} vs {c['track2']}={c['val2']:.2f}")
    
    # Test 3: Apply corrections
    print("\n--- Test 1c: Apply Corrections ---")
    adjustments = engine.apply_corrections(report)
    print(f"Adjustments generated: {len(adjustments.adjustments)}")
    for adj in adjustments.adjustments[:3]:
        print(f"  - {adj.intervention_type.value}: {adj.target}")
        print(f"    Reason: {adj.reason}")
    
    # Test 4: High tension
    print("\n--- Test 1d: High Tension State ---")
    state = MockCognitiveState()
    state.set_high_tension()
    report = engine.evaluate_coherence(state)
    print(f"Tension: {report.cognitive_tension:.2f}")
    print(f"Tension sources: {report.tension_sources}")
    
    adjustments = engine.apply_corrections(report)
    print(f"Adjustments: {len(adjustments.adjustments)}")
    
    # Statistics
    print("\n--- Statistics ---")
    stats = engine.get_statistics()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    print("\n[PASS] Coherence Engine V2 tests passed")


def test_meta_context_system():
    """Test Meta-Context System"""
    print("\n" + "=" * 70)
    print("TEST 2: Meta-Context System")
    print("=" * 70)
    
    meta_context = MetaContextSystem(verbose=True)
    state = MockCognitiveState()
    
    # Test 1: Push macro context
    print("\n--- Test 2a: Push Macro Context ---")
    exploration = Context('exploration', ContextLevel.MACRO)
    exploration.track_amplifications = {'perception': 1.3, 'curiosity': 1.4}
    meta_context.push_context(exploration)
    
    # Test 2: Push micro context with timer
    print("\n--- Test 2b: Timed Micro Context ---")
    threat_eval = create_threat_evaluation_context(duration=2.0)
    meta_context.push_context(threat_eval)
    
    print(f"Stack depth: {meta_context.context_stack.depth()}")
    print(f"Active context: {meta_context.get_active_context()}")
    
    # Test 3: Wait for expiration
    print("\n--- Test 2c: Context Expiration ---")
    print("Waiting 2.5 seconds for context to expire...")
    time.sleep(2.5)
    
    meta_context.update_contexts(state)
    print(f"Stack depth after expiration: {meta_context.context_stack.depth()}")
    print(f"Active context: {meta_context.get_active_context()}")
    
    # Test 4: Conditional rules
    print("\n--- Test 2d: Conditional Context Rules ---")
    
    # Rule: Enter survival mode when danger > 0.7
    def high_danger(state):
        return state.truth_values['danger'].get('main') > 0.7
    
    survival = create_survival_context()
    rule = ConditionalRule(
        condition=high_danger,
        action='enter',
        target_context=survival,
        priority=10,
        cooldown=1.0
    )
    
    meta_context.add_rule(rule)
    
    # Trigger rule
    state.truth_values['danger'].set('main', 0.9)
    print("Danger set to 0.9, updating contexts...")
    meta_context.update_contexts(state)
    
    print(f"Active context: {meta_context.get_active_context()}")
    
    # Test 5: Predefined contexts
    print("\n--- Test 2e: Predefined Context Templates ---")
    creative = create_creative_context()
    learning = create_learning_context()
    
    print(f"Creative context amplifications: {creative.track_amplifications}")
    print(f"Learning context plasticity: {learning.plasticity_factor}")
    
    # Statistics
    print("\n--- Statistics ---")
    stats = meta_context.get_statistics()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    print("\n[PASS] Meta-Context System tests passed")


def test_haacklang_operators():
    """Test HaackLang Operators"""
    print("\n" + "=" * 70)
    print("TEST 3: HaackLang 2.0 Operators")
    print("=" * 70)
    
    # Test 1: Fuzzy blend
    print("\n--- Test 3a: Fuzzy Blend ---")
    main = 0.8
    perception = 0.6
    blended = fuzzy_blend(main, perception, 0.3)
    print(f"main={main} blend(0.3) perception={perception}")
    print(f"Result: {blended:.2f}")
    print(f"Expected: ~{0.8 * 0.7 + 0.6 * 0.3:.2f}")
    
    # Test 2: Paraconsistent logic
    print("\n--- Test 3b: Paraconsistent And ---")
    evidence_for = ParaconsistentValue(belief=0.8, disbelief=0.2)
    evidence_against = ParaconsistentValue(belief=0.3, disbelief=0.7)
    combined = paraconsistent_and(evidence_for, evidence_against)
    
    print(f"Evidence FOR: belief={evidence_for.belief}, disbelief={evidence_for.disbelief}")
    print(f"Evidence AGAINST: belief={evidence_against.belief}, disbelief={evidence_against.disbelief}")
    print(f"Combined: belief={combined.belief}, disbelief={combined.disbelief}")
    print(f"Contradictory: {combined.is_contradictory()}")
    print(f"Certainty: {combined.certainty():.2f}")
    
    # Test 3: Temporal derivative
    print("\n--- Test 3c: Temporal Derivative ---")
    window = TemporalWindow(size=5)
    values = [0.2, 0.3, 0.5, 0.6, 0.7]
    for i, val in enumerate(values):
        window.add(val, float(i))
    
    derivative = temporal_derivative(window)
    print(f"Values: {values}")
    print(f"Delta (rate of change): {derivative:.3f}")
    print(f"Trend: {'increasing' if derivative > 0 else 'decreasing'}")
    
    # Test 4: Track interference
    print("\n--- Test 3d: Track Interference ---")
    track1 = MockTrack('fast', 100, 0.0)
    track2 = MockTrack('slow', 500, 0.0)
    
    interference = track_interference(track1, track2)
    print(f"Track 1: phase={track1.phase:.2f}")
    print(f"Track 2: phase={track2.phase:.2f}")
    print(f"Interference: {interference:.2f}")
    print(f"Type: {'constructive' if interference > 0 else 'destructive'}")
    
    # Test 5: Probability
    print("\n--- Test 3e: Probability (P) ---")
    evidence = 0.8
    prior = 0.3
    posterior = probability(evidence, prior)
    print(f"P(threat | evidence={evidence}) with prior={prior}")
    print(f"Posterior: {posterior:.2f}")
    
    # Test 6: Operator registry
    print("\n--- Test 3f: Operator Registry ---")
    print(f"Total operators: {len(OPERATORS.list_operators())}")
    
    # Test getting operators (using unicode-safe approach)
    blend_op = OPERATORS.get('blend')
    print(f"Operator 'blend': {blend_op.__name__ if blend_op else 'Not found'}")
    
    # Test direct symbol access
    direct_op = OPERATORS.operators.get('⊕')
    print(f"Direct symbol access: {direct_op.__name__ if direct_op else 'Not found'}")
    
    print("\n[PASS] HaackLang Operators tests passed")


def test_integration():
    """Test integration of all three systems"""
    print("\n" + "=" * 70)
    print("TEST 4: Integrated System")
    print("=" * 70)
    
    # Initialize all systems
    coherence_engine = CoherenceEngineV2(verbose=False)
    meta_context = MetaContextSystem(verbose=False)
    state = MockCognitiveState()
    
    print("\n--- Scenario: Danger Detection -> Context Shift -> Coherence Restoration ---")
    
    # Step 1: Start in exploration
    print("\n1. Initial state: Exploration")
    exploration = Context('exploration', ContextLevel.MACRO)
    meta_context.push_context(exploration)
    print(f"   Context: {meta_context.get_active_context().name}")
    
    # Step 2: Detect danger
    print("\n2. Danger detected!")
    state.truth_values['danger'].set('main', 0.9)
    state.truth_values['danger'].set('slow', 0.2)  # Contradiction
    
    # Step 3: Evaluate coherence
    print("\n3. Evaluate coherence")
    report = coherence_engine.evaluate_coherence(state)
    print(f"   Contradiction: {report.contradiction_level:.2f}")
    print(f"   Severity: {report.severity():.2f}")
    
    # Step 4: Apply corrections
    print("\n4. Apply meta-logic corrections")
    adjustments = coherence_engine.apply_corrections(report)
    print(f"   Adjustments: {len(adjustments.adjustments)}")
    for adj in adjustments.adjustments[:2]:
        print(f"   - {adj.intervention_type.value}: {adj.target}")
    
    # Step 5: Context shift to survival
    print("\n5. Shift to survival context")
    survival = create_survival_context()
    meta_context.push_context(survival)
    print(f"   Context: {meta_context.get_active_context().name}")
    print(f"   Amplifications: {survival.track_amplifications}")
    print(f"   Suppressions: {survival.track_suppressions}")
    
    # Step 6: Use operators to blend tracks
    print("\n6. Blend perception into main track")
    main_danger = state.truth_values['danger'].get('main')
    perception_danger = 0.85
    blended = fuzzy_blend(main_danger, perception_danger, 0.4)
    state.truth_values['danger'].set('main', blended)
    print(f"   main={main_danger:.2f} blend(0.4) perception={perception_danger:.2f} = {blended:.2f}")
    
    # Step 7: Re-evaluate
    print("\n7. Re-evaluate coherence")
    report2 = coherence_engine.evaluate_coherence(state)
    print(f"   Contradiction: {report2.contradiction_level:.2f}")
    print(f"   Severity: {report2.severity():.2f}")
    print(f"   Improvement: {report.severity() - report2.severity():.2f}")
    
    print("\n[PASS] Integration test passed")
    
    # Final statistics
    print("\n" + "=" * 70)
    print("FINAL STATISTICS")
    print("=" * 70)
    
    print("\nCoherence Engine:")
    for key, value in coherence_engine.get_statistics().items():
        print(f"  {key}: {value}")
    
    print("\nMeta-Context System:")
    for key, value in meta_context.get_statistics().items():
        print(f"  {key}: {value}")


# ========== Main ==========

def main():
    """Run all tests"""
    print("\n" + "=" * 70)
    print("SINGULARIS INFINITY ENGINE - PHASE 2A TESTS")
    print("=" * 70)
    print("\nTesting three core innovations:")
    print("1. Coherence Engine V2 (Meta-Logic)")
    print("2. Meta-Context System (Hierarchical Temporal Contexts)")
    print("3. HaackLang 2.0 Operators (Full Cognitive DSL)")
    
    try:
        test_coherence_engine_v2()
        test_meta_context_system()
        test_haacklang_operators()
        test_integration()
        
        print("\n" + "=" * 70)
        print("[SUCCESS] ALL TESTS PASSED")
        print("=" * 70)
        print("\nPhase 2A foundation is ready!")
        print("\nNext steps:")
        print("  - Integrate with existing SCCE calculus")
        print("  - Connect to HaackLang parser/interpreter")
        print("  - Add to Singularis main loop")
        print("  - Build Phase 2B (Polyrhythmic Learning, Memory Engine v2)")
        
    except Exception as e:
        print(f"\n[FAIL] TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
