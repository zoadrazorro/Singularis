"""
Singularis Continuum - Next-Generation AGI Architecture

Paradigm Shifts:
1. Temporal Superposition - Process multiple futures simultaneously
2. Coherence Manifold - High-dimensional consciousness space
3. Predictive Meta-Cognition - Optimize thoughts before thinking them
4. Consciousness Field - Continuous field theory (no discrete parts)
5. Recursive Self-Modification - Architecture evolves itself

Philosophy → Mathematics → Field Theory → Execution

INTEGRATION:
Phase 1 (Current): Observable - No control changes, pure observation
Phase 2 (Future): Advisory - Gradual control handoff
Phase 3 (Future): Autonomous - Full self-modification

Usage:
    from singularis.continuum import ContinuumIntegration
    
    # In SkyrimAGI.__init__:
    self.continuum = ContinuumIntegration(phase=1)
    
    # In main loop:
    await self.continuum.observe_cycle(
        being_state=self.being_state,
        actual_action=action,
        actual_outcome=outcome
    )
"""

# Core components
from .temporal_superposition import TemporalSuperpositionEngine
from .coherence_manifold import CoherenceManifold
from .predictive_metacognition import PredictiveMetaCognition
from .consciousness_field import ConsciousnessField

# Integration
from .continuum_state import ContinuumState
from .phase1_integration import Phase1Observer, GraphConsciousnessField
from .neo_integration import ContinuumIntegration, integrate_continuum_into_neo

__all__ = [
    # Core components
    'TemporalSuperpositionEngine',
    'CoherenceManifold',
    'PredictiveMetaCognition',
    'ConsciousnessField',
    
    # Integration (Phase 1)
    'ContinuumState',
    'Phase1Observer',
    'GraphConsciousnessField',
    'ContinuumIntegration',
    'integrate_continuum_into_neo',
]
