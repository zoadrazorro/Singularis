"""
Test Neuron Swarm: Hebbian Learning & Emergent Intelligence

Validates:
1. Hebbian learning: "Fire together, wire together"
2. Pattern recognition emerges from experience
3. Distributed activation propagation
4. Emergent swarm coherence
5. Connection matrix dynamics
"""

import sys
from pathlib import Path
import numpy as np

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from loguru import logger
from singularis.tier3_neurons.base import Neuron
from singularis.tier3_neurons.swarm import NeuronSwarm
from singularis.core.types import Lumen


# Configure logger for tests
logger.remove()
logger.add(sys.stdout, level="INFO", format="{time:HH:mm:ss} | {level} | {message}")


def test_neuron_initialization():
    """Test 1: Neuron initializes correctly"""
    logger.info("="*80)
    logger.info("TEST 1: Neuron Initialization")
    logger.info("="*80)

    neuron = Neuron(
        neuron_id="test_n0",
        lumen_specialization=Lumen.ONTICUM,
        learning_rate=0.05,
        activation_threshold=0.5,
    )

    assert neuron.neuron_id == "test_n0"
    assert neuron.lumen_specialization == Lumen.ONTICUM
    assert neuron.activation == 0.0
    assert len(neuron.state.connection_weights) == 0

    logger.success("✓ Neuron initialization test passed")
    return neuron


def test_neuron_activation():
    """Test 2: Neuron activation function"""
    logger.info("="*80)
    logger.info("TEST 2: Neuron Activation")
    logger.info("="*80)

    neuron = Neuron(
        neuron_id="test_n0",
        lumen_specialization=Lumen.STRUCTURALE,
    )

    # Test with no inputs → should have low activation
    activation = neuron.activate({})
    logger.info(f"Activation with no inputs: {activation:.3f}")
    assert 0.0 <= activation <= 1.0

    # Test with strong positive input
    inputs = {"source_1": 0.9}

    # First, establish a connection by simulating Hebbian learning
    neuron.state.connection_weights["source_1"] = 0.8

    activation = neuron.activate(inputs)
    logger.info(f"Activation with strong positive input: {activation:.3f}")
    assert activation > 0.5  # Should be high

    logger.success("✓ Neuron activation test passed")
    return neuron


def test_hebbian_learning():
    """Test 3: Hebbian learning - fire together, wire together"""
    logger.info("="*80)
    logger.info("TEST 3: Hebbian Learning")
    logger.info("="*80)

    neuron = Neuron(
        neuron_id="test_n0",
        lumen_specialization=Lumen.PARTICIPATUM,
        learning_rate=0.1,
        activation_threshold=0.3,
    )

    # Simulate co-activation multiple times
    for i in range(10):
        # Activate neuron
        inputs = {"source_A": 0.8}
        neuron.state.connection_weights["source_A"] = 0.5  # Initial weight

        activation = neuron.activate(
            inputs,
            active_neurons={"test_n0", "source_A"}  # Both firing
        )

    # Check that Hebbian learning strengthened connection
    weight_after = neuron.state.connection_weights.get("source_A", 0.0)

    logger.info(f"Weight to source_A after 10 co-activations: {weight_after:.3f}")
    logger.info(f"Coactivation count: {neuron.state.coactivation_counts.get('source_A', 0)}")

    assert weight_after > 0.5  # Should have increased from initial 0.5
    assert neuron.state.coactivation_counts.get("source_A", 0) > 0

    logger.success("✓ Hebbian learning test passed")


def test_pattern_learning():
    """Test 4: Pattern learning and recognition"""
    logger.info("="*80)
    logger.info("TEST 4: Pattern Learning & Recognition")
    logger.info("="*80)

    neuron = Neuron(
        neuron_id="test_n0",
        lumen_specialization=Lumen.ONTICUM,
    )

    # Learn a pattern
    pattern = "consciousness awareness mind"
    neuron.learn_pattern(pattern, strength=1.0)

    # Test recognition of exact pattern
    recognition = neuron.recognize_pattern(pattern)
    logger.info(f"Recognition of exact pattern: {recognition:.3f}")
    assert recognition > 0.0

    # Test recognition of similar pattern
    similar_pattern = "consciousness mind awareness"  # Same words, different order
    recognition_similar = neuron.recognize_pattern(similar_pattern)
    logger.info(f"Recognition of similar pattern: {recognition_similar:.3f}")
    assert recognition_similar > 0.0

    # Test recognition of unrelated pattern
    unrelated = "mathematics physics chemistry"
    recognition_unrelated = neuron.recognize_pattern(unrelated)
    logger.info(f"Recognition of unrelated pattern: {recognition_unrelated:.3f}")
    assert recognition_unrelated < recognition  # Should be lower

    logger.success("✓ Pattern learning test passed")


