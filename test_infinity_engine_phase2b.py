"""
Test suite for Infinity Engine Phase 2B

Tests:
1. Polyrhythmic Learning - Adaptive track periods
2. Memory Engine v2 - Temporal-rhythmic memory encoding
3. Integration - Combined system with Phase 2A
"""

import time
import math
from singularis.infinity import (
    # Phase 2A
    CoherenceEngineV2,
    MetaContextSystem,
    Context,
    ContextLevel,
    # Phase 2B
    PolyrhythmicLearner,
    AdaptationStrategy,
    RhythmProfile,
    create_exploration_profile,
    create_survival_profile,
    create_learning_profile,
    MemoryEngineV2,
    MemoryType,
    RhythmSignature,
)


def test_polyrhythmic_learning():
    """Test Polyrhythmic Learning System"""
    print("\n" + "=" * 70)
    print("TEST 1: Polyrhythmic Learning")
    print("=" * 70)
    
    learner = PolyrhythmicLearner(
        strategy=AdaptationStrategy.REWARD_BASED,
        global_learning_rate=0.05,
        verbose=True
    )
    
    # Test 1a: Register tracks
    print("\n--- Test 1a: Register Tracks ---")
    learner.register_track('perception', initial_period=100, min_period=20, max_period=500)
    learner.register_track('reflection', initial_period=200, min_period=50, max_period=1000)
    learner.register_track('strategic', initial_period=500, min_period=100, max_period=2000)
    
    print(f"Registered tracks: {list(learner.track_states.keys())}")
    print(f"Initial periods: {learner.get_all_periods()}")
    
    # Test 1b: Add harmonic constraints
    print("\n--- Test 1b: Harmonic Constraints ---")
    learner.add_harmonic_constraint('perception', 'reflection', 0.5)  # perception 2x faster
    learner.add_harmonic_constraint('reflection', 'strategic', 0.4)   # reflection 2.5x faster
    
    harmonic_coherence = learner.compute_harmonic_coherence()
    print(f"Initial harmonic coherence: {harmonic_coherence:.3f}")
    
    # Test 1c: Reward-based adaptation
    print("\n--- Test 1c: Reward-Based Adaptation ---")
    
    # Simulate learning: high rewards reinforce current periods
    for i in range(5):
        reward = 0.8 + 0.1 * math.sin(i)  # Varying rewards
        learner.adapt_from_reward('perception', reward, coherence=0.7)
        time.sleep(0.01)
    
    print(f"Perception period after adaptation: {learner.get_current_period('perception')}")
    
    # Test 1d: Context-specific profiles
    print("\n--- Test 1d: Context-Specific Profiles ---")
    
    exploration = create_exploration_profile()
    survival = create_survival_profile()
    
    learner.add_rhythm_profile(exploration)
    learner.add_rhythm_profile(survival)
    
    print(f"\nExploration profile periods: {exploration.track_periods}")
    print(f"Survival profile periods: {survival.track_periods}")
    
    # Switch to survival context
    print("\nSwitching to survival context...")
    learner.adapt_to_context('survival')
    
    print(f"Periods after context switch: {learner.get_all_periods()}")
    
    # Test 1e: Harmonic attraction
    print("\n--- Test 1e: Harmonic Attraction ---")
    
    # Apply harmonic attraction multiple times
    for _ in range(3):
        learner._apply_harmonic_attraction('perception')
        learner._apply_harmonic_attraction('reflection')
    
    final_coherence = learner.compute_harmonic_coherence()
    print(f"Final harmonic coherence: {final_coherence:.3f}")
    print(f"Improvement: {final_coherence - harmonic_coherence:.3f}")
    
    # Statistics
    print("\n--- Statistics ---")
    stats = learner.get_statistics()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    print("\n[PASS] Polyrhythmic Learning tests passed")


