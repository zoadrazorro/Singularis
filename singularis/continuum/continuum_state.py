"""
Continuum State - Unified State Representation

Wraps BeingState and provides interface for Continuum components.
This is the bridge between Neo (discrete) and Continuum (continuous).
"""

import numpy as np
from typing import Dict, Any, Optional
from dataclasses import dataclass
from ..core.being_state import BeingState


@dataclass
class ContinuumState:
    """
    Unified state representation for Continuum.
    Can be constructed from BeingState or field summary.
    """
    
    # Core state
    being_state: Optional[BeingState] = None
    field_summary: Optional[Dict[str, Any]] = None
    
    # Derived properties
    manifold_position: Optional[np.ndarray] = None
    field_coherence: float = 0.5
    
    @classmethod
    def from_being_state(cls, being_state: BeingState) -> 'ContinuumState':
        """Create ContinuumState from BeingState."""
        return cls(
            being_state=being_state,
            field_summary=None,
            manifold_position=None,
            field_coherence=being_state.coherence_C
        )
    
    @classmethod
    def from_field_summary(cls, field_summary: Dict[str, Any]) -> 'ContinuumState':
        """Create ContinuumState from field summary."""
        # Create pseudo-BeingState from field
        pseudo_being = BeingState()
        pseudo_being.coherence_C = field_summary.get('global_coherence', 0.5)
        pseudo_being.temporal_coherence = field_summary.get('temporal_coherence', 0.5)
        
        return cls(
            being_state=pseudo_being,
            field_summary=field_summary,
            manifold_position=None,
            field_coherence=field_summary.get('global_coherence', 0.5)
        )
    
    def get_coherence(self) -> float:
        """Get coherence value (from BeingState or field)."""
        if self.being_state:
            return self.being_state.coherence_C
        return self.field_coherence
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'has_being_state': self.being_state is not None,
            'has_field_summary': self.field_summary is not None,
            'coherence': self.get_coherence(),
            'manifold_position': self.manifold_position.tolist() if self.manifold_position is not None else None
        }
