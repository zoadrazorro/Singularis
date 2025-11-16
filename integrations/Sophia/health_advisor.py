"""
Health Advisor Agent - Sleep optimization, exercise planning, nutrition tracking, and stress management.

This agent monitors your health patterns and provides personalized recommendations
for better sleep, exercise, nutrition, and stress management.
"""

from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta, time
from dataclasses import dataclass
from enum import Enum
import statistics


class SleepQuality(Enum):
    """Sleep quality ratings."""
    EXCELLENT = 5
    GOOD = 4
    FAIR = 3
    POOR = 2
    TERRIBLE = 1


class StressLevel(Enum):
    """Stress level ratings."""
    MINIMAL = 1
    LOW = 2
    MODERATE = 3
    HIGH = 4
    SEVERE = 5


class ExerciseIntensity(Enum):
    """Exercise intensity levels."""
    REST = 0
    LIGHT = 1
    MODERATE = 2
    VIGOROUS = 3
    INTENSE = 4


@dataclass
class SleepRecord:
    """Records a sleep session."""
    date: datetime
    bedtime: time
    wake_time: time
    duration_hours: float
    quality: SleepQuality
    interruptions: int = 0
    notes: str = ""


@dataclass
class ExerciseSession:
    """Records an exercise session."""
    date: datetime
    activity: str
    duration_minutes: int
    intensity: ExerciseIntensity
    calories_burned: Optional[int] = None
    heart_rate_avg: Optional[int] = None
    notes: str = ""


@dataclass
class StressEvent:
    """Records a stress event."""
    timestamp: datetime
    level: StressLevel
    triggers: List[str]
    coping_strategy: Optional[str] = None
    duration_minutes: Optional[int] = None


@dataclass
class NutritionLog:
    """Records nutrition information."""
    date: datetime
    meal_type: str  # breakfast, lunch, dinner, snack
    description: str
    calories: Optional[int] = None
    protein_g: Optional[float] = None
    carbs_g: Optional[float] = None
    fat_g: Optional[float] = None
    water_ml: Optional[int] = None


