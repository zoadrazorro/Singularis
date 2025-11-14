"""
Coherence Engine V2 - Meta-Logic 2.0

The executive consciousness layer that monitors cognitive state and
applies dynamic corrections to maintain coherence.

This extends the base CoherenceEngine (which computes coherence) by
adding executive function - the ability to detect problems and fix them.

Key capabilities:
- Detect contradictions across tracks
- Measure cognitive tension
- Trigger context shifts when needed
- Dynamically adjust track weights
- Rewrite cognitive rules on-the-fly
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple
from enum import Enum
import time
import math


class InterventionType(Enum):
    """Types of meta-logic interventions"""
    DAMPEN_TRACK = "dampen_track"
    BOOST_TRACK = "boost_track"
    FORCE_CONTEXT_SHIFT = "force_context_shift"
    REWRITE_RULE = "rewrite_rule"
    MODULATE_EMOTION = "modulate_emotion"
    SYNC_TRACKS = "sync_tracks"
    RESET_TRACK = "reset_track"


@dataclass
class CoherenceReport:
    """
    Comprehensive coherence analysis across all cognitive dimensions.
    
    This is the diagnostic output that drives meta-logic decisions.
    """
    # Core metrics
    contradiction_level: float = 0.0  # [0, 1] - how contradictory beliefs are
    cognitive_tension: float = 0.0    # [0, 1] - dissonance between tracks
    coherence_ratio: float = 1.0      # [0, 1] - integrated vs conflicting info
    modal_consistency: float = 1.0    # [0, 1] - alignment across logic modes
    context_appropriateness: float = 1.0  # [0, 1] - fit to environment
    
    # Detailed diagnostics
    conflicting_tracks: List[Tuple[str, str]] = field(default_factory=list)
    contradictions: List[Dict] = field(default_factory=list)
    tension_sources: List[str] = field(default_factory=list)
    misaligned_tracks: List[str] = field(default_factory=list)
    
    # Temporal
    timestamp: float = field(default_factory=time.time)
    
    def needs_adjustment(self, thresholds: Dict[str, float]) -> bool:
        """Check if any metric exceeds intervention threshold"""
        return (
            self.contradiction_level > thresholds.get('contradiction', 0.7) or
            self.cognitive_tension > thresholds.get('tension', 0.6) or
            self.coherence_ratio < thresholds.get('coherence', 0.4) or
            self.modal_consistency < thresholds.get('consistency', 0.5) or
            self.context_appropriateness < thresholds.get('context', 0.5)
        )
    
    def severity(self) -> float:
        """Overall severity score [0, 1] - higher = worse"""
        return (
            self.contradiction_level * 0.3 +
            self.cognitive_tension * 0.25 +
            (1.0 - self.coherence_ratio) * 0.25 +
            (1.0 - self.modal_consistency) * 0.1 +
            (1.0 - self.context_appropriateness) * 0.1
        )


@dataclass
class CognitiveAdjustment:
    """Single adjustment to cognitive state"""
    intervention_type: InterventionType
    target: str  # Track name, context, or rule ID
    parameter: str  # What to adjust
    value: float  # New value or delta
    reason: str  # Why this adjustment


@dataclass
class CognitiveAdjustments:
    """Collection of adjustments to apply"""
    adjustments: List[CognitiveAdjustment] = field(default_factory=list)
    priority: int = 0  # Higher = more urgent
    
    def add(self, intervention: InterventionType, target: str, 
            parameter: str, value: float, reason: str):
        """Add an adjustment"""
        self.adjustments.append(CognitiveAdjustment(
            intervention_type=intervention,
            target=target,
            parameter=parameter,
            value=value,
            reason=reason
        ))
    
    def dampen_track(self, track: str, factor: float, reason: str):
        """Dampen a track's influence"""
        self.add(InterventionType.DAMPEN_TRACK, track, 'weight', factor, reason)
    
    def boost_track(self, track: str, factor: float, reason: str):
        """Boost a track's influence"""
        self.add(InterventionType.BOOST_TRACK, track, 'weight', factor, reason)
    
    def force_context_shift(self, new_context: str, reason: str):
        """Force immediate context change"""
        self.add(InterventionType.FORCE_CONTEXT_SHIFT, new_context, 'active', 1.0, reason)
    
    def modulate_emotion(self, emotion: str, factor: float, reason: str):
        """Adjust emotional gain/inhibition"""
        self.add(InterventionType.MODULATE_EMOTION, emotion, 'gain', factor, reason)
    
    def sync_tracks(self, tracks: List[str], reason: str):
        """Force track synchronization"""
        self.add(InterventionType.SYNC_TRACKS, ','.join(tracks), 'phase', 0.0, reason)


