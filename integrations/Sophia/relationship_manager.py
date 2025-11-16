"""
Relationship Manager Agent - Track communication, suggest check-ins, remember important dates, detect isolation.

This agent helps maintain healthy relationships by tracking communication patterns,
suggesting timely check-ins, and detecting social isolation.
"""

from typing import List, Dict, Optional, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum


class RelationshipType(Enum):
    """Types of relationships."""
    FAMILY = "family"
    CLOSE_FRIEND = "close_friend"
    FRIEND = "friend"
    COLLEAGUE = "colleague"
    ACQUAINTANCE = "acquaintance"
    ROMANTIC = "romantic"


class CommunicationType(Enum):
    """Types of communication."""
    IN_PERSON = "in_person"
    PHONE_CALL = "phone_call"
    VIDEO_CALL = "video_call"
    TEXT_MESSAGE = "text_message"
    EMAIL = "email"
    SOCIAL_MEDIA = "social_media"


@dataclass
class Person:
    """Represents a person in your network."""
    id: str
    name: str
    relationship_type: RelationshipType
    importance: int = 5  # 1-10 scale
    preferred_communication: Optional[CommunicationType] = None
    birthday: Optional[datetime] = None
    notes: str = ""
    tags: Set[str] = field(default_factory=set)


@dataclass
class Interaction:
    """Records an interaction with someone."""
    timestamp: datetime
    person_id: str
    communication_type: CommunicationType
    duration_minutes: Optional[int] = None
    quality: int = 5  # 1-10 scale (how meaningful was it?)
    initiated_by_you: bool = True
    notes: str = ""


@dataclass
class ImportantDate:
    """Tracks important dates for people."""
    person_id: str
    date: datetime
    event_type: str  # birthday, anniversary, etc.
    recurring: bool = True
    notes: str = ""


@dataclass
class CheckInSuggestion:
    """Suggests checking in with someone."""
    person_id: str
    person_name: str
    reason: str
    priority: int  # 1-10
    days_since_contact: int
    suggested_method: CommunicationType