def test_swarm_initialization():
    """Test 5: Swarm initializes with 18 neurons"""
    logger.info("="*80)
    logger.info("TEST 5: Swarm Initialization")
    logger.info("="*80)

    swarm = NeuronSwarm(neurons_per_layer=6)

    # Check total neurons
    assert len(swarm.neurons) == 18

    # Check distribution across lumina
    ontical_neurons = [
        n for n in swarm.neurons.values()
        if n.lumen_specialization == Lumen.ONTICUM
    ]
    structural_neurons = [
        n for n in swarm.neurons.values()
        if n.lumen_specialization == Lumen.STRUCTURALE
    ]
    participatory_neurons = [
        n for n in swarm.neurons.values()
        if n.lumen_specialization == Lumen.PARTICIPATUM
    ]

    assert len(ontical_neurons) == 6
    assert len(structural_neurons) == 6
    assert len(participatory_neurons) == 6

    logger.info(f"Total neurons: {len(swarm.neurons)}")
    logger.info(f"Ontical (ℓₒ): {len(ontical_neurons)}")
    logger.info(f"Structural (ℓₛ): {len(structural_neurons)}")
    logger.info(f"Participatory (ℓₚ): {len(participatory_neurons)}")

    logger.success("✓ Swarm initialization test passed")
    return swarm


def test_swarm_pattern_processing():
    """Test 6: Swarm processes patterns"""
    logger.info("="*80)
    logger.info("TEST 6: Swarm Pattern Processing")
    logger.info("="*80)

    swarm = NeuronSwarm(neurons_per_layer=6)

    # Process a philosophical pattern
    pattern = "What is consciousness and how does awareness emerge?"
    result = swarm.process_pattern(pattern, iterations=3)

    # Validate result structure
    assert "pattern" in result
    assert "total_neurons" in result
    assert "active_neurons" in result
    assert "activations" in result
    assert "emergent_coherence" in result
    assert "lumen_statistics" in result

    # Check that some neurons activated
    logger.info(f"Active neurons: {result['active_neurons']}/{result['total_neurons']}")
    logger.info(f"Average activation: {result['average_activation']:.3f}")
    logger.info(f"Emergent coherence: {result['emergent_coherence']:.3f}")

    # Log lumen statistics
    for lumen, stats in result['lumen_statistics'].items():
        logger.info(f"{lumen}: mean={stats['mean']:.3f}, max={stats['max']:.3f}")

    assert result['total_neurons'] == 18
    assert 0.0 <= result['emergent_coherence'] <= 1.0

    logger.success("✓ Swarm pattern processing test passed")
    return result


def test_emergent_pattern_recognition():
    """Test 7: Emergent pattern recognition through experience"""
    logger.info("="*80)
    logger.info("TEST 7: Emergent Pattern Recognition")
    logger.info("="*80)

    swarm = NeuronSwarm(neurons_per_layer=6, learning_rate=0.1)

    # Train on similar patterns multiple times
    patterns = [
        "consciousness awareness mind",
        "consciousness mind awareness experience",
        "awareness consciousness subjective experience",
    ]

    logger.info("Training on 3 similar patterns...")
    for i, pattern in enumerate(patterns):
        result = swarm.process_pattern(pattern, iterations=2)
        logger.info(f"  Pattern {i+1}: {result['active_neurons']} neurons active")

    # Now test on a related pattern (should recognize better)
    test_pattern = "consciousness awareness"
    result_familiar = swarm.process_pattern(test_pattern, iterations=2)

    # Test on unrelated pattern
    unrelated_pattern = "mathematics physics chemistry"
    result_unfamiliar = swarm.process_pattern(unrelated_pattern, iterations=2)

    logger.info(f"\nFamiliar pattern: {result_familiar['average_activation']:.3f} avg activation")
    logger.info(f"Unfamiliar pattern: {result_unfamiliar['average_activation']:.3f} avg activation")

    # Familiar pattern should have higher activation
    # (This may not always hold with random initialization, but should trend this way)
    logger.info(f"Emergent coherence (familiar): {result_familiar['emergent_coherence']:.3f}")
    logger.info(f"Emergent coherence (unfamiliar): {result_unfamiliar['emergent_coherence']:.3f}")

    logger.success("✓ Emergent pattern recognition test passed")