class CoherenceEngineV2:
    """
    Meta-Logic 2.0: The executive consciousness layer
    
    This is the "brain's conscience" - continuously monitoring cognitive state
    and applying corrections to maintain coherence.
    
    Unlike the base CoherenceEngine (which just computes a score), this one
    actively intervenes to fix problems.
    """
    
    def __init__(
        self,
        contradiction_threshold: float = 0.7,
        tension_threshold: float = 0.6,
        coherence_minimum: float = 0.4,
        consistency_minimum: float = 0.5,
        context_fit_minimum: float = 0.5,
        verbose: bool = True
    ):
        """
        Initialize Coherence Engine V2.
        
        Args:
            contradiction_threshold: Max acceptable contradiction level
            tension_threshold: Max acceptable cognitive tension
            coherence_minimum: Min acceptable coherence ratio
            consistency_minimum: Min acceptable modal consistency
            context_fit_minimum: Min acceptable context appropriateness
            verbose: Print diagnostic info
        """
        self.thresholds = {
            'contradiction': contradiction_threshold,
            'tension': tension_threshold,
            'coherence': coherence_minimum,
            'consistency': consistency_minimum,
            'context': context_fit_minimum
        }
        
        self.verbose = verbose
        
        # History
        self.reports: List[CoherenceReport] = []
        self.interventions: List[CognitiveAdjustments] = []
        self.max_history = 1000
        
        # Statistics
        self.total_evaluations = 0
        self.total_interventions = 0
        
        if verbose:
            print("[COHERENCE V2] Meta-Logic 2.0 initialized")
            print(f"[COHERENCE V2] Thresholds: {self.thresholds}")
    
    def evaluate_coherence(self, cognitive_state: 'CognitiveState') -> CoherenceReport:
        """
        Comprehensive coherence analysis across all cognitive dimensions.
        
        Args:
            cognitive_state: Current cognitive state with tracks, contexts, etc.
        
        Returns:
            CoherenceReport with detailed diagnostics
        """
        self.total_evaluations += 1
        
        report = CoherenceReport()
        
        # 1. Detect contradictions
        report.contradiction_level, report.contradictions = self._detect_contradictions(
            cognitive_state
        )
        
        # 2. Measure cognitive tension
        report.cognitive_tension, report.tension_sources = self._measure_cognitive_tension(
            cognitive_state
        )
        
        # 3. Compute coherence ratio
        report.coherence_ratio = self._compute_coherence_ratio(cognitive_state)
        
        # 4. Check modal consistency
        report.modal_consistency, report.misaligned_tracks = self._check_modal_alignment(
            cognitive_state
        )
        
        # 5. Evaluate context appropriateness
        report.context_appropriateness = self._evaluate_context_appropriateness(
            cognitive_state
        )
        
        # 6. Identify conflicting tracks
        report.conflicting_tracks = self._find_conflicting_tracks(cognitive_state)
        
        # Store report
        self.reports.append(report)
        if len(self.reports) > self.max_history:
            self.reports.pop(0)
        
        if self.verbose and report.severity() > 0.5:
            print(f"[COHERENCE V2] WARNING High severity: {report.severity():.2f}")
            print(f"  Contradiction: {report.contradiction_level:.2f}")
            print(f"  Tension: {report.cognitive_tension:.2f}")
            print(f"  Coherence: {report.coherence_ratio:.2f}")
        
        return report
    
    def apply_corrections(self, report: CoherenceReport) -> CognitiveAdjustments:
        """
        Apply dynamic adjustments to restore coherence.
        
        This is where meta-logic becomes executive function - we don't just
        observe problems, we fix them.
        
        Args:
            report: Coherence diagnostic report
        
        Returns:
            CognitiveAdjustments to apply to the system
        """
        adjustments = CognitiveAdjustments()
        
        # Priority based on severity
        adjustments.priority = int(report.severity() * 10)
        
        # 1. Handle contradictions
        if report.contradiction_level > self.thresholds['contradiction']:
            self._resolve_contradictions(report, adjustments)
        
        # 2. Reduce cognitive tension
        if report.cognitive_tension > self.thresholds['tension']:
            self._reduce_tension(report, adjustments)
        
        # 3. Restore coherence
        if report.coherence_ratio < self.thresholds['coherence']:
            self._restore_coherence(report, adjustments)
        
        # 4. Fix modal inconsistency
        if report.modal_consistency < self.thresholds['consistency']:
            self._fix_modal_consistency(report, adjustments)
        
        # 5. Adjust context if inappropriate
        if report.context_appropriateness < self.thresholds['context']:
            self._adjust_context(report, adjustments)
        
        # Store intervention
        if adjustments.adjustments:
            self.total_interventions += 1
            self.interventions.append(adjustments)
            if len(self.interventions) > self.max_history:
                self.interventions.pop(0)
            
            if self.verbose:
                print(f"[COHERENCE V2] Applying {len(adjustments.adjustments)} corrections")
                for adj in adjustments.adjustments[:3]:  # Show first 3
                    print(f"  - {adj.intervention_type.value}: {adj.target} ({adj.reason})")
        
        return adjustments
    
    # ========== Detection Methods ==========
    
    def _detect_contradictions(self, state: 'CognitiveState') -> Tuple[float, List[Dict]]:
        """
        Detect logical contradictions across tracks.
        
        A contradiction occurs when:
        - Same TruthValue has opposite values on different tracks
        - Paraconsistent track holds both P and ¬P strongly
        - Beliefs conflict with strong evidence
        """
        contradictions = []
        
        # Check for opposite values across tracks
        for tv_name, tv in state.truth_values.items():
            tracks = tv.tracks.keys()
            for i, track1 in enumerate(tracks):
                for track2 in list(tracks)[i+1:]:
                    val1 = tv.get(track1)
                    val2 = tv.get(track2)
                    
                    # Opposite values (one high, one low)
                    if abs(val1 - val2) > 0.7:
                        contradictions.append({
                            'truthvalue': tv_name,
                            'track1': track1,
                            'track2': track2,
                            'val1': val1,
                            'val2': val2,
                            'severity': abs(val1 - val2)
                        })
        
        # Compute overall contradiction level
        if not contradictions:
            return 0.0, []
        
        avg_severity = sum(c['severity'] for c in contradictions) / len(contradictions)
        return min(1.0, avg_severity), contradictions
    
    def _measure_cognitive_tension(self, state: 'CognitiveState') -> Tuple[float, List[str]]:
        """
        Measure dissonance between competing beliefs or goals.
        
        Tension arises from:
        - Conflicting goals
        - Incompatible beliefs
        - Emotional dissonance
        """
        tension_sources = []
        total_tension = 0.0
        count = 0
        
        # Check for goal conflicts
        if hasattr(state, 'goals'):
            for i, goal1 in enumerate(state.goals):
                for goal2 in state.goals[i+1:]:
                    if self._goals_conflict(goal1, goal2):
                        tension_sources.append(f"Goal conflict: {goal1} vs {goal2}")
                        total_tension += 0.5
                        count += 1
        
        # Check for emotional dissonance
        if hasattr(state, 'emotions'):
            # Fear + Trust = tension
            fear = state.emotions.get('fear', 0.0)
            trust = state.emotions.get('trust', 0.0)
            if fear > 0.5 and trust > 0.5:
                tension_sources.append("Emotional dissonance: high fear + high trust")
                total_tension += fear * trust
                count += 1
        
        # Average tension
        if count == 0:
            return 0.0, []
        
        return min(1.0, total_tension / count), tension_sources
    
    def _compute_coherence_ratio(self, state: 'CognitiveState') -> float:
        """
        Ratio of integrated vs. conflicting information.
        
        High coherence = most tracks agree
        Low coherence = tracks diverge
        """
        if not hasattr(state, 'truth_values') or not state.truth_values:
            return 1.0
        
        agreements = 0
        comparisons = 0
        
        for tv in state.truth_values.values():
            tracks = list(tv.tracks.keys())
            if len(tracks) < 2:
                continue
            
            # Compare all track pairs
            for i, track1 in enumerate(tracks):
                for track2 in tracks[i+1:]:
                    val1 = tv.get(track1)
                    val2 = tv.get(track2)
                    
                    # Agreement if values are close
                    if abs(val1 - val2) < 0.3:
                        agreements += 1
                    comparisons += 1
        
        if comparisons == 0:
            return 1.0
        
        return agreements / comparisons
    
    def _check_modal_alignment(self, state: 'CognitiveState') -> Tuple[float, List[str]]:
        """
        Check if different cognitive modes (perception, intuition, reflection) align.
        
        Misalignment = perception says one thing, intuition says another
        """
        misaligned = []
        
        # This requires track metadata about their cognitive role
        # For now, use heuristic: fast tracks vs slow tracks should roughly agree
        
        if not hasattr(state, 'tracks'):
            return 1.0, []
        
        fast_tracks = [t for t in state.tracks if t.period < 200]
        slow_tracks = [t for t in state.tracks if t.period > 1000]
        
        if not fast_tracks or not slow_tracks:
            return 1.0, []
        
        # Compare average values
        # (This is simplified - real version would compare specific TruthValues)
        consistency = 0.8  # Placeholder
        
        return consistency, misaligned
    
    def _evaluate_context_appropriateness(self, state: 'CognitiveState') -> float:
        """
        Validate that current cognitive state matches environmental demands.
        
        E.g., if danger is high but context is 'creative', that's inappropriate
        """
        if not hasattr(state, 'context') or not hasattr(state, 'truth_values'):
            return 1.0
        
        context = state.context
        
        # Context-specific checks
        if context == 'survival':
            # Should have high alertness, low creativity
            danger = state.truth_values.get('danger', None)
            if danger and danger.get('main') < 0.3:
                return 0.5  # In survival mode but low danger = inappropriate
        
        elif context == 'creative':
            # Should have low stress, high openness
            stress = state.truth_values.get('stress', None)
            if stress and stress.get('main') > 0.7:
                return 0.5  # Too stressed for creativity
        
        return 1.0  # Default: appropriate
    
    def _find_conflicting_tracks(self, state: 'CognitiveState') -> List[Tuple[str, str]]:
        """Find pairs of tracks with conflicting values"""
        conflicts = []
        
        for tv_name, tv in state.truth_values.items():
            tracks = list(tv.tracks.keys())
            for i, track1 in enumerate(tracks):
                for track2 in tracks[i+1:]:
                    val1 = tv.get(track1)
                    val2 = tv.get(track2)
                    
                    if abs(val1 - val2) > 0.6:
                        conflicts.append((f"{tv_name}.{track1}", f"{tv_name}.{track2}"))
        
        return conflicts
    
    # ========== Correction Methods ==========
    
    def _resolve_contradictions(self, report: CoherenceReport, adjustments: CognitiveAdjustments):
        """Resolve detected contradictions"""
        for contradiction in report.contradictions[:3]:  # Top 3
            # Dampen the more extreme track
            tv = contradiction['truthvalue']
            track1 = contradiction['track1']
            track2 = contradiction['track2']
            val1 = contradiction['val1']
            val2 = contradiction['val2']
            
            # Dampen whichever is more extreme
            if abs(val1 - 0.5) > abs(val2 - 0.5):
                adjustments.dampen_track(
                    f"{tv}.{track1}",
                    0.7,
                    f"Contradiction with {track2}"
                )
            else:
                adjustments.dampen_track(
                    f"{tv}.{track2}",
                    0.7,
                    f"Contradiction with {track1}"
                )
    
    def _reduce_tension(self, report: CoherenceReport, adjustments: CognitiveAdjustments):
        """Reduce cognitive tension"""
        # Force context shift if tension is very high
        if report.cognitive_tension > 0.8:
            adjustments.force_context_shift(
                'reflection',
                f"High tension ({report.cognitive_tension:.2f}) requires reflection"
            )
        
        # Dampen conflicting tracks
        for track1, track2 in report.conflicting_tracks[:2]:
            adjustments.dampen_track(track1, 0.8, "Reducing tension")
            adjustments.dampen_track(track2, 0.8, "Reducing tension")
    
    def _restore_coherence(self, report: CoherenceReport, adjustments: CognitiveAdjustments):
        """Restore coherence ratio"""
        # Sync misaligned tracks
        if report.misaligned_tracks:
            adjustments.sync_tracks(
                report.misaligned_tracks[:3],
                f"Low coherence ({report.coherence_ratio:.2f})"
            )
    
    def _fix_modal_consistency(self, report: CoherenceReport, adjustments: CognitiveAdjustments):
        """Fix modal inconsistency"""
        for track in report.misaligned_tracks[:2]:
            adjustments.boost_track(
                track,
                1.2,
                "Improving modal consistency"
            )
    
    def _adjust_context(self, report: CoherenceReport, adjustments: CognitiveAdjustments):
        """Adjust context to match state"""
        # This requires knowing what context would be appropriate
        # For now, default to 'reflection' when confused
        adjustments.force_context_shift(
            'reflection',
            f"Context inappropriate ({report.context_appropriateness:.2f})"
        )
    
    # ========== Utility Methods ==========
    
    def _goals_conflict(self, goal1: str, goal2: str) -> bool:
        """Check if two goals conflict"""
        # Simplified - real version would use semantic understanding
        conflict_pairs = [
            ('explore', 'hide'),
            ('attack', 'flee'),
            ('trust', 'suspect'),
        ]
        
        for g1, g2 in conflict_pairs:
            if (g1 in goal1.lower() and g2 in goal2.lower()) or \
               (g2 in goal1.lower() and g1 in goal2.lower()):
                return True
        
        return False
    
    def get_statistics(self) -> Dict:
        """Get engine statistics"""
        return {
            'total_evaluations': self.total_evaluations,
            'total_interventions': self.total_interventions,
            'intervention_rate': self.total_interventions / max(1, self.total_evaluations),
            'avg_severity': sum(r.severity() for r in self.reports[-100:]) / max(1, len(self.reports[-100:])),
            'recent_reports': len(self.reports),
        }


# ========== Mock CognitiveState for Type Hints ==========
# Real version would import from actual cognitive architecture

class CognitiveState:
    """
    Mock cognitive state for type hints.
    Real implementation would come from HaackLang runtime.
    """
    def __init__(self):
        self.truth_values: Dict = {}
        self.tracks: List = []
        self.context: str = 'default'
        self.goals: List[str] = []
        self.emotions: Dict[str, float] = {}