class RelationshipManager:
    """
    Relationship Manager Agent that helps maintain healthy social connections.
    
    Features:
    - Track communication frequency with each person
    - Suggest timely check-ins based on relationship importance
    - Remember and remind about important dates
    - Detect social isolation patterns
    - Analyze relationship health
    """
    
    def __init__(self):
        self.people: Dict[str, Person] = {}
        self.interactions: List[Interaction] = []
        self.important_dates: List[ImportantDate] = []
        
        # Configuration
        self.check_in_intervals = {
            RelationshipType.ROMANTIC: 1,  # days
            RelationshipType.FAMILY: 7,
            RelationshipType.CLOSE_FRIEND: 14,
            RelationshipType.FRIEND: 30,
            RelationshipType.COLLEAGUE: 60,
            RelationshipType.ACQUAINTANCE: 90,
        }
    
    # ============================================================================
    # PERSON MANAGEMENT
    # ============================================================================
    
    def add_person(self, person: Person) -> None:
        """Add a person to your network."""
        self.people[person.id] = person
        
        # Auto-add birthday if provided
        if person.birthday:
            self.important_dates.append(ImportantDate(
                person_id=person.id,
                date=person.birthday,
                event_type="birthday",
                recurring=True
            ))
    
    def update_person(self, person_id: str, **kwargs) -> None:
        """Update person information."""
        if person_id in self.people:
            person = self.people[person_id]
            for key, value in kwargs.items():
                if hasattr(person, key):
                    setattr(person, key, value)
    
    def get_person(self, person_id: str) -> Optional[Person]:
        """Get person by ID."""
        return self.people.get(person_id)
    
    # ============================================================================
    # INTERACTION TRACKING
    # ============================================================================
    
    def log_interaction(self, interaction: Interaction) -> None:
        """Log an interaction with someone."""
        self.interactions.append(interaction)
    
    def get_last_interaction(self, person_id: str) -> Optional[Interaction]:
        """Get the most recent interaction with a person."""
        person_interactions = [i for i in self.interactions if i.person_id == person_id]
        if person_interactions:
            return max(person_interactions, key=lambda x: x.timestamp)
        return None
    
    def get_interaction_history(self, person_id: str, days: int = 90) -> List[Interaction]:
        """Get interaction history with a person."""
        cutoff = datetime.now() - timedelta(days=days)
        return [i for i in self.interactions 
                if i.person_id == person_id and i.timestamp > cutoff]
    
    def get_communication_frequency(self, person_id: str, days: int = 90) -> Dict:
        """Analyze communication frequency with a person."""
        history = self.get_interaction_history(person_id, days)
        
        if not history:
            return {
                'total_interactions': 0,
                'interactions_per_week': 0,
                'avg_quality': 0,
                'last_contact': None
            }
        
        # Calculate metrics
        total = len(history)
        weeks = days / 7
        per_week = total / weeks
        
        qualities = [i.quality for i in history if i.quality]
        avg_quality = sum(qualities) / len(qualities) if qualities else 0
        
        last_contact = max(history, key=lambda x: x.timestamp).timestamp
        
        # Communication type breakdown
        type_counts = {}
        for interaction in history:
            comm_type = interaction.communication_type.value
            type_counts[comm_type] = type_counts.get(comm_type, 0) + 1
        
        return {
            'total_interactions': total,
            'interactions_per_week': round(per_week, 1),
            'avg_quality': round(avg_quality, 1),
            'last_contact': last_contact,
            'days_since_contact': (datetime.now() - last_contact).days,
            'communication_breakdown': type_counts
        }
    
    # ============================================================================
    # CHECK-IN SUGGESTIONS
    # ============================================================================
    
    def get_check_in_suggestions(self, limit: int = 10) -> List[CheckInSuggestion]:
        """
        Get prioritized list of people to check in with.
        
        Considers:
        - Time since last contact
        - Relationship importance
        - Relationship type
        - Communication patterns
        """
        suggestions = []
        
        for person_id, person in self.people.items():
            last_interaction = self.get_last_interaction(person_id)
            
            if last_interaction:
                days_since = (datetime.now() - last_interaction.timestamp).days
            else:
                days_since = 999  # Never contacted
            
            # Get expected interval for this relationship type
            expected_interval = self.check_in_intervals.get(person.relationship_type, 30)
            
            # Calculate priority
            # Higher if: overdue, high importance, long time since contact
            overdue_factor = max(0, days_since - expected_interval) / expected_interval
            priority = (person.importance * 0.5) + (overdue_factor * 5)
            
            # Only suggest if overdue or approaching due date
            if days_since >= expected_interval * 0.8:
                suggestions.append(CheckInSuggestion(
                    person_id=person_id,
                    person_name=person.name,
                    reason=self._generate_check_in_reason(person, days_since, expected_interval),
                    priority=min(10, int(priority)),
                    days_since_contact=days_since,
                    suggested_method=person.preferred_communication or CommunicationType.TEXT_MESSAGE
                ))
        
        # Sort by priority
        suggestions.sort(key=lambda x: x.priority, reverse=True)
        return suggestions[:limit]
    
    def _generate_check_in_reason(self, person: Person, days_since: int, expected_interval: int) -> str:
        """Generate a reason for the check-in suggestion."""
        if days_since > expected_interval * 2:
            return f"It's been {days_since} days - much longer than usual!"
        elif days_since > expected_interval:
            return f"It's been {days_since} days since you last connected"
        else:
            return f"Good time for a regular check-in ({days_since} days)"
    
    # ============================================================================
    # IMPORTANT DATES
    # ============================================================================
    
    def add_important_date(self, date: ImportantDate) -> None:
        """Add an important date."""
        self.important_dates.append(date)
    
    def get_upcoming_dates(self, days_ahead: int = 30) -> List[Dict]:
        """Get important dates coming up."""
        upcoming = []
        now = datetime.now()
        
        for date_info in self.important_dates:
            # Handle recurring dates (like birthdays)
            if date_info.recurring:
                # Get this year's occurrence
                this_year = date_info.date.replace(year=now.year)
                next_year = date_info.date.replace(year=now.year + 1)
                
                for occurrence in [this_year, next_year]:
                    days_until = (occurrence - now).days
                    if 0 <= days_until <= days_ahead:
                        person = self.people.get(date_info.person_id)
                        upcoming.append({
                            'person_id': date_info.person_id,
                            'person_name': person.name if person else 'Unknown',
                            'date': occurrence,
                            'days_until': days_until,
                            'event_type': date_info.event_type,
                            'notes': date_info.notes
                        })
            else:
                # Non-recurring date
                days_until = (date_info.date - now).days
                if 0 <= days_until <= days_ahead:
                    person = self.people.get(date_info.person_id)
                    upcoming.append({
                        'person_id': date_info.person_id,
                        'person_name': person.name if person else 'Unknown',
                        'date': date_info.date,
                        'days_until': days_until,
                        'event_type': date_info.event_type,
                        'notes': date_info.notes
                    })
        
        # Sort by date
        upcoming.sort(key=lambda x: x['days_until'])
        return upcoming
    
    # ============================================================================
    # SOCIAL ISOLATION DETECTION
    # ============================================================================
    
    def detect_isolation_patterns(self, days: int = 30) -> Dict:
        """
        Detect patterns of social isolation.
        
        Warning signs:
        - Declining interaction frequency
        - Low quality interactions
        - Avoiding in-person contact
        - Not initiating contact
        """
        cutoff = datetime.now() - timedelta(days=days)
        recent_interactions = [i for i in self.interactions if i.timestamp > cutoff]
        
        # Calculate metrics
        total_interactions = len(recent_interactions)
        interactions_per_week = total_interactions / (days / 7)
        
        # Quality analysis
        qualities = [i.quality for i in recent_interactions if i.quality]
        avg_quality = sum(qualities) / len(qualities) if qualities else 0
        
        # In-person contact
        in_person = [i for i in recent_interactions 
                    if i.communication_type == CommunicationType.IN_PERSON]
        in_person_percentage = (len(in_person) / total_interactions * 100) if total_interactions else 0
        
        # Initiation analysis
        initiated_by_you = [i for i in recent_interactions if i.initiated_by_you]
        initiation_rate = (len(initiated_by_you) / total_interactions * 100) if total_interactions else 0
        
        # Relationship diversity
        unique_people = len(set(i.person_id for i in recent_interactions))
        
        # Detect warning signs
        warnings = []
        isolation_score = 0
        
        if interactions_per_week < 3:
            warnings.append("⚠️ Low social interaction frequency (< 3 per week)")
            isolation_score += 3
        
        if avg_quality < 5:
            warnings.append("⚠️ Low quality interactions (avg < 5/10)")
            isolation_score += 2
        
        if in_person_percentage < 20 and total_interactions > 0:
            warnings.append("⚠️ Very little in-person contact (< 20%)")
            isolation_score += 2
        
        if initiation_rate < 30 and total_interactions > 0:
            warnings.append("⚠️ Rarely initiating contact (< 30%)")
            isolation_score += 2
        
        if unique_people < 3:
            warnings.append("⚠️ Limited social circle (< 3 people)")
            isolation_score += 1
        
        # Compare to previous period
        previous_cutoff = cutoff - timedelta(days=days)
        previous_interactions = [i for i in self.interactions 
                                if previous_cutoff < i.timestamp < cutoff]
        
        if len(previous_interactions) > len(recent_interactions) * 1.5:
            warnings.append("⚠️ Declining social activity (50% drop from previous period)")
            isolation_score += 3
        
        # Determine isolation level
        if isolation_score >= 8:
            isolation_level = "SEVERE"
        elif isolation_score >= 5:
            isolation_level = "MODERATE"
        elif isolation_score >= 2:
            isolation_level = "MILD"
        else:
            isolation_level = "HEALTHY"
        
        return {
            'isolation_level': isolation_level,
            'isolation_score': isolation_score,
            'interactions_per_week': round(interactions_per_week, 1),
            'avg_quality': round(avg_quality, 1),
            'in_person_percentage': round(in_person_percentage, 1),
            'initiation_rate': round(initiation_rate, 1),
            'unique_people_contacted': unique_people,
            'warnings': warnings,
            'recommendations': self._generate_isolation_recommendations(isolation_level, warnings)
        }
    
    def _generate_isolation_recommendations(self, level: str, warnings: List[str]) -> List[str]:
        """Generate recommendations based on isolation level."""
        recs = []
        
        if level == "SEVERE":
            recs.extend([
                "🔴 URGENT: Consider talking to a mental health professional",
                "Reach out to at least one close friend or family member today",
                "Join a group activity or class this week",
                "Schedule regular social commitments (weekly coffee, game night, etc.)"
            ])
        elif level == "MODERATE":
            recs.extend([
                "🟡 Schedule at least 2-3 social activities this week",
                "Reach out to friends you haven't seen in a while",
                "Try to have at least one in-person interaction per week",
                "Join a club, class, or group related to your interests"
            ])
        elif level == "MILD":
            recs.extend([
                "Consider increasing social activities slightly",
                "Mix in more in-person interactions with digital ones",
                "Take initiative to reach out to others more often"
            ])
        else:
            recs.append("✅ Your social connections look healthy! Keep it up.")
        
        # Specific recommendations based on warnings
        if any("in-person" in w for w in warnings):
            recs.append("Prioritize face-to-face meetings over digital communication")
        
        if any("initiating" in w for w in warnings):
            recs.append("Take the initiative - don't wait for others to reach out first")
        
        if any("quality" in w for w in warnings):
            recs.append("Focus on deeper, more meaningful conversations")
        
        return recs[:5]
    
    # ============================================================================
    # RELATIONSHIP HEALTH ANALYSIS
    # ============================================================================
    
    def analyze_relationship_health(self, person_id: str) -> Dict:
        """Analyze the health of a specific relationship."""
        person = self.people.get(person_id)
        if not person:
            return {'error': 'Person not found'}
        
        freq_data = self.get_communication_frequency(person_id, days=90)
        expected_interval = self.check_in_intervals.get(person.relationship_type, 30)
        
        # Calculate health score (0-100)
        health_score = 100
        
        # Frequency factor
        if freq_data['days_since_contact'] > expected_interval * 2:
            health_score -= 40
        elif freq_data['days_since_contact'] > expected_interval:
            health_score -= 20
        
        # Quality factor
        if freq_data['avg_quality'] < 5:
            health_score -= 20
        elif freq_data['avg_quality'] < 7:
            health_score -= 10
        
        # Consistency factor
        if freq_data['interactions_per_week'] < 0.5:
            health_score -= 20
        
        health_score = max(0, health_score)
        
        # Determine status
        if health_score >= 80:
            status = "STRONG"
        elif health_score >= 60:
            status = "HEALTHY"
        elif health_score >= 40:
            status = "NEEDS_ATTENTION"
        else:
            status = "AT_RISK"
        
        return {
            'person_name': person.name,
            'relationship_type': person.relationship_type.value,
            'health_score': health_score,
            'status': status,
            'days_since_contact': freq_data['days_since_contact'],
            'expected_interval': expected_interval,
            'avg_interaction_quality': freq_data['avg_quality'],
            'recommendations': self._generate_relationship_recommendations(person, freq_data, status)
        }
    
    def _generate_relationship_recommendations(self, person: Person, freq_data: Dict, status: str) -> List[str]:
        """Generate recommendations for a specific relationship."""
        recs = []
        
        if status == "AT_RISK":
            recs.append(f"🔴 URGENT: Reach out to {person.name} soon - it's been {freq_data['days_since_contact']} days")
            recs.append("Consider scheduling a meaningful in-person meeting")
        elif status == "NEEDS_ATTENTION":
            recs.append(f"🟡 Check in with {person.name} this week")
            recs.append("Try to increase interaction frequency")
        
        # Quality recommendations
        if freq_data['avg_quality'] < 6:
            recs.append("Focus on deeper, more meaningful interactions")
            recs.append("Ask about what's really going on in their life")
        
        # Communication method recommendations
        comm_breakdown = freq_data.get('communication_breakdown', {})
        if comm_breakdown and 'in_person' not in comm_breakdown:
            recs.append("Try to meet in person - it strengthens connections")
        
        return recs[:4]
    
    def get_relationship_report(self) -> Dict:
        """Generate comprehensive relationship report."""
        # Overall stats
        total_people = len(self.people)
        total_interactions_30d = len([i for i in self.interactions 
                                     if i.timestamp > datetime.now() - timedelta(days=30)])
        
        # Relationship health breakdown
        health_breakdown = {
            'STRONG': 0,
            'HEALTHY': 0,
            'NEEDS_ATTENTION': 0,
            'AT_RISK': 0
        }
        
        for person_id in self.people.keys():
            analysis = self.analyze_relationship_health(person_id)
            status = analysis.get('status', 'UNKNOWN')
            if status in health_breakdown:
                health_breakdown[status] += 1
        
        # Check-in suggestions
        suggestions = self.get_check_in_suggestions(5)
        
        # Upcoming dates
        upcoming = self.get_upcoming_dates(14)
        
        # Isolation check
        isolation = self.detect_isolation_patterns(30)
        
        return {
            'total_people': total_people,
            'interactions_last_30_days': total_interactions_30d,
            'relationship_health': health_breakdown,
            'top_check_in_suggestions': [
                {'name': s.person_name, 'reason': s.reason, 'priority': s.priority}
                for s in suggestions
            ],
            'upcoming_important_dates': upcoming[:5],
            'isolation_assessment': {
                'level': isolation['isolation_level'],
                'score': isolation['isolation_score'],
                'warnings': isolation['warnings']
            }
        }


