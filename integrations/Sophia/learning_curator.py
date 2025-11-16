"""
Learning Curator Agent - Course recommendations, study schedule optimization, knowledge gap analysis, and reading lists.

This agent helps optimize your learning journey by recommending courses, identifying knowledge gaps,
and creating personalized study schedules.
"""

from typing import List, Dict, Optional, Set, Tuple
from datetime import datetime, timedelta, time
from dataclasses import dataclass, field
from enum import Enum
import statistics


class LearningGoalType(Enum):
    """Types of learning goals."""
    CAREER = "career"
    PERSONAL = "personal"
    ACADEMIC = "academic"
    HOBBY = "hobby"


class SkillLevel(Enum):
    """Skill proficiency levels."""
    BEGINNER = 1
    INTERMEDIATE = 2
    ADVANCED = 3
    EXPERT = 4


class ContentType(Enum):
    """Types of learning content."""
    COURSE = "course"
    BOOK = "book"
    ARTICLE = "article"
    VIDEO = "video"
    PODCAST = "podcast"
    PRACTICE = "practice"
    PROJECT = "project"


class StudySessionQuality(Enum):
    """Quality of study session."""
    EXCELLENT = 5
    GOOD = 4
    FAIR = 3
    POOR = 2
    DISTRACTED = 1


@dataclass
class Skill:
    """Represents a skill to learn or improve."""
    id: str
    name: str
    category: str
    current_level: SkillLevel
    target_level: SkillLevel
    importance: int = 5  # 1-10
    prerequisites: List[str] = field(default_factory=list)
    related_skills: List[str] = field(default_factory=list)


@dataclass
class LearningGoal:
    """Represents a learning goal."""
    id: str
    title: str
    goal_type: LearningGoalType
    skills: List[str]  # Skill IDs
    deadline: Optional[datetime] = None
    priority: int = 5  # 1-10
    motivation: str = ""
    completed: bool = False


@dataclass
class LearningResource:
    """Represents a learning resource."""
    id: str
    title: str
    content_type: ContentType
    skill_id: str
    difficulty: SkillLevel
    estimated_hours: float
    url: Optional[str] = None
    author: str = ""
    rating: Optional[float] = None
    completed: bool = False
    notes: str = ""


@dataclass
class StudySession:
    """Records a study session."""
    timestamp: datetime
    skill_id: str
    resource_id: Optional[str]
    duration_minutes: int
    quality: StudySessionQuality
    topics_covered: List[str] = field(default_factory=list)
    notes: str = ""
    breakthrough: bool = False  # Did you have an "aha!" moment?


@dataclass
class KnowledgeGap:
    """Represents an identified knowledge gap."""
    skill_id: str
    skill_name: str
    gap_description: str
    severity: int  # 1-10
    recommended_resources: List[str] = field(default_factory=list)