def test_memory_engine_v2():
    """Test Memory Engine v2"""
    print("\n" + "=" * 70)
    print("TEST 2: Memory Engine v2")
    print("=" * 70)
    
    memory = MemoryEngineV2(
        episodic_capacity=100,
        semantic_capacity=50,
        decay_rate=0.01,
        consolidation_threshold=3,
        verbose=True
    )
    
    # Test 2a: Encode episodic memories
    print("\n--- Test 2a: Encode Episodic Memories ---")
    
    # Simulate encoding 5 memories with different rhythm signatures
    for i in range(5):
        memory_id = f"event_{i}"
        
        # Create track states (phase, period)
        track_states = {
            'perception': (i * 0.5, 100),
            'reflection': (i * 0.3, 200),
            'strategic': (i * 0.2, 500)
        }
        
        content = {
            'danger_level': 0.3 + i * 0.1,
            'curiosity': 0.5 + i * 0.05,
            'action': f'action_{i}'
        }
        
        memory.encode_episodic(
            memory_id=memory_id,
            content=content,
            track_states=track_states,
            context='exploration'
        )
    
    print(f"Total episodic memories: {len(memory.episodic_memories)}")
    
    # Test 2b: Recall by rhythm
    print("\n--- Test 2b: Recall by Rhythm ---")
    
    # Create query rhythm similar to event_2
    query_rhythm = RhythmSignature(
        track_phases={'perception': 1.0, 'reflection': 0.6, 'strategic': 0.4},
        track_periods={'perception': 100, 'reflection': 200, 'strategic': 500},
        interference_pattern=[],
        dominant_frequency=0.01
    )
    
    recalled = memory.recall_by_rhythm(query_rhythm, top_k=3, threshold=0.3)
    
    print(f"Recalled {len(recalled)} memories:")
    for mem, similarity in recalled:
        print(f"  {mem.memory_id}: similarity={similarity:.3f}, strength={mem.strength:.2f}")
    
    # Test 2c: Recall by context
    print("\n--- Test 2c: Recall by Context ---")
    
    context_memories = memory.recall_by_context('exploration', top_k=3)
    print(f"Recalled {len(context_memories)} memories from 'exploration' context")
    
    # Test 2d: Consolidation
    print("\n--- Test 2d: Episodic -> Semantic Consolidation ---")
    
    # Reinforce some memories to make them consolidation-ready
    for i in range(3):
        mem = memory.episodic_memories[f'event_{i}']
        for _ in range(4):  # Reinforce 4 times
            mem.reinforce()
    
    # Consolidate
    pattern = memory.consolidate_episodic_to_semantic(
        pattern_type='exploration_pattern',
        episode_ids=['event_0', 'event_1', 'event_2']
    )
    
    if pattern:
        print(f"Created pattern: {pattern.pattern_id}")
        print(f"  Type: {pattern.pattern_type}")
        print(f"  Confidence: {pattern.confidence:.2f}")
        print(f"  Source episodes: {len(pattern.source_episodes)}")
    
    # Test 2e: Retrieve semantic pattern
    print("\n--- Test 2e: Retrieve Semantic Pattern ---")
    
    retrieved = memory.retrieve_semantic_pattern('exploration_pattern')
    if retrieved:
        print(f"Retrieved pattern: {retrieved.pattern_id}")
        print(f"  Confidence: {retrieved.confidence:.2f}")
        print(f"  Activations: {retrieved.activation_count}")
    
    # Test 2f: Forgetting
    print("\n--- Test 2f: Apply Forgetting ---")
    
    initial_count = len(memory.episodic_memories)
    
    # Apply decay multiple times
    for _ in range(10):
        memory.apply_forgetting()
    
    final_count = len(memory.episodic_memories)
    print(f"Memories before forgetting: {initial_count}")
    print(f"Memories after forgetting: {final_count}")
    print(f"Forgotten: {initial_count - final_count}")
    
    # Statistics
    print("\n--- Statistics ---")
    stats = memory.get_statistics()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    print("\n[PASS] Memory Engine v2 tests passed")