if __name__ == "__main__":
    # Demo usage
    manager = RelationshipManager()
    
    # Add people
    manager.add_person(Person(
        id="1",
        name="Mom",
        relationship_type=RelationshipType.FAMILY,
        importance=10,
        preferred_communication=CommunicationType.PHONE_CALL,
        birthday=datetime(1960, 5, 15)
    ))
    
    manager.add_person(Person(
        id="2",
        name="Best Friend",
        relationship_type=RelationshipType.CLOSE_FRIEND,
        importance=9,
        preferred_communication=CommunicationType.TEXT_MESSAGE
    ))
    
    # Log interactions
    manager.log_interaction(Interaction(
        timestamp=datetime.now() - timedelta(days=3),
        person_id="1",
        communication_type=CommunicationType.PHONE_CALL,
        duration_minutes=30,
        quality=8,
        initiated_by_you=True
    ))
    
    manager.log_interaction(Interaction(
        timestamp=datetime.now() - timedelta(days=20),
        person_id="2",
        communication_type=CommunicationType.TEXT_MESSAGE,
        duration_minutes=10,
        quality=6,
        initiated_by_you=False
    ))
    
    # Get report
    print("=== RELATIONSHIP REPORT ===")
    report = manager.get_relationship_report()
    
    print(f"\nTotal People: {report['total_people']}")
    print(f"Interactions (30d): {report['interactions_last_30_days']}")
    
    print("\nRelationship Health:")
    for status, count in report['relationship_health'].items():
        print(f"  {status}: {count}")
    
    print("\nCheck-In Suggestions:")
    for suggestion in report['top_check_in_suggestions']:
        print(f"  - {suggestion['name']}: {suggestion['reason']} (Priority: {suggestion['priority']})")
    
    print("\nIsolation Assessment:")
    print(f"  Level: {report['isolation_assessment']['level']}")
    print(f"  Score: {report['isolation_assessment']['score']}")
