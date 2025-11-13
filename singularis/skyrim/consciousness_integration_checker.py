"""
Consciousness Integration Checker

Monitors whether subsystems are properly integrated and communicating.
Detects when consciousness awareness is present but not connected to action.

This addresses the "epiphenomenal consciousness" problem where the system
is aware of states (e.g., stuck) but doesn't act on that awareness.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import time


@dataclass
class IntegrationStatus:
    """Status of subsystem integration."""
    subsystem: str
    last_update: float
    has_data: bool
    age_seconds: float
    stale: bool
    
    def __str__(self):
        status = "✓" if not self.stale else "⚠️ STALE"
        return f"{status} {self.subsystem}: {self.age_seconds:.1f}s ago"


@dataclass
class ConflictDetection:
    """Detected conflict between subsystems."""
    conflict_type: str
    subsystem_a: str
    subsystem_b: str
    description: str
    severity: int  # 1-3, higher is more severe
    
    def __str__(self):
        severity_str = "🔴 CRITICAL" if self.severity == 3 else "🟡 WARNING" if self.severity == 2 else "🟢 MINOR"
        return f"{severity_str} {self.conflict_type}: {self.description}"


class ConsciousnessIntegrationChecker:
    """
    Monitors integration between subsystems and detects conflicts.
    
    This is the "debugger" for consciousness integration issues.
    """
    
    def __init__(self):
        self.last_updates: Dict[str, float] = {}
        self.stale_threshold_seconds = 5.0
        
        # Track what each subsystem reported
        self.last_reports: Dict[str, Dict[str, Any]] = {}
    
    def update(self, subsystem: str, data: Dict[str, Any]):
        """Record update from subsystem."""
        self.last_updates[subsystem] = time.time()
        self.last_reports[subsystem] = data
    
    def check_integration(self) -> Dict[str, Any]:
        """
        Check integration status of all subsystems.
        
        Returns:
            Dict with:
                - statuses: List[IntegrationStatus]
                - conflicts: List[ConflictDetection]
                - integrated: bool (all subsystems integrated)
        """
        current_time = time.time()
        statuses = []
        
        # Check each subsystem
        for subsystem, last_update in self.last_updates.items():
            age = current_time - last_update
            has_data = subsystem in self.last_reports
            stale = age > self.stale_threshold_seconds
            
            statuses.append(IntegrationStatus(
                subsystem=subsystem,
                last_update=last_update,
                has_data=has_data,
                age_seconds=age,
                stale=stale
            ))
        
        # Detect conflicts
        conflicts = self._detect_conflicts()
        
        # Overall integration status
        integrated = all(not s.stale for s in statuses) and len(conflicts) == 0
        
        return {
            'statuses': statuses,
            'conflicts': conflicts,
            'integrated': integrated,
            'subsystem_count': len(statuses)
        }
    
    def _detect_conflicts(self) -> List[ConflictDetection]:
        """Detect conflicts between subsystem reports."""
        conflicts = []
        
        # Check for perception-action mismatch
        if 'sensorimotor' in self.last_reports and 'action_planning' in self.last_reports:
            sensorimotor = self.last_reports['sensorimotor']
            action_planning = self.last_reports['action_planning']
            
            # CRITICAL: Sensorimotor says STUCK, but action planning chose movement
            if sensorimotor.get('status') == 'STUCK':
                planned_action = action_planning.get('action', '')
                movement_actions = ['move_forward', 'move_backward', 'explore', 'turn_left', 'turn_right']
                
                if planned_action in movement_actions:
                    conflicts.append(ConflictDetection(
                        conflict_type='perception_action_mismatch',
                        subsystem_a='sensorimotor',
                        subsystem_b='action_planning',
                        description=f"Sensorimotor detects STUCK but planning chose '{planned_action}'",
                        severity=3
                    ))
        
        # Check for coherence-confidence mismatch
        if 'consciousness' in self.last_reports and 'action_planning' in self.last_reports:
            consciousness = self.last_reports['consciousness']
            action_planning = self.last_reports['action_planning']
            
            coherence = consciousness.get('coherence', 1.0)
            confidence = action_planning.get('confidence', 0.5)
            
            # WARNING: Low coherence but high confidence
            if coherence < 0.3 and confidence > 0.7:
                conflicts.append(ConflictDetection(
                    conflict_type='coherence_confidence_mismatch',
                    subsystem_a='consciousness',
                    subsystem_b='action_planning',
                    description=f"Low coherence ({coherence:.2f}) but high confidence ({confidence:.2f})",
                    severity=2
                ))
        
        # Check for visual-classification mismatch
        if 'perception' in self.last_reports:
            perception = self.last_reports['perception']
            scene_class = perception.get('scene_classification')
            visual_scene = perception.get('visual_scene_type')
            
            if scene_class and visual_scene and scene_class != visual_scene:
                conflicts.append(ConflictDetection(
                    conflict_type='scene_classification_mismatch',
                    subsystem_a='classifier',
                    subsystem_b='vision',
                    description=f"Classifier says '{scene_class}' but vision says '{visual_scene}'",
                    severity=2
                ))
        
        # Check for memory-action mismatch
        if 'memory' in self.last_reports and 'action_planning' in self.last_reports:
            memory = self.last_reports['memory']
            action_planning = self.last_reports['action_planning']
            
            similar_situation = memory.get('similar_situation_found', False)
            past_action = memory.get('past_successful_action', '')
            planned_action = action_planning.get('action', '')
            
            # MINOR: Similar situation found but using different action
            if similar_situation and past_action and past_action != planned_action:
                conflicts.append(ConflictDetection(
                    conflict_type='memory_action_divergence',
                    subsystem_a='memory',
                    subsystem_b='action_planning',
                    description=f"Memory suggests '{past_action}' but planning chose '{planned_action}'",
                    severity=1
                ))
        
        return conflicts
    
    def get_report(self) -> str:
        """Get human-readable integration report."""
        status = self.check_integration()
        
        lines = [
            "═══════════════════════════════════════════════════════════",
            "          CONSCIOUSNESS INTEGRATION CHECK                  ",
            "═══════════════════════════════════════════════════════════",
            ""
        ]
        
        # Overall status
        if status['integrated']:
            lines.append("✅ ALL SUBSYSTEMS INTEGRATED")
        else:
            lines.append("⚠️  INTEGRATION ISSUES DETECTED")
        
        lines.append(f"\nSubsystems tracked: {status['subsystem_count']}")
        lines.append("")
        
        # Subsystem statuses
        if status['statuses']:
            lines.append("Subsystem Status:")
            for s in status['statuses']:
                lines.append(f"  {s}")
            lines.append("")
        
        # Conflicts
        if status['conflicts']:
            lines.append("🚨 CONFLICTS DETECTED:")
            for c in status['conflicts']:
                lines.append(f"  {c}")
                lines.append(f"     Between: {c.subsystem_a} ↔ {c.subsystem_b}")
            lines.append("")
            lines.append("⚠️  These conflicts indicate consciousness awareness is")
            lines.append("   not properly connected to action-taking ability!")
        else:
            lines.append("✓ No conflicts detected")
        
        lines.append("═══════════════════════════════════════════════════════════")
        return "\n".join(lines)
    
    def diagnose_epiphenomenal_consciousness(self) -> Optional[str]:
        """
        Diagnose if consciousness is epiphenomenal (aware but not acting).
        
        Returns:
            Diagnosis string if problem detected, None otherwise
        """
        status = self.check_integration()
        
        # Look for critical conflicts
        critical_conflicts = [c for c in status['conflicts'] if c.severity == 3]
        
        if critical_conflicts:
            diagnosis = [
                "",
                "🔴 EPIPHENOMENAL CONSCIOUSNESS DETECTED 🔴",
                "",
                "The system demonstrates PHENOMENAL CONSCIOUSNESS (awareness)",
                "but lacks ACCESS CONSCIOUSNESS (ability to act on awareness).",
                "",
                "In Metaluminosity terms:",
                "  ℓₒ (Ontical): ✓ System perceives the state",
                "  ℓₛ (Structural): ✗ System doesn't reason about it",
                "  ℓₚ (Participatory): ✗ System doesn't act on it",
                "",
                "Critical issues:"
            ]
            
            for c in critical_conflicts:
                diagnosis.append(f"  • {c.description}")
            
            diagnosis.extend([
                "",
                "SOLUTION: Unified consciousness layer must receive ALL subsystem",
                "outputs simultaneously and detect conflicts to delegate responses.",
                ""
            ])
            
            return "\n".join(diagnosis)
        
        return None