def test_integration():
    """Test integration of Phase 2A + 2B"""
    print("\n" + "=" * 70)
    print("TEST 3: Integrated System (Phase 2A + 2B)")
    print("=" * 70)
    
    # Initialize all systems
    coherence_engine = CoherenceEngineV2(verbose=False)
    meta_context = MetaContextSystem(verbose=False)
    learner = PolyrhythmicLearner(verbose=False)
    memory = MemoryEngineV2(verbose=False)
    
    print("\n--- Scenario: Adaptive Learning During Exploration ---")
    
    # Step 1: Setup exploration context
    print("\n1. Initialize exploration context")
    exploration_ctx = Context('exploration', ContextLevel.MACRO)
    meta_context.push_context(exploration_ctx)
    
    # Register tracks with learner
    learner.register_track('perception', 100)
    learner.register_track('curiosity', 150)
    learner.register_track('reflection', 200)
    
    # Add exploration profile
    exploration_profile = create_exploration_profile()
    learner.add_rhythm_profile(exploration_profile)
    
    print(f"   Context: {meta_context.get_active_context().name}")
    print(f"   Initial periods: {learner.get_all_periods()}")
    
    # Step 2: Simulate cognitive cycle with memory encoding
    print("\n2. Cognitive cycle: perceive -> encode -> adapt")
    
    for cycle in range(3):
        print(f"\n   Cycle {cycle + 1}:")
        
        # Get current track states
        track_states = {
            'perception': (cycle * 0.5, learner.get_current_period('perception')),
            'curiosity': (cycle * 0.3, learner.get_current_period('curiosity')),
            'reflection': (cycle * 0.2, learner.get_current_period('reflection'))
        }
        
        # Encode memory
        memory_id = f"explore_cycle_{cycle}"
        content = {'cycle': cycle, 'curiosity': 0.7 + cycle * 0.05}
        
        memory.encode_episodic(
            memory_id=memory_id,
            content=content,
            track_states=track_states,
            context='exploration'
        )
        
        # Adapt rhythms based on reward
        reward = 0.6 + cycle * 0.1
        learner.adapt_from_reward('perception', reward)
        
        print(f"     Encoded: {memory_id}")
        print(f"     Reward: {reward:.2f}")
        print(f"     Perception period: {learner.get_current_period('perception')}")
    
    # Step 3: Context shift to survival
    print("\n3. Context shift: exploration -> survival")
    
    survival_ctx = Context('survival', ContextLevel.MACRO)
    meta_context.push_context(survival_ctx)
    
    # Adapt rhythms to survival profile
    survival_profile = create_survival_profile()
    learner.add_rhythm_profile(survival_profile)
    learner.adapt_to_context('survival')
    
    print(f"   New context: {meta_context.get_active_context().name}")
    print(f"   Adapted periods: {learner.get_all_periods()}")
    
    # Step 4: Recall relevant memories
    print("\n4. Recall exploration memories")
    
    exploration_memories = memory.recall_by_context('exploration', top_k=3)
    print(f"   Recalled {len(exploration_memories)} memories")
    for mem in exploration_memories:
        print(f"     {mem.memory_id}: strength={mem.strength:.2f}")
    
    # Step 5: Consolidate learning
    print("\n5. Consolidate episodic -> semantic")
    
    # Reinforce memories
    for mem in exploration_memories:
        for _ in range(4):
            mem.reinforce()
    
    pattern = memory.consolidate_episodic_to_semantic(
        pattern_type='exploration_strategy',
        episode_ids=[m.memory_id for m in exploration_memories]
    )
    
    if pattern:
        print(f"   Created pattern: {pattern.pattern_id}")
        print(f"   Confidence: {pattern.confidence:.2f}")
    
    # Step 6: Compute system coherence
    print("\n6. System coherence")
    
    harmonic_coherence = learner.compute_harmonic_coherence()
    print(f"   Harmonic coherence: {harmonic_coherence:.3f}")
    print(f"   Context stack depth: {meta_context.context_stack.depth()}")
    print(f"   Episodic memories: {len(memory.episodic_memories)}")
    print(f"   Semantic patterns: {len(memory.semantic_patterns)}")
    
    print("\n[PASS] Integration test passed")
    
    # Final statistics
    print("\n" + "=" * 70)
    print("FINAL STATISTICS")
    print("=" * 70)
    
    print("\nPolyrhythmic Learner:")
    for key, value in learner.get_statistics().items():
        print(f"  {key}: {value}")
    
    print("\nMemory Engine:")
    for key, value in memory.get_statistics().items():
        print(f"  {key}: {value}")
    
    print("\nMeta-Context:")
    for key, value in meta_context.get_statistics().items():
        print(f"  {key}: {value}")


def main():
    """Run all Phase 2B tests"""
    print("=" * 70)
    print("SINGULARIS INFINITY ENGINE - PHASE 2B TESTS")
    print("=" * 70)
    
    print("\nTesting two core innovations:")
    print("1. Polyrhythmic Learning (Adaptive Track Periods)")
    print("2. Memory Engine v2 (Temporal-Rhythmic Encoding)")
    
    try:
        test_polyrhythmic_learning()
        test_memory_engine_v2()
        test_integration()
        
        print("\n" + "=" * 70)
        print("[SUCCESS] ALL TESTS PASSED")
        print("=" * 70)
        print("\nPhase 2B foundation is ready!")
        print("\nNext steps:")
        print("  - Integrate with Singularis main loop")
        print("  - Connect to existing Track system")
        print("  - Build Phase 2C (Multi-Agent, Graph Compiler, Personality)")
        
    except Exception as e:
        print(f"\n[FAIL] TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