class LearningCurator:
    """
    Learning Curator Agent that optimizes your learning journey.
    
    Features:
    - Course recommendations based on goals and current skills
    - Study schedule optimization based on energy and availability
    - Knowledge gap analysis to identify what to learn next
    - Reading list management with prioritization
    - Progress tracking and learning analytics
    """
    
    def __init__(self):
        self.skills: Dict[str, Skill] = {}
        self.goals: Dict[str, LearningGoal] = {}
        self.resources: Dict[str, LearningResource] = {}
        self.study_sessions: List[StudySession] = []
        self.knowledge_gaps: List[KnowledgeGap] = []
        
        # Learning preferences
        self.preferred_study_times: List[Tuple[time, time]] = [
            (time(9, 0), time(11, 0)),  # Morning
            (time(19, 0), time(21, 0))  # Evening
        ]
        self.max_daily_study_hours: float = 3.0
        self.preferred_content_types: List[ContentType] = [ContentType.COURSE, ContentType.BOOK]
    
    # ============================================================================
    # SKILL MANAGEMENT
    # ============================================================================
    
    def add_skill(self, skill: Skill) -> None:
        """Add a skill to track."""
        self.skills[skill.id] = skill
    
    def update_skill_level(self, skill_id: str, new_level: SkillLevel) -> None:
        """Update skill proficiency level."""
        if skill_id in self.skills:
            self.skills[skill_id].current_level = new_level
    
    def get_skill_progress(self, skill_id: str) -> Dict:
        """Get progress information for a skill."""
        if skill_id not in self.skills:
            return {'error': 'Skill not found'}
        
        skill = self.skills[skill_id]
        
        # Calculate progress percentage
        current = skill.current_level.value
        target = skill.target_level.value
        start = 1  # Beginner
        progress = ((current - start) / (target - start) * 100) if target > start else 100
        
        # Get study time for this skill
        skill_sessions = [s for s in self.study_sessions if s.skill_id == skill_id]
        total_hours = sum(s.duration_minutes for s in skill_sessions) / 60
        
        # Get recent sessions (last 30 days)
        cutoff = datetime.now() - timedelta(days=30)
        recent_sessions = [s for s in skill_sessions if s.timestamp > cutoff]
        recent_hours = sum(s.duration_minutes for s in recent_sessions) / 60
        
        # Calculate average quality
        qualities = [s.quality.value for s in skill_sessions if s.quality]
        avg_quality = statistics.mean(qualities) if qualities else 0
        
        return {
            'skill_name': skill.name,
            'current_level': skill.current_level.name,
            'target_level': skill.target_level.name,
            'progress_percentage': round(progress, 1),
            'total_study_hours': round(total_hours, 1),
            'recent_study_hours': round(recent_hours, 1),
            'avg_session_quality': round(avg_quality, 1),
            'total_sessions': len(skill_sessions)
        }
    
    # ============================================================================
    # LEARNING GOALS
    # ============================================================================
    
    def add_goal(self, goal: LearningGoal) -> None:
        """Add a learning goal."""
        self.goals[goal.id] = goal
    
    def analyze_goal_progress(self, goal_id: str) -> Dict:
        """Analyze progress toward a learning goal."""
        if goal_id not in self.goals:
            return {'error': 'Goal not found'}
        
        goal = self.goals[goal_id]
        
        # Calculate skill progress for each skill in goal
        skill_progress = []
        for skill_id in goal.skills:
            if skill_id in self.skills:
                progress = self.get_skill_progress(skill_id)
                skill_progress.append({
                    'skill_name': progress['skill_name'],
                    'progress': progress['progress_percentage']
                })
        
        # Overall progress
        overall_progress = statistics.mean(s['progress'] for s in skill_progress) if skill_progress else 0
        
        # Time analysis
        if goal.deadline:
            days_remaining = (goal.deadline - datetime.now()).days
            on_track = overall_progress >= ((datetime.now() - (goal.deadline - timedelta(days=365))).days / 365 * 100)
        else:
            days_remaining = None
            on_track = None
        
        return {
            'goal_title': goal.title,
            'overall_progress': round(overall_progress, 1),
            'skill_breakdown': skill_progress,
            'days_remaining': days_remaining,
            'on_track': on_track,
            'completed': goal.completed,
            'recommendations': self._generate_goal_recommendations(goal, overall_progress, on_track)
        }
    
    def _generate_goal_recommendations(self, 
                                      goal: LearningGoal,
                                      progress: float,
                                      on_track: Optional[bool]) -> List[str]:
        """Generate recommendations for achieving a learning goal."""
        recs = []
        
        if goal.completed:
            recs.append("🎉 Goal completed! Set a new learning goal to continue growing.")
            return recs
        
        if on_track is False:
            recs.append("⚠️ Behind schedule. Increase study time or adjust deadline.")
        
        if progress < 25:
            recs.append("Focus on foundational skills first - build a strong base")
        elif progress < 50:
            recs.append("Good start! Maintain consistent study schedule")
        elif progress < 75:
            recs.append("Great progress! Focus on advanced topics and practice")
        else:
            recs.append("Almost there! Focus on mastery and real-world application")
        
        # Check for inactive skills
        for skill_id in goal.skills:
            skill_sessions = [s for s in self.study_sessions 
                            if s.skill_id == skill_id 
                            and s.timestamp > datetime.now() - timedelta(days=14)]
            if not skill_sessions:
                skill_name = self.skills[skill_id].name if skill_id in self.skills else "Unknown"
                recs.append(f"Haven't studied {skill_name} in 2 weeks - schedule a session")
        
        return recs[:5]
    
    # ============================================================================
    # RESOURCE MANAGEMENT
    # ============================================================================
    
    def add_resource(self, resource: LearningResource) -> None:
        """Add a learning resource."""
        self.resources[resource.id] = resource
    
    def recommend_resources(self, skill_id: str, limit: int = 5) -> List[LearningResource]:
        """
        Recommend resources for a skill based on:
        - Current skill level
        - Content type preferences
        - Ratings
        - Time commitment
        """
        if skill_id not in self.skills:
            return []
        
        skill = self.skills[skill_id]
        
        # Filter resources for this skill
        skill_resources = [r for r in self.resources.values() 
                          if r.skill_id == skill_id and not r.completed]
        
        # Score each resource
        scored_resources = []
        for resource in skill_resources:
            score = 0
            
            # Match difficulty to current level
            if resource.difficulty == skill.current_level:
                score += 10
            elif resource.difficulty.value == skill.current_level.value + 1:
                score += 8  # Slightly challenging is good
            elif resource.difficulty.value < skill.current_level.value:
                score += 3  # Review material
            
            # Prefer preferred content types
            if resource.content_type in self.preferred_content_types:
                score += 5
            
            # Rating bonus
            if resource.rating:
                score += resource.rating
            
            # Time commitment (prefer shorter for beginners)
            if skill.current_level == SkillLevel.BEGINNER and resource.estimated_hours <= 10:
                score += 3
            
            scored_resources.append((score, resource))
        
        # Sort by score and return top N
        scored_resources.sort(key=lambda x: x[0], reverse=True)
        return [r for _, r in scored_resources[:limit]]
    
    def get_reading_list(self, priority_threshold: int = 5) -> List[Dict]:
        """Get prioritized reading list (books and articles)."""
        reading_resources = [r for r in self.resources.values() 
                           if r.content_type in [ContentType.BOOK, ContentType.ARTICLE]
                           and not r.completed]
        
        # Prioritize based on skill importance and goal priority
        prioritized = []
        for resource in reading_resources:
            skill = self.skills.get(resource.skill_id)
            if not skill:
                continue
            
            # Find goals that include this skill
            related_goals = [g for g in self.goals.values() 
                           if resource.skill_id in g.skills and not g.completed]
            
            # Calculate priority
            priority = skill.importance
            if related_goals:
                priority += max(g.priority for g in related_goals)
            
            if priority >= priority_threshold:
                prioritized.append({
                    'resource': resource,
                    'skill_name': skill.name,
                    'priority': priority,
                    'estimated_hours': resource.estimated_hours
                })
        
        # Sort by priority
        prioritized.sort(key=lambda x: x['priority'], reverse=True)
        return prioritized
    
    # ============================================================================
    # STUDY SCHEDULE OPTIMIZATION
    # ============================================================================
    
    def log_study_session(self, session: StudySession) -> None:
        """Log a study session."""
        self.study_sessions.append(session)
    
    def optimize_study_schedule(self, 
                               days: int = 7,
                               available_hours_per_day: Optional[Dict[int, float]] = None) -> List[Dict]:
        """
        Generate optimized study schedule for the next N days.
        
        Considers:
        - Goal priorities and deadlines
        - Skill prerequisites
        - Preferred study times
        - Energy levels
        - Spaced repetition
        """
        schedule = []
        
        # Get active goals sorted by priority
        active_goals = sorted([g for g in self.goals.values() if not g.completed],
                            key=lambda x: x.priority, reverse=True)
        
        if not active_goals:
            return schedule
        
        # Create daily schedule
        for day_offset in range(days):
            study_date = datetime.now() + timedelta(days=day_offset)
            day_of_week = study_date.weekday()
            
            # Get available hours for this day
            if available_hours_per_day and day_of_week in available_hours_per_day:
                available_hours = available_hours_per_day[day_of_week]
            else:
                available_hours = self.max_daily_study_hours
            
            daily_schedule = []
            hours_scheduled = 0
            
            # Schedule sessions for top priority goals
            for goal in active_goals:
                if hours_scheduled >= available_hours:
                    break
                
                # Pick a skill from this goal to study
                for skill_id in goal.skills:
                    if skill_id not in self.skills:
                        continue
                    
                    skill = self.skills[skill_id]
                    
                    # Check if prerequisites are met
                    if not self._prerequisites_met(skill):
                        continue
                    
                    # Check if we studied this recently (spaced repetition)
                    last_session = self._get_last_session(skill_id)
                    if last_session:
                        days_since = (datetime.now() - last_session.timestamp).days
                        if days_since < 2:  # Don't study same skill too frequently
                            continue
                    
                    # Recommend resources
                    resources = self.recommend_resources(skill_id, limit=1)
                    
                    # Schedule 1-2 hour session
                    session_hours = min(2.0, available_hours - hours_scheduled)
                    
                    if session_hours >= 0.5:  # At least 30 minutes
                        daily_schedule.append({
                            'date': study_date.strftime('%Y-%m-%d'),
                            'skill_name': skill.name,
                            'goal_title': goal.title,
                            'duration_hours': session_hours,
                            'recommended_resource': resources[0].title if resources else 'Choose a resource',
                            'time_slot': self._suggest_time_slot(study_date)
                        })
                        hours_scheduled += session_hours
                        break  # Move to next goal
            
            schedule.extend(daily_schedule)
        
        return schedule
    
    def _prerequisites_met(self, skill: Skill) -> bool:
        """Check if skill prerequisites are met."""
        for prereq_id in skill.prerequisites:
            if prereq_id in self.skills:
                prereq = self.skills[prereq_id]
                if prereq.current_level.value < prereq.target_level.value:
                    return False
        return True
    
    def _get_last_session(self, skill_id: str) -> Optional[StudySession]:
        """Get the most recent study session for a skill."""
        skill_sessions = [s for s in self.study_sessions if s.skill_id == skill_id]
        if skill_sessions:
            return max(skill_sessions, key=lambda x: x.timestamp)
        return None
    
    def _suggest_time_slot(self, date: datetime) -> str:
        """Suggest optimal time slot based on preferences."""
        if self.preferred_study_times:
            start_time, end_time = self.preferred_study_times[0]
            return f"{start_time.strftime('%H:%M')} - {end_time.strftime('%H:%M')}"
        return "Flexible"
    
    # ============================================================================
    # KNOWLEDGE GAP ANALYSIS
    # ============================================================================
    
    def analyze_knowledge_gaps(self) -> List[KnowledgeGap]:
        """
        Identify knowledge gaps based on:
        - Goals vs current skills
        - Skill prerequisites
        - Related skills
        - Study session quality
        """
        gaps = []
        
        # Check each active goal
        for goal in self.goals.values():
            if goal.completed:
                continue
            
            for skill_id in goal.skills:
                if skill_id not in self.skills:
                    continue
                
                skill = self.skills[skill_id]
                
                # Gap 1: Skill level below target
                if skill.current_level.value < skill.target_level.value:
                    level_gap = skill.target_level.value - skill.current_level.value
                    gaps.append(KnowledgeGap(
                        skill_id=skill_id,
                        skill_name=skill.name,
                        gap_description=f"Need to progress from {skill.current_level.name} to {skill.target_level.name}",
                        severity=level_gap * 2 + skill.importance,
                        recommended_resources=[r.id for r in self.recommend_resources(skill_id, 3)]
                    ))
                
                # Gap 2: Unmet prerequisites
                for prereq_id in skill.prerequisites:
                    if prereq_id in self.skills:
                        prereq = self.skills[prereq_id]
                        if prereq.current_level.value < 2:  # Below intermediate
                            gaps.append(KnowledgeGap(
                                skill_id=prereq_id,
                                skill_name=prereq.name,
                                gap_description=f"Prerequisite for {skill.name} - need stronger foundation",
                                severity=8,
                                recommended_resources=[r.id for r in self.recommend_resources(prereq_id, 3)]
                            ))
                
                # Gap 3: Low quality study sessions
                skill_sessions = [s for s in self.study_sessions 
                                if s.skill_id == skill_id
                                and s.timestamp > datetime.now() - timedelta(days=30)]
                
                if skill_sessions:
                    avg_quality = statistics.mean(s.quality.value for s in skill_sessions)
                    if avg_quality < 3:
                        gaps.append(KnowledgeGap(
                            skill_id=skill_id,
                            skill_name=skill.name,
                            gap_description="Low study session quality - may need different approach or resources",
                            severity=6,
                            recommended_resources=[]
                        ))
        
        # Sort by severity
        gaps.sort(key=lambda x: x.severity, reverse=True)
        self.knowledge_gaps = gaps
        return gaps
    
    # ============================================================================
    # LEARNING ANALYTICS
    # ============================================================================
    
    def get_learning_report(self, days: int = 30) -> Dict:
        """Generate comprehensive learning report."""
        cutoff = datetime.now() - timedelta(days=days)
        recent_sessions = [s for s in self.study_sessions if s.timestamp > cutoff]
        
        if not recent_sessions:
            return {'error': 'No study sessions recorded'}
        
        # Calculate metrics
        total_hours = sum(s.duration_minutes for s in recent_sessions) / 60
        avg_hours_per_week = total_hours / (days / 7)
        
        # Quality metrics
        qualities = [s.quality.value for s in recent_sessions]
        avg_quality = statistics.mean(qualities)
        
        # Breakthrough moments
        breakthroughs = len([s for s in recent_sessions if s.breakthrough])
        
        # Skills studied
        skills_studied = set(s.skill_id for s in recent_sessions)
        
        # Most studied skill
        skill_hours = {}
        for session in recent_sessions:
            skill_hours[session.skill_id] = skill_hours.get(session.skill_id, 0) + session.duration_minutes / 60
        
        top_skill_id = max(skill_hours, key=skill_hours.get) if skill_hours else None
        top_skill_name = self.skills[top_skill_id].name if top_skill_id and top_skill_id in self.skills else "Unknown"
        
        # Goal progress
        goal_progress = []
        for goal in self.goals.values():
            if not goal.completed:
                analysis = self.analyze_goal_progress(goal.id)
                goal_progress.append({
                    'goal': goal.title,
                    'progress': analysis['overall_progress']
                })
        
        # Knowledge gaps
        gaps = self.analyze_knowledge_gaps()
        
        return {
            'total_study_hours': round(total_hours, 1),
            'avg_hours_per_week': round(avg_hours_per_week, 1),
            'total_sessions': len(recent_sessions),
            'avg_session_quality': round(avg_quality, 1),
            'breakthrough_moments': breakthroughs,
            'skills_studied': len(skills_studied),
            'top_skill': top_skill_name,
            'top_skill_hours': round(skill_hours.get(top_skill_id, 0), 1) if top_skill_id else 0,
            'goal_progress': goal_progress,
            'knowledge_gaps': len(gaps),
            'top_gaps': [{'skill': g.skill_name, 'severity': g.severity} for g in gaps[:3]],
            'recommendations': self._generate_learning_recommendations(avg_hours_per_week, avg_quality, gaps)
        }
    
    def _generate_learning_recommendations(self,
                                          avg_hours_per_week: float,
                                          avg_quality: float,
                                          gaps: List[KnowledgeGap]) -> List[str]:
        """Generate personalized learning recommendations."""
        recs = []
        
        # Study volume
        if avg_hours_per_week < 5:
            recs.append("Increase study time to at least 5-10 hours per week for meaningful progress")
        elif avg_hours_per_week > 20:
            recs.append("⚠️ High study volume - ensure you're not burning out. Quality > quantity")
        
        # Study quality
        if avg_quality < 3:
            recs.append("⚠️ Low session quality. Try: better environment, shorter sessions, active learning")
        elif avg_quality >= 4:
            recs.append("✅ High quality sessions! Keep up the effective study habits")
        
        # Knowledge gaps
        if gaps:
            top_gap = gaps[0]
            recs.append(f"Priority: Address {top_gap.skill_name} - {top_gap.gap_description}")
        
        # General tips
        recs.extend([
            "Use spaced repetition - review material at increasing intervals",
            "Practice active recall instead of passive reading",
            "Teach concepts to others to solidify understanding",
            "Take breaks every 25-50 minutes (Pomodoro technique)"
        ])
        
        return recs[:6]