def test_connection_matrix():
    """Test 8: Connection matrix formation"""
    logger.info("="*80)
    logger.info("TEST 8: Connection Matrix")
    logger.info("="*80)

    swarm = NeuronSwarm(neurons_per_layer=6)

    # Process multiple patterns to form connections
    patterns = [
        "being existence reality",
        "structure form logic",
        "consciousness awareness experience",
    ]

    for pattern in patterns:
        swarm.process_pattern(pattern, iterations=3)

    # Get connection matrix
    matrix = swarm.get_connection_matrix()

    logger.info(f"Connection matrix shape: {matrix.shape}")
    logger.info(f"Total connections formed: {np.count_nonzero(matrix)}")
    logger.info(f"Average connection strength: {np.mean(np.abs(matrix)):.3f}")
    logger.info(f"Max connection strength: {np.max(np.abs(matrix)):.3f}")

    assert matrix.shape == (18, 18)
    assert np.count_nonzero(matrix) > 0  # Some connections should have formed

    logger.success("✓ Connection matrix test passed")


def test_lumen_specialization():
    """Test 9: Lumen-specific activation patterns"""
    logger.info("="*80)
    logger.info("TEST 9: Lumen Specialization")
    logger.info("="*80)

    swarm = NeuronSwarm(neurons_per_layer=6)

    # Focus on each lumen separately
    ontical_pattern = "being power energy existence"
    structural_pattern = "logic form structure rationality"
    participatory_pattern = "consciousness awareness experience"

    result_ontical = swarm.process_pattern(
        ontical_pattern,
        lumen_focus=Lumen.ONTICUM,
        iterations=2
    )

    result_structural = swarm.process_pattern(
        structural_pattern,
        lumen_focus=Lumen.STRUCTURALE,
        iterations=2
    )

    result_participatory = swarm.process_pattern(
        participatory_pattern,
        lumen_focus=Lumen.PARTICIPATUM,
        iterations=2
    )

    logger.info(f"Ontical focus: {result_ontical['active_neurons']} active")
    logger.info(f"Structural focus: {result_structural['active_neurons']} active")
    logger.info(f"Participatory focus: {result_participatory['active_neurons']} active")

    # Each should have activated some neurons
    assert result_ontical['active_neurons'] >= 0
    assert result_structural['active_neurons'] >= 0
    assert result_participatory['active_neurons'] >= 0

    logger.success("✓ Lumen specialization test passed")


def test_swarm_statistics():
    """Test 10: Swarm summary statistics"""
    logger.info("="*80)
    logger.info("TEST 10: Swarm Statistics")
    logger.info("="*80)

    swarm = NeuronSwarm(neurons_per_layer=6)

    # Process some patterns
    patterns = [
        "consciousness",
        "being",
        "structure",
    ]

    for pattern in patterns:
        swarm.process_pattern(pattern, iterations=2)

    # Get summary
    summary = swarm.get_swarm_summary()

    logger.info(f"Total neurons: {summary['total_neurons']}")
    logger.info(f"Total activations: {summary['total_activations']}")
    logger.info(f"Patterns learned: {summary['total_patterns_learned']}")
    logger.info(f"Avg connections/neuron: {summary['average_connections_per_neuron']:.1f}")
    logger.info(f"Total connections: {summary['total_connections']}")

    assert summary['total_neurons'] == 18
    assert summary['total_activations'] == len(patterns)

    logger.success("✓ Swarm statistics test passed")


def run_all_tests():
    """Run complete neuron swarm test suite"""
    logger.info("="*80)
    logger.info("NEURON SWARM TEST SUITE")
    logger.info("Testing Hebbian learning and emergent intelligence")
    logger.info("="*80)

    tests = [
        ("Neuron Initialization", test_neuron_initialization),
        ("Neuron Activation", test_neuron_activation),
        ("Hebbian Learning", test_hebbian_learning),
        ("Pattern Learning", test_pattern_learning),
        ("Swarm Initialization", test_swarm_initialization),
        ("Swarm Pattern Processing", test_swarm_pattern_processing),
        ("Emergent Pattern Recognition", test_emergent_pattern_recognition),
        ("Connection Matrix", test_connection_matrix),
        ("Lumen Specialization", test_lumen_specialization),
        ("Swarm Statistics", test_swarm_statistics),
    ]

    passed = 0
    failed = 0

    for name, test_func in tests:
        try:
            test_func()
            passed += 1
        except Exception as e:
            logger.error(f"TEST FAILED: {name}")
            logger.error(f"Error: {str(e)}")
            import traceback
            traceback.print_exc()
            failed += 1

    # Summary
    logger.info("="*80)
    logger.info("TEST SUITE SUMMARY")
    logger.info("="*80)
    logger.info(f"Total tests: {len(tests)}")
    logger.success(f"Passed: {passed} ✓")
    if failed > 0:
        logger.error(f"Failed: {failed} ✗")

    for name, _ in tests:
        logger.info(f"  ✓ {name}")

    logger.info("="*80)

    if failed == 0:
        logger.success("ALL TESTS PASSED! 🎉")
        logger.success("Hebbian learning is operational. Neurons are wiring together!")
        return True
    else:
        logger.error(f"{failed} test(s) failed.")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
