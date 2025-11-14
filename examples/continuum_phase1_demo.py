"""
Continuum Phase 1 Demo

Demonstrates how to integrate Continuum into Neo in Phase 1 (Observable mode).
This is a standalone demo that doesn't require Skyrim.
"""

import asyncio
import numpy as np
from singularis.core.being_state import BeingState
from singularis.core.lumina import Lumina
from singularis.continuum import ContinuumIntegration


async def simulate_neo_cycle(cycle: int) -> tuple[BeingState, str, dict]:
    """
    Simulate one Neo cycle.
    Returns: (being_state, action, outcome)
    """
    # Create mock BeingState
    being_state = BeingState()
    being_state.cycle_number = cycle
    being_state.coherence_C = 0.7 + np.random.normal(0, 0.05)
    being_state.temporal_coherence = 0.75 + np.random.normal(0, 0.03)
    being_state.phi_hat = 0.6 + np.random.normal(0, 0.04)
    being_state.emotion_intensity = 0.5 + np.random.normal(0, 0.1)
    
    # Mock Lumina
    being_state.lumina = Lumina(
        ontic=0.8 + np.random.normal(0, 0.02),
        structural=0.75 + np.random.normal(0, 0.02),
        participatory=0.7 + np.random.normal(0, 0.02)
    )
    
    # Mock action (Neo's decision)
    actions = ['move_forward', 'turn_left', 'turn_right', 'interact', 'wait']
    action = np.random.choice(actions)
    
    # Mock outcome
    outcome = {
        'coherence': being_state.coherence_C + np.random.normal(0.01, 0.02),
        'success': np.random.random() > 0.2,  # 80% success rate
        'reward': np.random.normal(0.5, 0.2)
    }
    
    return being_state, action, outcome


async def main():
    """Run Phase 1 demo."""
    print("=" * 70)
    print("CONTINUUM PHASE 1 DEMO - Observable Mode")
    print("=" * 70)
    print()
    
    # Initialize Continuum (Phase 1)
    continuum = ContinuumIntegration(
        phase=1,
        subsystems=[
            'perception', 'consciousness', 'emotion', 'motivation',
            'learning', 'action', 'temporal', 'lumina_ontic',
            'lumina_structural', 'lumina_participatory'
        ],
        config={
            'manifold_dimensions': 20
        }
    )
    
    print("\n[DEMO] Running 50 simulated Neo cycles...")
    print("[DEMO] Continuum will observe and log advisory actions\n")
    
    # Run 50 cycles
    for cycle in range(50):
        # Simulate Neo cycle
        being_state, action, outcome = await simulate_neo_cycle(cycle)
        
        # Let Continuum observe
        observation = await continuum.observe_cycle(
            being_state=being_state,
            actual_action=action,
            actual_outcome=outcome
        )
        
        # Print progress every 10 cycles
        if (cycle + 1) % 10 == 0:
            print(f"\n[DEMO] Completed {cycle + 1} cycles")
            stats = continuum.get_stats()
            print(f"[DEMO] Advisory match rate: {stats.get('advisory_match_rate', 0):.1%}")
            print(f"[DEMO] Field coherence: {stats.get('avg_field_coherence', 0):.3f}")
    
    # Generate final report
    print("\n" + "=" * 70)
    print("FINAL REPORT")
    print("=" * 70)
    
    report = continuum.generate_report()
    print(report)
    
    # Check if ready for Phase 2
    if continuum.is_ready_for_phase2():
        print("\n✓ READY FOR PHASE 2 UPGRADE")
    else:
        print("\n⚠ Need more observations for Phase 2")
        print("  Run 100+ cycles with >30% match rate")
    
    print("\n" + "=" * 70)
    print("DEMO COMPLETE")
    print("=" * 70)


if __name__ == '__main__':
    asyncio.run(main())