class HealthAdvisor:
    """
    Health Advisor Agent that optimizes sleep, exercise, nutrition, and stress management.
    
    Features:
    - Sleep pattern analysis and optimization
    - Personalized exercise planning
    - Nutrition tracking and recommendations
    - Stress detection and management strategies
    """
    
    def __init__(self):
        self.sleep_records: List[SleepRecord] = []
        self.exercise_sessions: List[ExerciseSession] = []
        self.stress_events: List[StressEvent] = []
        self.nutrition_logs: List[NutritionLog] = []
        
        # User profile
        self.target_sleep_hours = 8.0
        self.target_exercise_minutes_per_week = 150  # WHO recommendation
        self.target_calories_per_day = 2000
        
    # ============================================================================
    # SLEEP OPTIMIZATION
    # ============================================================================
    
    def log_sleep(self, record: SleepRecord) -> None:
        """Log a sleep session."""
        self.sleep_records.append(record)
    
    def analyze_sleep_patterns(self, days: int = 30) -> Dict:
        """
        Analyze sleep patterns over the last N days.
        
        Returns metrics and insights about sleep quality.
        """
        recent_sleep = [s for s in self.sleep_records 
                       if s.date > datetime.now() - timedelta(days=days)]
        
        if not recent_sleep:
            return {'error': 'No sleep data available'}
        
        # Calculate metrics
        avg_duration = statistics.mean(s.duration_hours for s in recent_sleep)
        avg_quality = statistics.mean(s.quality.value for s in recent_sleep)
        avg_interruptions = statistics.mean(s.interruptions for s in recent_sleep)
        
        # Find optimal bedtime (when quality is highest)
        quality_by_bedtime = {}
        for record in recent_sleep:
            hour = record.bedtime.hour
            if hour not in quality_by_bedtime:
                quality_by_bedtime[hour] = []
            quality_by_bedtime[hour].append(record.quality.value)
        
        optimal_bedtime = max(quality_by_bedtime.items(), 
                             key=lambda x: statistics.mean(x[1]))[0] if quality_by_bedtime else None
        
        # Detect patterns
        patterns = self._detect_sleep_patterns(recent_sleep)
        
        return {
            'avg_duration_hours': round(avg_duration, 1),
            'avg_quality': round(avg_quality, 1),
            'avg_interruptions': round(avg_interruptions, 1),
            'optimal_bedtime': f"{optimal_bedtime}:00" if optimal_bedtime else "Unknown",
            'sleep_debt_hours': max(0, (self.target_sleep_hours - avg_duration) * days),
            'patterns': patterns,
            'recommendations': self._generate_sleep_recommendations(recent_sleep)
        }
    
    def _detect_sleep_patterns(self, records: List[SleepRecord]) -> List[str]:
        """Detect patterns in sleep data."""
        patterns = []
        
        # Check for consistency
        durations = [s.duration_hours for s in records]
        if statistics.stdev(durations) > 2:
            patterns.append("Inconsistent sleep schedule detected")
        
        # Check for sleep debt
        avg_duration = statistics.mean(durations)
        if avg_duration < self.target_sleep_hours - 1:
            patterns.append(f"Chronic sleep deprivation: {round(self.target_sleep_hours - avg_duration, 1)}h deficit")
        
        # Check for weekend catch-up sleep
        # (Would need day-of-week info in real implementation)
        
        # Check for frequent interruptions
        avg_interruptions = statistics.mean(s.interruptions for s in records)
        if avg_interruptions > 2:
            patterns.append("Frequent sleep interruptions detected")
        
        return patterns
    
    def _generate_sleep_recommendations(self, records: List[SleepRecord]) -> List[str]:
        """Generate personalized sleep recommendations."""
        recs = []
        
        avg_duration = statistics.mean(s.duration_hours for s in records)
        avg_quality = statistics.mean(s.quality.value for s in records)
        
        # Duration recommendations
        if avg_duration < 7:
            recs.append("Aim for 7-9 hours of sleep. Go to bed 30 minutes earlier.")
        elif avg_duration > 9:
            recs.append("You may be oversleeping. Try waking up 30 minutes earlier.")
        
        # Quality recommendations
        if avg_quality < 3:
            recs.extend([
                "Avoid screens 1 hour before bed (blue light disrupts melatonin)",
                "Keep bedroom cool (60-67°F / 15-19°C)",
                "Avoid caffeine after 2pm",
                "Try meditation or deep breathing before bed"
            ])
        
        # Interruption recommendations
        avg_interruptions = statistics.mean(s.interruptions for s in records)
        if avg_interruptions > 2:
            recs.extend([
                "Reduce liquid intake 2 hours before bed",
                "Use white noise or earplugs",
                "Ensure room is completely dark (blackout curtains)"
            ])
        
        return recs[:5]
    
    def get_optimal_sleep_schedule(self) -> Dict[str, str]:
        """Calculate optimal sleep schedule based on historical data."""
        if not self.sleep_records:
            return {
                'bedtime': "22:00",
                'wake_time': "06:00",
                'note': "Default recommendation (no data yet)"
            }
        
        analysis = self.analyze_sleep_patterns()
        optimal_bedtime = analysis.get('optimal_bedtime', '22:00')
        
        # Calculate wake time
        bedtime_hour = int(optimal_bedtime.split(':')[0])
        wake_hour = (bedtime_hour + int(self.target_sleep_hours)) % 24
        
        return {
            'bedtime': optimal_bedtime,
            'wake_time': f"{wake_hour:02d}:00",
            'target_duration': f"{self.target_sleep_hours} hours"
        }
    
    # ============================================================================
    # EXERCISE PLANNING
    # ============================================================================
    
    def log_exercise(self, session: ExerciseSession) -> None:
        """Log an exercise session."""
        self.exercise_sessions.append(session)
    
    def analyze_exercise_patterns(self, weeks: int = 4) -> Dict:
        """Analyze exercise patterns over the last N weeks."""
        cutoff = datetime.now() - timedelta(weeks=weeks)
        recent_sessions = [s for s in self.exercise_sessions if s.date > cutoff]
        
        if not recent_sessions:
            return {'error': 'No exercise data available'}
        
        # Calculate metrics
        total_minutes = sum(s.duration_minutes for s in recent_sessions)
        avg_minutes_per_week = total_minutes / weeks
        sessions_per_week = len(recent_sessions) / weeks
        
        # Activity breakdown
        activity_counts = {}
        for session in recent_sessions:
            activity_counts[session.activity] = activity_counts.get(session.activity, 0) + 1
        
        # Intensity distribution
        intensity_minutes = {intensity: 0 for intensity in ExerciseIntensity}
        for session in recent_sessions:
            intensity_minutes[session.intensity] += session.duration_minutes
        
        return {
            'total_minutes': total_minutes,
            'avg_minutes_per_week': round(avg_minutes_per_week, 1),
            'sessions_per_week': round(sessions_per_week, 1),
            'target_progress': round((avg_minutes_per_week / self.target_exercise_minutes_per_week) * 100, 1),
            'activity_breakdown': activity_counts,
            'intensity_distribution': {k.name: v for k, v in intensity_minutes.items()},
            'recommendations': self._generate_exercise_recommendations(recent_sessions, avg_minutes_per_week)
        }
    
    def _generate_exercise_recommendations(self, sessions: List[ExerciseSession], avg_weekly_minutes: float) -> List[str]:
        """Generate personalized exercise recommendations."""
        recs = []
        
        # Volume recommendations
        if avg_weekly_minutes < self.target_exercise_minutes_per_week:
            deficit = self.target_exercise_minutes_per_week - avg_weekly_minutes
            recs.append(f"Add {round(deficit)} minutes of exercise per week to meet WHO guidelines")
        
        # Variety recommendations
        activity_counts = {}
        for session in sessions:
            activity_counts[session.activity] = activity_counts.get(session.activity, 0) + 1
        
        if len(activity_counts) < 3:
            recs.append("Add variety to your routine (try strength training, cardio, and flexibility)")
        
        # Intensity recommendations
        intensity_counts = {intensity: 0 for intensity in ExerciseIntensity}
        for session in sessions:
            intensity_counts[session.intensity] += 1
        
        if intensity_counts[ExerciseIntensity.VIGOROUS] + intensity_counts[ExerciseIntensity.INTENSE] < len(sessions) * 0.3:
            recs.append("Include more high-intensity workouts (aim for 30% of sessions)")
        
        # Consistency recommendations
        if len(sessions) < 12:  # Less than 3x per week
            recs.append("Aim for at least 3 workout sessions per week for consistency")
        
        # Recovery recommendations
        if len(sessions) > 28:  # More than 7x per week
            recs.append("Consider adding rest days to prevent overtraining")
        
        return recs[:5]
    
    def generate_exercise_plan(self, days: int = 7) -> List[Dict]:
        """Generate a personalized exercise plan for the next N days."""
        plan = []
        
        # Analyze current patterns to determine gaps
        analysis = self.analyze_exercise_patterns()
        
        # Simple weekly template (can be personalized based on history)
        template = [
            {'day': 'Monday', 'activity': 'Strength Training', 'duration': 45, 'intensity': ExerciseIntensity.MODERATE},
            {'day': 'Tuesday', 'activity': 'Cardio (Running)', 'duration': 30, 'intensity': ExerciseIntensity.VIGOROUS},
            {'day': 'Wednesday', 'activity': 'Yoga/Stretching', 'duration': 30, 'intensity': ExerciseIntensity.LIGHT},
            {'day': 'Thursday', 'activity': 'Strength Training', 'duration': 45, 'intensity': ExerciseIntensity.MODERATE},
            {'day': 'Friday', 'activity': 'HIIT', 'duration': 25, 'intensity': ExerciseIntensity.INTENSE},
            {'day': 'Saturday', 'activity': 'Outdoor Activity', 'duration': 60, 'intensity': ExerciseIntensity.MODERATE},
            {'day': 'Sunday', 'activity': 'Rest/Light Walk', 'duration': 20, 'intensity': ExerciseIntensity.LIGHT},
        ]
        
        return template[:days]
    
    # ============================================================================
    # STRESS MANAGEMENT
    # ============================================================================
    
    def log_stress(self, event: StressEvent) -> None:
        """Log a stress event."""
        self.stress_events.append(event)
    
    def analyze_stress_patterns(self, days: int = 30) -> Dict:
        """Analyze stress patterns over the last N days."""
        cutoff = datetime.now() - timedelta(days=days)
        recent_events = [e for e in self.stress_events if e.timestamp > cutoff]
        
        if not recent_events:
            return {'error': 'No stress data available'}
        
        # Calculate metrics
        avg_stress = statistics.mean(e.level.value for e in recent_events)
        high_stress_days = len([e for e in recent_events if e.level.value >= 4])
        
        # Identify common triggers
        all_triggers = []
        for event in recent_events:
            all_triggers.extend(event.triggers)
        
        trigger_counts = {}
        for trigger in all_triggers:
            trigger_counts[trigger] = trigger_counts.get(trigger, 0) + 1
        
        top_triggers = sorted(trigger_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        
        # Analyze coping strategies
        coping_effectiveness = {}
        for event in recent_events:
            if event.coping_strategy:
                if event.coping_strategy not in coping_effectiveness:
                    coping_effectiveness[event.coping_strategy] = []
                coping_effectiveness[event.coping_strategy].append(event.level.value)
        
        return {
            'avg_stress_level': round(avg_stress, 1),
            'high_stress_days': high_stress_days,
            'stress_frequency': len(recent_events) / days,
            'top_triggers': top_triggers,
            'coping_strategies': {k: round(statistics.mean(v), 1) 
                                 for k, v in coping_effectiveness.items()},
            'recommendations': self._generate_stress_recommendations(recent_events, avg_stress)
        }
    
    def _generate_stress_recommendations(self, events: List[StressEvent], avg_stress: float) -> List[str]:
        """Generate personalized stress management recommendations."""
        recs = []
        
        # General stress level recommendations
        if avg_stress >= 4:
            recs.append("⚠️ High stress levels detected. Consider talking to a mental health professional.")
        elif avg_stress >= 3:
            recs.append("Moderate stress detected. Prioritize stress management techniques.")
        
        # Trigger-based recommendations
        all_triggers = []
        for event in events:
            all_triggers.extend(event.triggers)
        
        if 'work' in all_triggers or 'deadlines' in all_triggers:
            recs.append("Work stress is common. Try time-blocking and setting boundaries.")
        
        if 'sleep' in all_triggers or 'fatigue' in all_triggers:
            recs.append("Poor sleep increases stress. Prioritize sleep optimization.")
        
        # Evidence-based stress management techniques
        recs.extend([
            "Practice deep breathing: 4-7-8 technique (4s inhale, 7s hold, 8s exhale)",
            "Try progressive muscle relaxation before bed",
            "Exercise reduces stress hormones and boosts endorphins",
            "Limit caffeine and alcohol when stressed",
            "Connect with friends/family - social support reduces stress"
        ])
        
        return recs[:7]
    
    def suggest_stress_relief(self, current_stress: StressLevel) -> List[str]:
        """Suggest immediate stress relief techniques based on current stress level."""
        if current_stress == StressLevel.MINIMAL:
            return ["You're doing great! Maintain your current habits."]
        
        if current_stress == StressLevel.LOW:
            return [
                "Take a 5-minute walk",
                "Listen to calming music",
                "Stretch for 2 minutes"
            ]
        
        if current_stress == StressLevel.MODERATE:
            return [
                "Practice 4-7-8 breathing for 5 minutes",
                "Take a 15-minute walk outside",
                "Do a quick meditation (Headspace, Calm)",
                "Call a friend or family member"
            ]
        
        if current_stress == StressLevel.HIGH:
            return [
                "Step away from stressor immediately",
                "Practice box breathing (4-4-4-4)",
                "Do intense exercise (20-30 min)",
                "Journal about what's bothering you",
                "Talk to someone you trust"
            ]
        
        # SEVERE
        return [
            "⚠️ Seek immediate support from a mental health professional",
            "Call a crisis hotline if needed (988 in US)",
            "Remove yourself from the stressful situation",
            "Practice grounding techniques (5-4-3-2-1 method)",
            "Reach out to your support network immediately"
        ]
    
    # ============================================================================
    # NUTRITION TRACKING
    # ============================================================================
    
    def log_nutrition(self, log: NutritionLog) -> None:
        """Log nutrition information."""
        self.nutrition_logs.append(log)
    
    def analyze_nutrition(self, days: int = 7) -> Dict:
        """Analyze nutrition over the last N days."""
        cutoff = datetime.now() - timedelta(days=days)
        recent_logs = [n for n in self.nutrition_logs if n.date > cutoff]
        
        if not recent_logs:
            return {'error': 'No nutrition data available'}
        
        # Calculate daily averages
        logs_with_calories = [n for n in recent_logs if n.calories]
        avg_calories = statistics.mean(n.calories for n in logs_with_calories) if logs_with_calories else None
        
        logs_with_protein = [n for n in recent_logs if n.protein_g]
        avg_protein = statistics.mean(n.protein_g for n in logs_with_protein) if logs_with_protein else None
        
        logs_with_water = [n for n in recent_logs if n.water_ml]
        avg_water = statistics.mean(n.water_ml for n in logs_with_water) if logs_with_water else None
        
        # Meal frequency
        meal_counts = {}
        for log in recent_logs:
            meal_counts[log.meal_type] = meal_counts.get(log.meal_type, 0) + 1
        
        return {
            'avg_calories_per_day': round(avg_calories) if avg_calories else 'Not tracked',
            'avg_protein_g': round(avg_protein, 1) if avg_protein else 'Not tracked',
            'avg_water_ml': round(avg_water) if avg_water else 'Not tracked',
            'meal_frequency': meal_counts,
            'recommendations': self._generate_nutrition_recommendations(avg_calories, avg_protein, avg_water)
        }
    
    def _generate_nutrition_recommendations(self, 
                                           avg_calories: Optional[float],
                                           avg_protein: Optional[float],
                                           avg_water: Optional[float]) -> List[str]:
        """Generate personalized nutrition recommendations."""
        recs = []
        
        # Calorie recommendations
        if avg_calories:
            if avg_calories < self.target_calories_per_day - 500:
                recs.append("You may be under-eating. Ensure adequate calorie intake for energy.")
            elif avg_calories > self.target_calories_per_day + 500:
                recs.append("Consider reducing portion sizes or choosing lower-calorie options.")
        
        # Protein recommendations
        if avg_protein:
            target_protein = 0.8 * 70  # 0.8g per kg for 70kg person (adjust based on user)
            if avg_protein < target_protein:
                recs.append(f"Increase protein intake (target: {round(target_protein)}g/day). Add lean meats, fish, eggs, legumes.")
        
        # Hydration recommendations
        if avg_water:
            if avg_water < 2000:  # 2L per day
                recs.append("Increase water intake (target: 2-3L/day). Keep a water bottle nearby.")
        else:
            recs.append("Start tracking water intake. Aim for 8 glasses (2L) per day.")
        
        # General recommendations
        recs.extend([
            "Eat more whole foods (fruits, vegetables, whole grains)",
            "Limit processed foods and added sugars",
            "Include healthy fats (avocado, nuts, olive oil)",
            "Eat mindfully - avoid distractions during meals"
        ])
        
        return recs[:5]
    
    # ============================================================================
    # COMPREHENSIVE HEALTH REPORT
    # ============================================================================
    
    def get_health_report(self) -> Dict:
        """Generate comprehensive health report."""
        return {
            'sleep': self.analyze_sleep_patterns(30),
            'exercise': self.analyze_exercise_patterns(4),
            'stress': self.analyze_stress_patterns(30),
            'nutrition': self.analyze_nutrition(7),
            'overall_score': self._calculate_health_score(),
            'priority_actions': self._get_priority_health_actions()
        }
    
    def _calculate_health_score(self) -> float:
        """Calculate overall health score (0-100)."""
        score = 0
        components = 0
        
        # Sleep score (0-25)
        if self.sleep_records:
            recent_sleep = [s for s in self.sleep_records 
                          if s.date > datetime.now() - timedelta(days=30)]
            if recent_sleep:
                avg_duration = statistics.mean(s.duration_hours for s in recent_sleep)
                avg_quality = statistics.mean(s.quality.value for s in recent_sleep)
                sleep_score = (min(avg_duration / self.target_sleep_hours, 1) * 15) + (avg_quality / 5 * 10)
                score += sleep_score
                components += 1
        
        # Exercise score (0-25)
        if self.exercise_sessions:
            recent_exercise = [s for s in self.exercise_sessions 
                             if s.date > datetime.now() - timedelta(weeks=4)]
            if recent_exercise:
                total_minutes = sum(s.duration_minutes for s in recent_exercise)
                avg_weekly = total_minutes / 4
                exercise_score = min(avg_weekly / self.target_exercise_minutes_per_week, 1) * 25
                score += exercise_score
                components += 1
        
        # Stress score (0-25) - inverted (lower stress = higher score)
        if self.stress_events:
            recent_stress = [e for e in self.stress_events 
                           if e.timestamp > datetime.now() - timedelta(days=30)]
            if recent_stress:
                avg_stress = statistics.mean(e.level.value for e in recent_stress)
                stress_score = (1 - (avg_stress - 1) / 4) * 25  # Invert and scale
                score += stress_score
                components += 1
        
        # Nutrition score (0-25)
        if self.nutrition_logs:
            recent_nutrition = [n for n in self.nutrition_logs 
                              if n.date > datetime.now() - timedelta(days=7)]
            if recent_nutrition:
                # Simple score based on tracking consistency
                nutrition_score = min(len(recent_nutrition) / 21, 1) * 25  # 3 meals x 7 days
                score += nutrition_score
                components += 1
        
        return round(score / components if components > 0 else 0, 1)
    
    def _get_priority_health_actions(self) -> List[str]:
        """Get top priority health actions."""
        actions = []
        
        # Check each area and prioritize
        if self.sleep_records:
            analysis = self.analyze_sleep_patterns(30)
            if analysis.get('avg_duration_hours', 8) < 7:
                actions.append("🔴 CRITICAL: Increase sleep duration (currently < 7 hours)")
        
        if self.exercise_sessions:
            analysis = self.analyze_exercise_patterns(4)
            if analysis.get('avg_minutes_per_week', 0) < 75:  # Less than 50% of target
                actions.append("🟡 IMPORTANT: Increase exercise frequency (currently < 75 min/week)")
        
        if self.stress_events:
            analysis = self.analyze_stress_patterns(30)
            if analysis.get('avg_stress_level', 0) >= 4:
                actions.append("🔴 CRITICAL: High stress levels - seek support")
        
        return actions[:3]


if __name__ == "__main__":
    # Demo usage
    advisor = HealthAdvisor()
    
    # Add sample data
    advisor.log_sleep(SleepRecord(
        date=datetime.now() - timedelta(days=1),
        bedtime=time(23, 0),
        wake_time=time(7, 0),
        duration_hours=7.5,
        quality=SleepQuality.GOOD,
        interruptions=1
    ))
    
    advisor.log_exercise(ExerciseSession(
        date=datetime.now(),
        activity="Running",
        duration_minutes=30,
        intensity=ExerciseIntensity.MODERATE
    ))
    
    advisor.log_stress(StressEvent(
        timestamp=datetime.now(),
        level=StressLevel.MODERATE,
        triggers=["work", "deadlines"],
        coping_strategy="deep breathing"
    ))
    
    # Generate report
    print("=== HEALTH REPORT ===")
    report = advisor.get_health_report()
    print(f"Overall Health Score: {report['overall_score']}/100")
    
    print("\nPriority Actions:")
    for action in report['priority_actions']:
        print(f"  {action}")
