"""
Creative Catalyst Agent - Suggests creative time blocks, tracks creative output, detects slumps, delivers inspiration.

This agent helps maintain and boost your creative practice by optimizing creative time,
tracking output, detecting creative blocks, and providing timely inspiration.
"""

from typing import List, Dict, Optional, Set
from datetime import datetime, timedelta, time
from dataclasses import dataclass, field
from enum import Enum
import statistics
import random


class CreativeField(Enum):
    """Types of creative work."""
    WRITING = "writing"
    MUSIC = "music"
    VISUAL_ART = "visual_art"
    DESIGN = "design"
    PHOTOGRAPHY = "photography"
    VIDEO = "video"
    CODING = "coding"
    CRAFTS = "crafts"
    OTHER = "other"


class CreativePhase(Enum):
    """Phases of creative process."""
    IDEATION = "ideation"
    DRAFTING = "drafting"
    REFINEMENT = "refinement"
    COMPLETION = "completion"


class MoodState(Enum):
    """Mood during creative work."""
    INSPIRED = "inspired"
    FOCUSED = "focused"
    STRUGGLING = "struggling"
    BLOCKED = "blocked"
    FLOWING = "flowing"


@dataclass
class CreativeProject:
    """Represents a creative project."""
    id: str
    title: str
    field: CreativeField
    phase: CreativePhase
    started: datetime
    deadline: Optional[datetime] = None
    completed: bool = False
    description: str = ""
    tags: Set[str] = field(default_factory=set)


@dataclass
class CreativeSession:
    """Records a creative work session."""
    timestamp: datetime
    project_id: Optional[str]
    field: CreativeField
    duration_minutes: int
    output_count: int = 0  # words, measures, sketches, etc.
    mood: MoodState = MoodState.FOCUSED
    breakthrough: bool = False
    notes: str = ""


@dataclass
class CreativeBlock:
    """Records a creative block or slump."""
    detected_date: datetime
    field: CreativeField
    duration_days: int
    severity: int  # 1-10
    possible_causes: List[str] = field(default_factory=list)
    resolved: bool = False


@dataclass
class Inspiration:
    """Represents an inspiration item."""
    id: str
    content: str
    source: str
    field: CreativeField
    tags: Set[str] = field(default_factory=set)
    saved_date: datetime = field(default_factory=datetime.now)
    used: bool = False


