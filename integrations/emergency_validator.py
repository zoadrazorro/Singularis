"""
Emergency Validator - False Positive Prevention

CRITICAL: Emergency detection (falls, injuries) must be paranoid about false positives.

Principles:
1. Never trigger on single frame
2. Require temporal consistency (N frames over M seconds)
3. Cross-validate with other sensors (heart rate, motion)
4. Escalate gradually (check-in → warning → emergency)
5. Always give user chance to respond before escalating

This prevents:
- Camera glitches triggering 911 advice
- User sitting down being detected as fall
- Shadows/pets triggering false alarms
- Single anomalous sensor reading causing panic
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from enum import Enum

from loguru import logger

from life_timeline import LifeTimeline, LifeEvent, EventType, EventSource


class EmergencySeverity(Enum):
    """Severity levels for emergency validation."""
    NONE = "none"              # No emergency
    SUSPICIOUS = "suspicious"  # Single indicator, needs validation
    LIKELY = "likely"          # Multiple indicators, check on user
    CONFIRMED = "confirmed"    # Strong evidence, advise emergency action


@dataclass
class EmergencyEvidence:
    """Evidence for potential emergency."""
    event_type: str  # 'fall', 'no_movement', 'hr_spike', etc.
    timestamp: datetime
    confidence: float  # 0-1
    source: str  # 'camera', 'fitbit', etc.
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class EmergencyValidation:
    """Result of emergency validation."""
    is_emergency: bool
    severity: EmergencySeverity
    confidence: float  # 0-1
    evidence: List[EmergencyEvidence]
    reasoning: str
    recommended_action: str
    escalation_level: int  # 1=check-in, 2=warning, 3=emergency


class EmergencyValidator:
    """
    Validates potential emergencies with paranoid false-positive prevention.
    
    Key Features:
    - Temporal validation (requires consistency over time)
    - Cross-sensor validation (multiple sources must agree)
    - Graduated escalation (check-in before emergency)
    - User response tracking (escalate only if no response)
    """
    
    def __init__(self, timeline: LifeTimeline):
        """
        Initialize validator.
        
        Args:
            timeline: LifeTimeline for historical context
        """
        self.timeline = timeline
        
        # Validation thresholds
        self.fall_validation_frames = 3  # Require 3 frames
        self.fall_validation_seconds = 5.0  # Within 5 seconds
        self.no_movement_hours = 6  # 6 hours of no movement
        self.hr_spike_threshold = 1.5  # 150% of baseline
        
        # Escalation tracking
        self.pending_validations: Dict[str, List[EmergencyEvidence]] = {}
        self.user_responses: Dict[str, datetime] = {}
        self.escalation_attempts: Dict[str, int] = {}
        
        logger.info("[EMERGENCY-VALIDATOR] Initialized with paranoid false-positive prevention")
    
    def validate_fall(
        self,
        user_id: str,
        fall_event: LifeEvent
    ) -> EmergencyValidation:
        """
        Validate potential fall with temporal consistency check.
        
        Args:
            user_id: User ID
            fall_event: Fall detection event
            
        Returns:
            EmergencyValidation with severity and recommended action
        """
        logger.info(f"[EMERGENCY-VALIDATOR] Validating potential fall for {user_id}")
        
        # Step 1: Check temporal consistency (multiple frames)
        recent_falls = self._get_recent_falls(user_id, seconds=self.fall_validation_seconds)
        
        if len(recent_falls) < self.fall_validation_frames:
            logger.info(
                f"[EMERGENCY-VALIDATOR] Only {len(recent_falls)} fall frames, "
                f"need {self.fall_validation_frames} for validation"
            )
            return EmergencyValidation(
                is_emergency=False,
                severity=EmergencySeverity.SUSPICIOUS,
                confidence=0.3,
                evidence=[EmergencyEvidence(
                    event_type='fall',
                    timestamp=fall_event.timestamp,
                    confidence=fall_event.confidence or 0.5,
                    source='camera',
                    details={'frames': len(recent_falls)}
                )],
                reasoning=f"Single fall frame detected, need {self.fall_validation_frames} "
                         f"consistent frames for validation",
                recommended_action="Monitor for additional frames",
                escalation_level=0
            )
        
        # Step 2: Cross-validate with other sensors
        hr_spike = self._check_heart_rate_spike(user_id, fall_event.timestamp)
        no_movement = self._check_no_movement_after(user_id, fall_event.timestamp, minutes=2)
        
        evidence = [
            EmergencyEvidence(
                event_type='fall',
                timestamp=fall_event.timestamp,
                confidence=fall_event.confidence or 0.8,
                source='camera',
                details={'frames': len(recent_falls)}
            )
        ]
        
        if hr_spike:
            evidence.append(EmergencyEvidence(
                event_type='hr_spike',
                timestamp=hr_spike['timestamp'],
                confidence=0.7,
                source='fitbit',
                details={'bpm': hr_spike['bpm']}
            ))
        
        if no_movement:
            evidence.append(EmergencyEvidence(
                event_type='no_movement',
                timestamp=datetime.now(),
                confidence=0.6,
                source='camera',
                details={'duration_seconds': no_movement['duration']}
            ))
        
        # Step 3: Determine severity based on evidence
        evidence_count = len(evidence)
        
        if evidence_count >= 3:
            # Strong evidence: fall + HR spike + no movement
            severity = EmergencySeverity.CONFIRMED
            confidence = 0.9
            recommended_action = "IMMEDIATE CHECK-IN: Ask if user is okay. If no response, advise calling 911."
            escalation_level = 2
            reasoning = "Fall detected with corroborating evidence (HR spike + no movement)"
        
        elif evidence_count == 2:
            # Moderate evidence: fall + one other indicator
            severity = EmergencySeverity.LIKELY
            confidence = 0.7
            recommended_action = "CHECK-IN: Ask if user is okay"
            escalation_level = 1
            reasoning = "Fall detected with one corroborating indicator"
        
        else:
            # Weak evidence: just consistent fall frames
            severity = EmergencySeverity.SUSPICIOUS
            confidence = 0.5
            recommended_action = "GENTLE CHECK-IN: 'I noticed you might have fallen, are you okay?'"
            escalation_level = 1
            reasoning = "Consistent fall posture detected across multiple frames"
        
        # Step 4: Check escalation history
        escalation_key = f"{user_id}_fall"
        if escalation_key in self.escalation_attempts:
            attempts = self.escalation_attempts[escalation_key]
            if attempts >= 2 and severity != EmergencySeverity.NONE:
                # User hasn't responded to 2+ check-ins, escalate
                severity = EmergencySeverity.CONFIRMED
                confidence = min(confidence + 0.2, 1.0)
                recommended_action = "ESCALATE: No response to check-ins. Advise user to call 911 if able."
                escalation_level = 3
                reasoning += f" + No response to {attempts} previous check-ins"
        
        logger.info(
            f"[EMERGENCY-VALIDATOR] Fall validation: {severity.value} "
            f"(confidence: {confidence:.2f}, evidence: {evidence_count})"
        )
        
        return EmergencyValidation(
            is_emergency=(severity in [EmergencySeverity.LIKELY, EmergencySeverity.CONFIRMED]),
            severity=severity,
            confidence=confidence,
            evidence=evidence,
            reasoning=reasoning,
            recommended_action=recommended_action,
            escalation_level=escalation_level
        )
    
    def validate_no_movement(
        self,
        user_id: str,
        duration_hours: float
    ) -> EmergencyValidation:
        """
        Validate no movement anomaly with context checks.
        
        Args:
            user_id: User ID
            duration_hours: Hours of no movement
            
        Returns:
            EmergencyValidation
        """
        logger.info(f"[EMERGENCY-VALIDATOR] Validating {duration_hours}h no movement for {user_id}")
        
        # Check if this is normal (e.g., sleeping)
        current_hour = datetime.now().hour
        is_night = 22 <= current_hour or current_hour <= 7
        is_weekend = datetime.now().weekday() >= 5
        
        # Get last known location
        recent_room_events = self.timeline.query_by_type(
            user_id,
            EventType.ROOM_ENTER,
            start_time=datetime.now() - timedelta(hours=duration_hours)
        )
        
        last_room = None
        if recent_room_events:
            last_room = recent_room_events[-1].features.get('room')
        
        evidence = [
            EmergencyEvidence(
                event_type='no_movement',
                timestamp=datetime.now(),
                confidence=0.6,
                source='camera',
                details={
                    'duration_hours': duration_hours,
                    'last_room': last_room
                }
            )
        ]
        
        # Context-aware severity
        if is_night and duration_hours < 10 and last_room == 'bedroom':
            # Probably sleeping
            return EmergencyValidation(
                is_emergency=False,
                severity=EmergencySeverity.NONE,
                confidence=0.8,
                evidence=evidence,
                reasoning=f"No movement for {duration_hours}h at night in bedroom - likely sleeping",
                recommended_action="No action needed",
                escalation_level=0
            )
        
        elif is_weekend and duration_hours < 12:
            # Sleeping in on weekend
            return EmergencyValidation(
                is_emergency=False,
                severity=EmergencySeverity.SUSPICIOUS,
                confidence=0.5,
                evidence=evidence,
                reasoning=f"No movement for {duration_hours}h on weekend - possibly sleeping in",
                recommended_action="Monitor, check-in if exceeds 12 hours",
                escalation_level=0
            )
        
        elif duration_hours >= 12:
            # Very long no movement - concerning
            return EmergencyValidation(
                is_emergency=True,
                severity=EmergencySeverity.LIKELY,
                confidence=0.7,
                evidence=evidence,
                reasoning=f"No movement for {duration_hours}h - unusually long",
                recommended_action="CHECK-IN: Ask if user is okay",
                escalation_level=1
            )
        
        else:
            # Moderate concern
            return EmergencyValidation(
                is_emergency=False,
                severity=EmergencySeverity.SUSPICIOUS,
                confidence=0.5,
                evidence=evidence,
                reasoning=f"No movement for {duration_hours}h - monitoring",
                recommended_action="Continue monitoring",
                escalation_level=0
            )
    
    def validate_hr_anomaly(
        self,
        user_id: str,
        hr_event: LifeEvent
    ) -> EmergencyValidation:
        """
        Validate heart rate anomaly with baseline comparison.
        
        Args:
            user_id: User ID
            hr_event: Heart rate event
            
        Returns:
            EmergencyValidation
        """
        current_hr = hr_event.features.get('bpm', 0)
        
        # Get baseline HR
        baseline = self._get_baseline_hr(user_id)
        
        if not baseline:
            # No baseline, can't validate
            return EmergencyValidation(
                is_emergency=False,
                severity=EmergencySeverity.NONE,
                confidence=0.0,
                evidence=[],
                reasoning="No baseline heart rate for comparison",
                recommended_action="Collect more data",
                escalation_level=0
            )
        
        deviation = (current_hr - baseline) / baseline
        
        evidence = [
            EmergencyEvidence(
                event_type='hr_spike',
                timestamp=hr_event.timestamp,
                confidence=0.7,
                source='fitbit',
                details={
                    'current_bpm': current_hr,
                    'baseline_bpm': baseline,
                    'deviation': deviation
                }
            )
        ]
        
        if deviation > 0.5:  # 50% above baseline
            return EmergencyValidation(
                is_emergency=True,
                severity=EmergencySeverity.LIKELY,
                confidence=0.6,
                evidence=evidence,
                reasoning=f"Heart rate {current_hr} bpm is {deviation*100:.0f}% above baseline {baseline} bpm",
                recommended_action="CHECK-IN: Ask if user feels okay",
                escalation_level=1
            )
        else:
            return EmergencyValidation(
                is_emergency=False,
                severity=EmergencySeverity.NONE,
                confidence=0.8,
                evidence=evidence,
                reasoning=f"Heart rate {current_hr} bpm within acceptable range of baseline {baseline} bpm",
                recommended_action="No action needed",
                escalation_level=0
            )
    
    def record_user_response(self, user_id: str, emergency_type: str):
        """Record that user responded to check-in."""
        key = f"{user_id}_{emergency_type}"
        self.user_responses[key] = datetime.now()
        self.escalation_attempts[key] = 0  # Reset escalation
        logger.info(f"[EMERGENCY-VALIDATOR] User {user_id} responded to {emergency_type} check-in")
    
    def record_escalation_attempt(self, user_id: str, emergency_type: str):
        """Record escalation attempt (for tracking non-responses)."""
        key = f"{user_id}_{emergency_type}"
        self.escalation_attempts[key] = self.escalation_attempts.get(key, 0) + 1
        logger.info(
            f"[EMERGENCY-VALIDATOR] Escalation attempt {self.escalation_attempts[key]} "
            f"for {user_id} {emergency_type}"
        )
    
    def _get_recent_falls(self, user_id: str, seconds: float) -> List[LifeEvent]:
        """Get recent fall detection events."""
        return self.timeline.query_by_type(
            user_id,
            EventType.FALL,
            start_time=datetime.now() - timedelta(seconds=seconds)
        )
    
    def _check_heart_rate_spike(
        self,
        user_id: str,
        around_time: datetime,
        window_minutes: int = 5
    ) -> Optional[Dict]:
        """Check if heart rate spiked around given time."""
        hr_events = self.timeline.query_by_type(
            user_id,
            EventType.HEART_RATE,
            start_time=around_time - timedelta(minutes=window_minutes),
            end_time=around_time + timedelta(minutes=window_minutes)
        )
        
        if not hr_events:
            return None
        
        baseline = self._get_baseline_hr(user_id)
        if not baseline:
            return None
        
        for event in hr_events:
            bpm = event.features.get('bpm', 0)
            if bpm > baseline * self.hr_spike_threshold:
                return {
                    'timestamp': event.timestamp,
                    'bpm': bpm,
                    'baseline': baseline
                }
        
        return None
    
    def _check_no_movement_after(
        self,
        user_id: str,
        after_time: datetime,
        minutes: int
    ) -> Optional[Dict]:
        """Check if there's no movement after given time."""
        movement_events = self.timeline.query_by_type(
            user_id,
            EventType.ROOM_ENTER,
            start_time=after_time,
            end_time=after_time + timedelta(minutes=minutes)
        )
        
        if not movement_events:
            duration = (datetime.now() - after_time).total_seconds()
            return {'duration': duration}
        
        return None
    
    def _get_baseline_hr(self, user_id: str) -> Optional[float]:
        """Get baseline heart rate for user."""
        # Get last 24h of HR data
        hr_events = self.timeline.query_by_type(
            user_id,
            EventType.HEART_RATE,
            start_time=datetime.now() - timedelta(hours=24)
        )
        
        if not hr_events:
            return None
        
        bpms = [e.features.get('bpm', 0) for e in hr_events if 'bpm' in e.features]
        
        if not bpms:
            return None
        
        # Use median as baseline (more robust than mean)
        bpms.sort()
        return bpms[len(bpms) // 2]