if __name__ == "__main__":
    # Demo usage
    curator = LearningCurator()
    
    # Add skills
    curator.add_skill(Skill(
        id="python",
        name="Python Programming",
        category="Programming",
        current_level=SkillLevel.INTERMEDIATE,
        target_level=SkillLevel.ADVANCED,
        importance=9
    ))
    
    curator.add_skill(Skill(
        id="ml",
        name="Machine Learning",
        category="AI",
        current_level=SkillLevel.BEGINNER,
        target_level=SkillLevel.INTERMEDIATE,
        importance=10,
        prerequisites=["python"]
    ))
    
    # Add goal
    curator.add_goal(LearningGoal(
        id="1",
        title="Become ML Engineer",
        goal_type=LearningGoalType.CAREER,
        skills=["python", "ml"],
        deadline=datetime.now() + timedelta(days=365),
        priority=10
    ))
    
    # Add resource
    curator.add_resource(LearningResource(
        id="1",
        title="Deep Learning Specialization",
        content_type=ContentType.COURSE,
        skill_id="ml",
        difficulty=SkillLevel.INTERMEDIATE,
        estimated_hours=40,
        rating=4.9
    ))
    
    # Log session
    curator.log_study_session(StudySession(
        timestamp=datetime.now() - timedelta(days=1),
        skill_id="python",
        resource_id="1",
        duration_minutes=90,
        quality=StudySessionQuality.GOOD,
        topics_covered=["decorators", "generators"]
    ))
    
    # Generate report
    print("=== LEARNING REPORT ===")
    report = curator.get_learning_report(30)
    print(f"Total Study Hours: {report['total_study_hours']}")
    print(f"Avg Hours/Week: {report['avg_hours_per_week']}")
    print(f"Session Quality: {report['avg_session_quality']}/5")
    
    print("\nRecommendations:")
    for rec in report['recommendations']:
        print(f"  - {rec}")
    
    # Get study schedule
    print("\n=== STUDY SCHEDULE (Next 7 Days) ===")
    schedule = curator.optimize_study_schedule(7)
    for session in schedule:
        print(f"{session['date']}: {session['skill_name']} ({session['duration_hours']}h) - {session['recommended_resource']}")
