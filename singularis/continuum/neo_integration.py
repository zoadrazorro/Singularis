"""
Neo Integration - Bolt Continuum onto Singularis Neo

This module provides the integration layer between:
- Singularis Neo (Beta v2.3) - Current production system
- Singularis Continuum - Next-generation architecture

Safe 3-phase upgrade path:
- Phase 1: Observable (this file) - No control changes
- Phase 2: Advisory - Gradual control handoff
- Phase 3: Autonomous - Full self-modification

Usage:
    # In skyrim_agi.py initialization:
    from singularis.continuum import ContinuumIntegration
    
    self.continuum = ContinuumIntegration(
        phase=1,  # Start with observation only
        subsystems=self.get_all_subsystems()
    )
    
    # In main loop:
    await self.continuum.observe_cycle(
        being_state=self.being_state,
        actual_action=action,
        actual_outcome=outcome
    )
"""

import asyncio
from typing import Dict, Any, Optional, List
from ..core.being_state import BeingState
from .phase1_integration import Phase1Observer


class ContinuumIntegration:
    """
    Main integration class for Continuum.
    Provides safe upgrade path from Neo to Continuum.
    """
    
    def __init__(
        self,
        phase: int = 1,
        subsystems: Optional[List[str]] = None,
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize Continuum integration.
        
        Args:
            phase: Integration phase (1, 2, or 3)
            subsystems: List of Neo subsystem names
            config: Configuration options
        """
        self.phase = phase
        self.config = config or {}
        
        # Phase 1: Observable only
        if phase == 1:
            print("[CONTINUUM] Initializing Phase 1: Observable Mode")
            print("[CONTINUUM] No control changes - pure observation")
            self.observer = Phase1Observer(
                subsystems=subsystems,
                manifold_dimensions=self.config.get('manifold_dimensions', 20)
            )
            self.mode = "OBSERVE"
        
        # Phase 2: Advisory (future)
        elif phase == 2:
            print("[CONTINUUM] Phase 2 not yet implemented")
            print("[CONTINUUM] Falling back to Phase 1")
            self.observer = Phase1Observer(subsystems=subsystems)
            self.mode = "OBSERVE"
        
        # Phase 3: Autonomous (future)
        elif phase == 3:
            print("[CONTINUUM] Phase 3 not yet implemented")
            print("[CONTINUUM] Falling back to Phase 1")
            self.observer = Phase1Observer(subsystems=subsystems)
            self.mode = "OBSERVE"
        
        else:
            raise ValueError(f"Invalid phase: {phase}. Must be 1, 2, or 3.")
        
        print(f"[CONTINUUM] Mode: {self.mode}")
        print(f"[CONTINUUM] Tracking {len(subsystems) if subsystems else 16} subsystems")
    
    async def observe_cycle(
        self,
        being_state: BeingState,
        actual_action: str,
        actual_outcome: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Observe one Neo cycle.
        
        Args:
            being_state: Current BeingState
            actual_action: Action Neo took
            actual_outcome: Outcome (optional, for learning)
        
        Returns:
            Observation data
        """
        if self.phase == 1:
            return await self.observer.observe_cycle(
                being_state,
                actual_action,
                actual_outcome
            )
        
        return {}
    
    def get_stats(self) -> Dict[str, Any]:
        """Get Continuum statistics."""
        if self.phase == 1:
            return self.observer.get_stats()
        return {}
    
    def generate_report(self) -> str:
        """Generate integration report."""
        if self.phase == 1:
            return self.observer.generate_report()
        return "No report available"
    
    def is_ready_for_phase2(self) -> bool:
        """Check if ready to upgrade to Phase 2."""
        if self.phase != 1:
            return False
        
        stats = self.get_stats()
        
        # Criteria for Phase 2:
        # 1. At least 100 observations
        # 2. Advisory match rate > 30%
        # 3. Field coherence stable
        
        observations = stats.get('total_observations', 0)
        match_rate = stats.get('advisory_match_rate', 0)
        
        return observations >= 100 and match_rate > 0.3
    
    async def cleanup(self):
        """Cleanup resources."""
        if self.phase == 1 and hasattr(self, 'observer'):
            await self.observer.cleanup()


def integrate_continuum_into_neo(skyrim_agi_instance):
    """
    Helper function to integrate Continuum into existing SkyrimAGI.
    
    Usage:
        from singularis.continuum import integrate_continuum_into_neo
        integrate_continuum_into_neo(self)  # In SkyrimAGI.__init__
    
    Args:
        skyrim_agi_instance: Instance of SkyrimAGI class
    """
    # Get all subsystems from Neo
    subsystems = [
        'perception', 'consciousness', 'emotion', 'motivation',
        'learning', 'action', 'temporal', 'lumina_ontic',
        'lumina_structural', 'lumina_participatory', 'gpt5',
        'double_helix', 'voice', 'video', 'research', 'philosophy',
        'metacognition', 'main_brain', 'wolfram', 'hybrid_llm'
    ]
    
    # Initialize Continuum in Phase 1
    skyrim_agi_instance.continuum = ContinuumIntegration(
        phase=1,
        subsystems=subsystems,
        config={
            'manifold_dimensions': 20,  # Start small
        }
    )
    
    print("[CONTINUUM] ✓ Integrated into Neo (Phase 1)")
    print("[CONTINUUM] Call continuum.observe_cycle() in main loop")
    
    return skyrim_agi_instance.continuum