class CreativeCatalyst:
    """
    Creative Catalyst Agent that optimizes and supports creative work.
    
    Features:
    - Suggest optimal creative time blocks based on productivity patterns
    - Track creative output across different fields
    - Detect creative slumps and blocks
    - Deliver timely inspiration and prompts
    - Analyze creative patterns and provide insights
    """
    
    def __init__(self):
        self.projects: Dict[str, CreativeProject] = {}
        self.sessions: List[CreativeSession] = []
        self.blocks: List[CreativeBlock] = []
        self.inspiration_library: Dict[str, Inspiration] = {}
        
        # Creative preferences
        self.preferred_creative_times: List[Tuple[time, time]] = [
            (time(6, 0), time(9, 0)),   # Early morning
            (time(22, 0), time(24, 0))  # Late night
        ]
        self.target_weekly_hours: float = 10.0
        self.primary_fields: List[CreativeField] = [CreativeField.WRITING]
    
    # ============================================================================
    # PROJECT MANAGEMENT
    # ============================================================================
    
    def add_project(self, project: CreativeProject) -> None:
        """Add a creative project."""
        self.projects[project.id] = project
    
    def update_project_phase(self, project_id: str, new_phase: CreativePhase) -> None:
        """Update project phase."""
        if project_id in self.projects:
            self.projects[project_id].phase = new_phase
    
    def complete_project(self, project_id: str) -> None:
        """Mark project as completed."""
        if project_id in self.projects:
            self.projects[project_id].completed = True
    
    def get_active_projects(self) -> List[CreativeProject]:
        """Get all active (non-completed) projects."""
        return [p for p in self.projects.values() if not p.completed]
    
    # ============================================================================
    # SESSION TRACKING
    # ============================================================================
    
    def log_session(self, session: CreativeSession) -> None:
        """Log a creative session."""
        self.sessions.append(session)
        
        # Check if this resolves a creative block
        self._check_block_resolution(session)
    
    def get_creative_output(self, days: int = 30) -> Dict:
        """
        Analyze creative output over the last N days.
        
        Returns metrics about productivity, consistency, and quality.
        """
        cutoff = datetime.now() - timedelta(days=days)
        recent_sessions = [s for s in self.sessions if s.timestamp > cutoff]
        
        if not recent_sessions:
            return {'error': 'No creative sessions recorded'}
        
        # Calculate metrics
        total_hours = sum(s.duration_minutes for s in recent_sessions) / 60
        avg_hours_per_week = total_hours / (days / 7)
        total_output = sum(s.output_count for s in recent_sessions)
        
        # Output by field
        field_breakdown = {}
        for session in recent_sessions:
            field = session.field.value
            if field not in field_breakdown:
                field_breakdown[field] = {'hours': 0, 'output': 0, 'sessions': 0}
            field_breakdown[field]['hours'] += session.duration_minutes / 60
            field_breakdown[field]['output'] += session.output_count
            field_breakdown[field]['sessions'] += 1
        
        # Mood analysis
        mood_counts = {}
        for session in recent_sessions:
            mood = session.mood.value
            mood_counts[mood] = mood_counts.get(mood, 0) + 1
        
        # Breakthrough moments
        breakthroughs = len([s for s in recent_sessions if s.breakthrough])
        
        # Consistency (sessions per week)
        sessions_per_week = len(recent_sessions) / (days / 7)
        
        return {
            'total_hours': round(total_hours, 1),
            'avg_hours_per_week': round(avg_hours_per_week, 1),
            'total_sessions': len(recent_sessions),
            'sessions_per_week': round(sessions_per_week, 1),
            'total_output': total_output,
            'field_breakdown': field_breakdown,
            'mood_distribution': mood_counts,
            'breakthrough_moments': breakthroughs,
            'consistency_score': self._calculate_consistency_score(recent_sessions, days),
            'insights': self._generate_output_insights(recent_sessions, avg_hours_per_week, mood_counts)
        }
    
    def _calculate_consistency_score(self, sessions: List[CreativeSession], days: int) -> float:
        """Calculate consistency score (0-100) based on regular practice."""
        if not sessions:
            return 0
        
        # Check how many days had creative work
        session_dates = set(s.timestamp.date() for s in sessions)
        days_with_work = len(session_dates)
        
        # Ideal: work every other day
        ideal_days = days / 2
        consistency = min(days_with_work / ideal_days, 1) * 100
        
        return round(consistency, 1)
    
    def _generate_output_insights(self, 
                                  sessions: List[CreativeSession],
                                  avg_hours_per_week: float,
                                  mood_counts: Dict) -> List[str]:
        """Generate insights about creative output."""
        insights = []
        
        # Volume insights
        if avg_hours_per_week < self.target_weekly_hours * 0.5:
            insights.append(f"⚠️ Low creative time ({avg_hours_per_week:.1f}h/week vs target {self.target_weekly_hours}h)")
        elif avg_hours_per_week >= self.target_weekly_hours:
            insights.append(f"✅ Meeting creative time goals ({avg_hours_per_week:.1f}h/week)")
        
        # Mood insights
        if mood_counts:
            total_sessions = sum(mood_counts.values())
            blocked_sessions = mood_counts.get('blocked', 0) + mood_counts.get('struggling', 0)
            
            if blocked_sessions / total_sessions > 0.3:
                insights.append("⚠️ High proportion of blocked/struggling sessions - may need a break or new approach")
            
            flowing_sessions = mood_counts.get('flowing', 0) + mood_counts.get('inspired', 0)
            if flowing_sessions / total_sessions > 0.5:
                insights.append("✅ Great flow state! You're in a productive creative period")
        
        # Breakthrough insights
        breakthroughs = len([s for s in sessions if s.breakthrough])
        if breakthroughs >= 3:
            insights.append(f"🎉 {breakthroughs} breakthrough moments - you're making real progress!")
        
        return insights
    
    # ============================================================================
    # CREATIVE TIME OPTIMIZATION
    # ============================================================================
    
    def suggest_creative_time_blocks(self, days: int = 7) -> List[Dict]:
        """
        Suggest optimal creative time blocks for the next N days.
        
        Based on:
        - Historical productivity patterns
        - Preferred creative times
        - Current project phases
        - Energy levels
        """
        suggestions = []
        
        # Analyze when you're most productive
        best_times = self._analyze_productive_times()
        
        # Get active projects
        active_projects = self.get_active_projects()
        
        for day_offset in range(days):
            date = datetime.now() + timedelta(days=day_offset)
            day_name = date.strftime('%A')
            
            # Suggest 1-2 creative blocks per day
            for time_slot in best_times[:2]:
                # Pick a project to work on
                project = None
                if active_projects:
                    # Prioritize projects with deadlines
                    deadline_projects = [p for p in active_projects if p.deadline]
                    if deadline_projects:
                        project = min(deadline_projects, key=lambda p: p.deadline)
                    else:
                        project = active_projects[0]
                
                suggestions.append({
                    'date': date.strftime('%Y-%m-%d'),
                    'day': day_name,
                    'time_slot': time_slot,
                    'duration_minutes': 90,  # 90-minute focused sessions
                    'project': project.title if project else 'Free exploration',
                    'suggested_activity': self._suggest_activity(project) if project else 'Experiment with new ideas',
                    'field': project.field.value if project else 'any'
                })
        
        return suggestions
    
    def _analyze_productive_times(self) -> List[str]:
        """Analyze when creative sessions are most productive."""
        if not self.sessions:
            # Return default preferred times
            return [f"{start.strftime('%H:%M')}-{end.strftime('%H:%M')}" 
                   for start, end in self.preferred_creative_times]
        
        # Analyze sessions by hour
        hour_productivity = {}
        for session in self.sessions:
            hour = session.timestamp.hour
            if hour not in hour_productivity:
                hour_productivity[hour] = {'count': 0, 'total_output': 0, 'good_mood': 0}
            
            hour_productivity[hour]['count'] += 1
            hour_productivity[hour]['total_output'] += session.output_count
            
            if session.mood in [MoodState.FLOWING, MoodState.INSPIRED]:
                hour_productivity[hour]['good_mood'] += 1
        
        # Score each hour
        hour_scores = []
        for hour, data in hour_productivity.items():
            score = (data['total_output'] * 0.5) + (data['good_mood'] * 2)
            hour_scores.append((hour, score))
        
        # Get top 3 hours
        hour_scores.sort(key=lambda x: x[1], reverse=True)
        top_hours = [h for h, _ in hour_scores[:3]]
        
        # Convert to time slots
        return [f"{h:02d}:00-{(h+2):02d}:00" for h in top_hours]
    
    def _suggest_activity(self, project: CreativeProject) -> str:
        """Suggest activity based on project phase."""
        activities = {
            CreativePhase.IDEATION: "Brainstorm and explore new directions",
            CreativePhase.DRAFTING: "Create first draft without self-editing",
            CreativePhase.REFINEMENT: "Polish and improve existing work",
            CreativePhase.COMPLETION: "Final touches and prepare for sharing"
        }
        return activities.get(project.phase, "Work on project")
    
    # ============================================================================
    # CREATIVE BLOCK DETECTION
    # ============================================================================
    
    def detect_creative_slumps(self) -> List[CreativeBlock]:
        """
        Detect creative slumps and blocks.
        
        Indicators:
        - No sessions for extended period
        - Declining output
        - Frequent blocked/struggling moods
        - No breakthrough moments
        """
        blocks = []
        
        # Check each creative field
        for field in self.primary_fields:
            field_sessions = [s for s in self.sessions if s.field == field]
            
            if not field_sessions:
                continue
            
            # Check for gaps in activity
            last_session = max(field_sessions, key=lambda s: s.timestamp)
            days_since = (datetime.now() - last_session.timestamp).days
            
            if days_since > 14:  # No activity for 2 weeks
                blocks.append(CreativeBlock(
                    detected_date=datetime.now(),
                    field=field,
                    duration_days=days_since,
                    severity=min(10, days_since // 2),
                    possible_causes=["Extended break", "Loss of motivation", "External pressures"]
                ))
            
            # Check recent sessions for struggling patterns
            recent_cutoff = datetime.now() - timedelta(days=30)
            recent_sessions = [s for s in field_sessions if s.timestamp > recent_cutoff]
            
            if recent_sessions:
                struggling_count = len([s for s in recent_sessions 
                                       if s.mood in [MoodState.BLOCKED, MoodState.STRUGGLING]])
                
                if struggling_count / len(recent_sessions) > 0.5:
                    blocks.append(CreativeBlock(
                        detected_date=datetime.now(),
                        field=field,
                        duration_days=30,
                        severity=7,
                        possible_causes=["Creative burnout", "Wrong approach", "Need new inspiration"],
                        resolved=False
                    ))
                
                # Check for declining output
                if len(recent_sessions) >= 5:
                    first_half = recent_sessions[:len(recent_sessions)//2]
                    second_half = recent_sessions[len(recent_sessions)//2:]
                    
                    avg_output_first = statistics.mean(s.output_count for s in first_half)
                    avg_output_second = statistics.mean(s.output_count for s in second_half)
                    
                    if avg_output_second < avg_output_first * 0.5:  # 50% decline
                        blocks.append(CreativeBlock(
                            detected_date=datetime.now(),
                            field=field,
                            duration_days=15,
                            severity=6,
                            possible_causes=["Declining productivity", "Perfectionism", "Fatigue"]
                        ))
        
        self.blocks.extend(blocks)
        return blocks
    
    def _check_block_resolution(self, session: CreativeSession) -> None:
        """Check if a session resolves any active blocks."""
        for block in self.blocks:
            if not block.resolved and block.field == session.field:
                # Good session after a block
                if session.mood in [MoodState.FLOWING, MoodState.INSPIRED] and session.output_count > 0:
                    block.resolved = True
    
    def get_block_recovery_suggestions(self, block: CreativeBlock) -> List[str]:
        """Get suggestions for overcoming a creative block."""
        suggestions = []
        
        if block.severity >= 8:
            suggestions.extend([
                "🔴 SEVERE BLOCK: Take a complete break for 3-7 days",
                "Engage in different creative activities (cross-pollination)",
                "Consume inspiring work in your field (books, films, art)",
                "Talk to other creators about their process"
            ])
        elif block.severity >= 5:
            suggestions.extend([
                "🟡 MODERATE BLOCK: Try a different approach or medium",
                "Set smaller, achievable goals",
                "Work on a completely different project",
                "Change your environment (coffee shop, park, library)"
            ])
        else:
            suggestions.extend([
                "🟢 MILD SLUMP: Push through with structured practice",
                "Use creative prompts and constraints",
                "Collaborate with others",
                "Review past successful work for motivation"
            ])
        
        # Field-specific suggestions
        if block.field == CreativeField.WRITING:
            suggestions.extend([
                "Try freewriting for 10 minutes without stopping",
                "Use writing prompts or story generators",
                "Read work by authors you admire"
            ])
        elif block.field == CreativeField.MUSIC:
            suggestions.extend([
                "Improvise without recording",
                "Learn a song you love",
                "Collaborate with other musicians"
            ])
        elif block.field == CreativeField.VISUAL_ART:
            suggestions.extend([
                "Try a new medium or technique",
                "Do observational sketches",
                "Visit galleries or browse art online"
            ])
        
        return suggestions[:7]
    
    # ============================================================================
    # INSPIRATION DELIVERY
    # ============================================================================
    
    def add_inspiration(self, inspiration: Inspiration) -> None:
        """Add an inspiration item to the library."""
        self.inspiration_library[inspiration.id] = inspiration
    
    def get_inspiration(self, 
                       field: Optional[CreativeField] = None,
                       tags: Optional[Set[str]] = None,
                       random_pick: bool = True) -> Optional[Inspiration]:
        """
        Get inspiration from the library.
        
        Can filter by field and tags, or get random inspiration.
        """
        # Filter inspiration
        filtered = list(self.inspiration_library.values())
        
        if field:
            filtered = [i for i in filtered if i.field == field]
        
        if tags:
            filtered = [i for i in filtered if i.tags.intersection(tags)]
        
        # Prefer unused inspiration
        unused = [i for i in filtered if not i.used]
        if unused:
            filtered = unused
        
        if not filtered:
            return None
        
        if random_pick:
            return random.choice(filtered)
        else:
            return filtered[0]
    
    def get_daily_inspiration(self) -> Dict:
        """Get daily inspiration package."""
        inspiration_package = {
            'quote': self._get_creative_quote(),
            'prompt': self._get_creative_prompt(),
            'challenge': self._get_creative_challenge(),
            'saved_inspiration': None
        }
        
        # Add saved inspiration if available
        saved = self.get_inspiration(random_pick=True)
        if saved:
            inspiration_package['saved_inspiration'] = {
                'content': saved.content,
                'source': saved.source,
                'field': saved.field.value
            }
        
        return inspiration_package
    
    def _get_creative_quote(self) -> str:
        """Get a random creative quote."""
        quotes = [
            "The secret of getting ahead is getting started. - Mark Twain",
            "Creativity is intelligence having fun. - Albert Einstein",
            "You can't use up creativity. The more you use, the more you have. - Maya Angelou",
            "The worst enemy to creativity is self-doubt. - Sylvia Plath",
            "Creativity takes courage. - Henri Matisse",
            "Every artist was first an amateur. - Ralph Waldo Emerson",
            "Art is never finished, only abandoned. - Leonardo da Vinci",
            "The desire to create is one of the deepest yearnings of the human soul. - Dieter F. Uchtdorf",
            "Creativity is contagious. Pass it on. - Albert Einstein",
            "Don't think. Thinking is the enemy of creativity. - Ray Bradbury"
        ]
        return random.choice(quotes)
    
    def _get_creative_prompt(self) -> str:
        """Get a random creative prompt."""
        prompts = [
            "Create something inspired by your childhood",
            "Combine two unrelated concepts",
            "Work in a medium you've never tried before",
            "Create something in exactly 15 minutes",
            "Use only three colors/notes/words",
            "Tell a story backwards",
            "Create something ugly on purpose, then make it beautiful",
            "Collaborate with randomness (dice, random words, etc.)",
            "Recreate a favorite work in your own style",
            "Express a complex emotion without words"
        ]
        return random.choice(prompts)
    
    def _get_creative_challenge(self) -> str:
        """Get a creative challenge."""
        challenges = [
            "30-day daily practice challenge",
            "Create 100 variations of one idea",
            "Finish one project before starting another",
            "Share your work publicly this week",
            "Teach someone your creative skill",
            "Create something every day for 7 days",
            "Collaborate with another creator",
            "Enter a competition or submit to a publication",
            "Create a series of related works",
            "Document your creative process"
        ]
        return random.choice(challenges)
    
    # ============================================================================
    # COMPREHENSIVE REPORT
    # ============================================================================
    
    def get_creative_report(self, days: int = 30) -> Dict:
        """Generate comprehensive creative report."""
        output = self.get_creative_output(days)
        blocks = self.detect_creative_slumps()
        active_projects = self.get_active_projects()
        
        # Calculate creative health score
        health_score = self._calculate_creative_health_score(output, blocks)
        
        return {
            'creative_output': output,
            'active_projects': len(active_projects),
            'projects_by_phase': self._count_projects_by_phase(active_projects),
            'creative_blocks': len([b for b in blocks if not b.resolved]),
            'resolved_blocks': len([b for b in blocks if b.resolved]),
            'creative_health_score': health_score,
            'time_block_suggestions': self.suggest_creative_time_blocks(7)[:3],
            'daily_inspiration': self.get_daily_inspiration(),
            'recommendations': self._generate_creative_recommendations(output, blocks, health_score)
        }
    
    def _count_projects_by_phase(self, projects: List[CreativeProject]) -> Dict[str, int]:
        """Count projects by phase."""
        counts = {phase.value: 0 for phase in CreativePhase}
        for project in projects:
            counts[project.phase.value] += 1
        return counts
    
    def _calculate_creative_health_score(self, output: Dict, blocks: List[CreativeBlock]) -> float:
        """Calculate creative health score (0-100)."""
        if 'error' in output:
            return 0
        
        score = 0
        
        # Consistency (0-30 points)
        consistency = output.get('consistency_score', 0)
        score += consistency * 0.3
        
        # Volume (0-25 points)
        avg_hours = output.get('avg_hours_per_week', 0)
        volume_score = min(avg_hours / self.target_weekly_hours, 1) * 25
        score += volume_score
        
        # Mood (0-25 points)
        mood_dist = output.get('mood_distribution', {})
        if mood_dist:
            total = sum(mood_dist.values())
            positive_moods = mood_dist.get('flowing', 0) + mood_dist.get('inspired', 0)
            mood_score = (positive_moods / total) * 25
            score += mood_score
        
        # Breakthroughs (0-10 points)
        breakthroughs = output.get('breakthrough_moments', 0)
        score += min(breakthroughs * 2, 10)
        
        # Blocks penalty (0-10 points deduction)
        active_blocks = len([b for b in blocks if not b.resolved])
        score -= min(active_blocks * 3, 10)
        
        return max(0, min(100, round(score, 1)))
    
    def _generate_creative_recommendations(self, 
                                          output: Dict,
                                          blocks: List[CreativeBlock],
                                          health_score: float) -> List[str]:
        """Generate personalized creative recommendations."""
        recs = []
        
        # Health score based
        if health_score >= 80:
            recs.append("✅ Excellent creative health! Keep up the momentum")
        elif health_score >= 60:
            recs.append("🟢 Good creative practice. Push for more consistency")
        elif health_score >= 40:
            recs.append("🟡 Creative practice needs attention. Increase frequency")
        else:
            recs.append("🔴 Low creative activity. Start with small, daily practice")
        
        # Block recommendations
        active_blocks = [b for b in blocks if not b.resolved]
        if active_blocks:
            most_severe = max(active_blocks, key=lambda b: b.severity)
            recs.extend(self.get_block_recovery_suggestions(most_severe)[:2])
        
        # Output recommendations
        if 'error' not in output:
            if output.get('avg_hours_per_week', 0) < self.target_weekly_hours * 0.5:
                recs.append("Schedule dedicated creative time blocks this week")
            
            consistency = output.get('consistency_score', 0)
            if consistency < 50:
                recs.append("Focus on consistency - even 15 minutes daily is better than sporadic long sessions")
        
        # General recommendations
        recs.extend([
            "Protect your creative time - treat it like an important meeting",
            "Share your work with others for feedback and motivation",
            "Consume great work in your field for inspiration"
        ])
        
        return recs[:7]


if __name__ == "__main__":
    # Demo usage
    catalyst = CreativeCatalyst()
    
    # Add project
    catalyst.add_project(CreativeProject(
        id="1",
        title="Novel Draft",
        field=CreativeField.WRITING,
        phase=CreativePhase.DRAFTING,
        started=datetime.now() - timedelta(days=30),
        deadline=datetime.now() + timedelta(days=90)
    ))
    
    # Log sessions
    catalyst.log_session(CreativeSession(
        timestamp=datetime.now() - timedelta(days=1),
        project_id="1",
        field=CreativeField.WRITING,
        duration_minutes=90,
        output_count=1500,  # words
        mood=MoodState.FLOWING,
        breakthrough=True
    ))
    
    catalyst.log_session(CreativeSession(
        timestamp=datetime.now() - timedelta(days=3),
        project_id="1",
        field=CreativeField.WRITING,
        duration_minutes=60,
        output_count=800,
        mood=MoodState.FOCUSED
    ))
    
    # Add inspiration
    catalyst.add_inspiration(Inspiration(
        id="1",
        content="What if gravity worked in reverse for one hour each day?",
        source="Random thought",
        field=CreativeField.WRITING,
        tags={"sci-fi", "prompt"}
    ))
    
    # Generate report
    print("=== CREATIVE REPORT ===")
    report = catalyst.get_creative_report(30)
    
    if 'error' not in report['creative_output']:
        print(f"Creative Health Score: {report['creative_health_score']}/100")
        print(f"Total Hours: {report['creative_output']['total_hours']}")
        print(f"Active Projects: {report['active_projects']}")
        print(f"Active Blocks: {report['creative_blocks']}")
        
        print("\nDaily Inspiration:")
        print(f"  Quote: {report['daily_inspiration']['quote']}")
        print(f"  Prompt: {report['daily_inspiration']['prompt']}")
        
        print("\nRecommendations:")
        for rec in report['recommendations']:
            print(f"  - {rec}")
