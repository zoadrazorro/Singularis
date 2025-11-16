"""
Productivity Coach Agent - Task prioritization, schedule optimization, and distraction prevention.

This agent analyzes your work patterns, optimizes your schedule, and helps minimize
context switching while preventing distractions.
"""

from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum


class Priority(Enum):
    """Task priority levels."""
    CRITICAL = 4
    HIGH = 3
    MEDIUM = 2
    LOW = 1


class EnergyLevel(Enum):
    """Energy level throughout the day."""
    PEAK = "peak"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class Task:
    """Represents a task with metadata."""
    id: str
    title: str
    priority: Priority
    estimated_duration: int  # minutes
    deadline: Optional[datetime] = None
    requires_deep_focus: bool = False
    context: str = "general"
    dependencies: List[str] = None
    completed: bool = False
    
    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []


@dataclass
class TimeBlock:
    """Represents a scheduled time block."""
    start: datetime
    end: datetime
    task_id: str
    energy_level: EnergyLevel
    buffer_before: int = 5  # minutes
    buffer_after: int = 5


@dataclass
class ContextSwitch:
    """Tracks context switching events."""
    timestamp: datetime
    from_context: str
    to_context: str
    cost_minutes: int = 15  # Average cost of context switch


class ProductivityCoach:
    """
    Productivity Coach Agent that optimizes task management and schedule.
    
    Features:
    - Task prioritization using Eisenhower Matrix + deadline urgency
    - Schedule optimization based on energy levels
    - Context switching minimization
    - Distraction detection and prevention
    """
    
    def __init__(self):
        self.tasks: List[Task] = []
        self.schedule: List[TimeBlock] = []
        self.context_switches: List[ContextSwitch] = []
        self.energy_profile: Dict[int, EnergyLevel] = self._default_energy_profile()
        self.distraction_log: List[Dict] = []
        
    def _default_energy_profile(self) -> Dict[int, EnergyLevel]:
        """Default energy levels by hour of day."""
        return {
            6: EnergyLevel.MEDIUM,
            7: EnergyLevel.HIGH,
            8: EnergyLevel.HIGH,
            9: EnergyLevel.PEAK,
            10: EnergyLevel.PEAK,
            11: EnergyLevel.HIGH,
            12: EnergyLevel.MEDIUM,
            13: EnergyLevel.LOW,
            14: EnergyLevel.MEDIUM,
            15: EnergyLevel.HIGH,
            16: EnergyLevel.HIGH,
            17: EnergyLevel.MEDIUM,
            18: EnergyLevel.MEDIUM,
            19: EnergyLevel.LOW,
            20: EnergyLevel.LOW,
        }
    
    def add_task(self, task: Task) -> None:
        """Add a task to the queue."""
        self.tasks.append(task)
    
    def prioritize_tasks(self) -> List[Task]:
        """
        Prioritize tasks using multiple factors:
        1. Priority level (CRITICAL > HIGH > MEDIUM > LOW)
        2. Deadline urgency
        3. Dependencies
        4. Deep focus requirements
        
        Returns sorted list of tasks.
        """
        def priority_score(task: Task) -> float:
            score = task.priority.value * 100
            
            # Add urgency score based on deadline
            if task.deadline:
                hours_until_deadline = (task.deadline - datetime.now()).total_seconds() / 3600
                if hours_until_deadline < 24:
                    score += 50
                elif hours_until_deadline < 72:
                    score += 30
                elif hours_until_deadline < 168:  # 1 week
                    score += 10
            
            # Penalize tasks with unmet dependencies
            if task.dependencies:
                unmet_deps = sum(1 for dep_id in task.dependencies 
                               if not any(t.id == dep_id and t.completed for t in self.tasks))
                score -= unmet_deps * 20
            
            # Boost deep focus tasks (schedule them during peak energy)
            if task.requires_deep_focus:
                score += 15
            
            return score
        
        return sorted([t for t in self.tasks if not t.completed], 
                     key=priority_score, reverse=True)
    
    def optimize_schedule(self, 
                         start_time: datetime, 
                         end_time: datetime,
                         break_duration: int = 15) -> List[TimeBlock]:
        """
        Optimize schedule based on:
        1. Energy levels throughout the day
        2. Task requirements (deep focus vs routine)
        3. Context grouping to minimize switches
        4. Buffer time between tasks
        
        Args:
            start_time: Start of work period
            end_time: End of work period
            break_duration: Minutes for breaks between tasks
            
        Returns list of scheduled time blocks.
        """
        prioritized_tasks = self.prioritize_tasks()
        schedule = []
        current_time = start_time
        current_context = None
        
        for task in prioritized_tasks:
            if current_time >= end_time:
                break
            
            # Get energy level for current hour
            hour = current_time.hour
            energy = self.energy_profile.get(hour, EnergyLevel.MEDIUM)
            
            # Match deep focus tasks with peak energy
            if task.requires_deep_focus and energy not in [EnergyLevel.PEAK, EnergyLevel.HIGH]:
                continue  # Skip for now, schedule during better time
            
            # Calculate context switch cost
            buffer_before = 5
            if current_context and current_context != task.context:
                buffer_before = 15  # Extra time for context switch
                self.context_switches.append(ContextSwitch(
                    timestamp=current_time,
                    from_context=current_context,
                    to_context=task.context
                ))
            
            # Schedule the task
            task_start = current_time + timedelta(minutes=buffer_before)
            task_end = task_start + timedelta(minutes=task.estimated_duration)
            
            if task_end > end_time:
                break
            
            schedule.append(TimeBlock(
                start=task_start,
                end=task_end,
                task_id=task.id,
                energy_level=energy,
                buffer_before=buffer_before,
                buffer_after=break_duration
            ))
            
            current_time = task_end + timedelta(minutes=break_duration)
            current_context = task.context
        
        self.schedule = schedule
        return schedule
    
    def minimize_context_switching(self) -> Dict[str, List[Task]]:
        """
        Group tasks by context to minimize switching.
        
        Returns dictionary of context -> tasks.
        """
        context_groups = {}
        for task in self.tasks:
            if not task.completed:
                if task.context not in context_groups:
                    context_groups[task.context] = []
                context_groups[task.context].append(task)
        
        return context_groups
    
    def detect_distraction(self, 
                          current_task: str, 
                          actual_activity: str,
                          duration_minutes: int) -> bool:
        """
        Detect if user is distracted from current task.
        
        Args:
            current_task: What should be worked on
            actual_activity: What is actually being done
            duration_minutes: How long the activity has lasted
            
        Returns True if distraction detected.
        """
        # Simple heuristic: if activity doesn't match task and lasts > 5 min
        is_distracted = (current_task.lower() not in actual_activity.lower() 
                        and duration_minutes > 5)
        
        if is_distracted:
            self.distraction_log.append({
                'timestamp': datetime.now(),
                'expected': current_task,
                'actual': actual_activity,
                'duration': duration_minutes
            })
        
        return is_distracted
    
    def get_distraction_prevention_tips(self) -> List[str]:
        """Get personalized distraction prevention tips."""
        tips = []
        
        # Analyze distraction patterns
        if len(self.distraction_log) > 5:
            recent_distractions = self.distraction_log[-10:]
            
            # Check for time-of-day patterns
            distraction_hours = [d['timestamp'].hour for d in recent_distractions]
            if distraction_hours.count(max(set(distraction_hours), key=distraction_hours.count)) >= 3:
                problem_hour = max(set(distraction_hours), key=distraction_hours.count)
                tips.append(f"You tend to get distracted around {problem_hour}:00. "
                          f"Schedule routine tasks then, save deep work for other times.")
            
            # Check for common distraction types
            activities = [d['actual'] for d in recent_distractions]
            if any('social' in a.lower() or 'chat' in a.lower() for a in activities):
                tips.append("Social media/chat is a common distraction. "
                          "Try using website blockers during focus time.")
            
            if any('email' in a.lower() for a in activities):
                tips.append("Email checking interrupts your flow. "
                          "Schedule specific times for email (e.g., 10am, 2pm, 4pm).")
        
        # General tips
        tips.extend([
            "Use the Pomodoro Technique: 25 min focus + 5 min break",
            "Turn off notifications during deep work sessions",
            "Keep your phone in another room during focus time",
            "Use noise-cancelling headphones or focus music"
        ])
        
        return tips[:5]  # Return top 5 tips
    
    def get_productivity_report(self) -> Dict:
        """Generate productivity report with metrics and insights."""
        completed_tasks = [t for t in self.tasks if t.completed]
        pending_tasks = [t for t in self.tasks if not t.completed]
        
        # Calculate context switch cost
        total_switch_cost = sum(cs.cost_minutes for cs in self.context_switches)
        
        # Calculate distraction time
        total_distraction_time = sum(d['duration'] for d in self.distraction_log)
        
        return {
            'tasks_completed': len(completed_tasks),
            'tasks_pending': len(pending_tasks),
            'completion_rate': len(completed_tasks) / len(self.tasks) if self.tasks else 0,
            'context_switches': len(self.context_switches),
            'context_switch_cost_minutes': total_switch_cost,
            'distractions': len(self.distraction_log),
            'distraction_time_minutes': total_distraction_time,
            'efficiency_score': self._calculate_efficiency_score(),
            'recommendations': self._generate_recommendations()
        }
    
    def _calculate_efficiency_score(self) -> float:
        """Calculate overall efficiency score (0-100)."""
        if not self.tasks:
            return 0.0
        
        # Base score from completion rate
        completion_rate = len([t for t in self.tasks if t.completed]) / len(self.tasks)
        score = completion_rate * 50
        
        # Penalty for context switches (max -20)
        switch_penalty = min(len(self.context_switches) * 2, 20)
        score -= switch_penalty
        
        # Penalty for distractions (max -20)
        distraction_penalty = min(len(self.distraction_log) * 3, 20)
        score -= distraction_penalty
        
        # Bonus for meeting deadlines (max +20)
        completed = [t for t in self.tasks if t.completed and t.deadline]
        on_time = sum(1 for t in completed if t.deadline > datetime.now())
        if completed:
            deadline_bonus = (on_time / len(completed)) * 20
            score += deadline_bonus
        
        return max(0, min(100, score))
    
    def _generate_recommendations(self) -> List[str]:
        """Generate actionable recommendations."""
        recs = []
        
        # Context switching
        if len(self.context_switches) > 5:
            recs.append("High context switching detected. Try batching similar tasks together.")
        
        # Distractions
        if len(self.distraction_log) > 3:
            recs.append("Frequent distractions detected. Review distraction prevention tips.")
        
        # Task completion
        overdue = [t for t in self.tasks if not t.completed and t.deadline and t.deadline < datetime.now()]
        if overdue:
            recs.append(f"{len(overdue)} tasks are overdue. Consider renegotiating deadlines or delegating.")
        
        # Deep focus
        deep_focus_tasks = [t for t in self.tasks if t.requires_deep_focus and not t.completed]
        if deep_focus_tasks:
            recs.append(f"{len(deep_focus_tasks)} deep focus tasks pending. "
                       f"Schedule them during your peak energy hours (9-11am).")
        
        return recs


if __name__ == "__main__":
    # Demo usage
    coach = ProductivityCoach()
    
    # Add sample tasks
    coach.add_task(Task(
        id="1",
        title="Write project proposal",
        priority=Priority.HIGH,
        estimated_duration=90,
        deadline=datetime.now() + timedelta(days=2),
        requires_deep_focus=True,
        context="writing"
    ))
    
    coach.add_task(Task(
        id="2",
        title="Review pull requests",
        priority=Priority.MEDIUM,
        estimated_duration=30,
        requires_deep_focus=False,
        context="code_review"
    ))
    
    coach.add_task(Task(
        id="3",
        title="Team standup",
        priority=Priority.HIGH,
        estimated_duration=15,
        deadline=datetime.now() + timedelta(hours=2),
        context="meetings"
    ))
    
    # Prioritize
    print("=== PRIORITIZED TASKS ===")
    for task in coach.prioritize_tasks():
        print(f"{task.priority.name}: {task.title} ({task.estimated_duration}min)")
    
    # Optimize schedule
    print("\n=== OPTIMIZED SCHEDULE ===")
    start = datetime.now().replace(hour=9, minute=0, second=0, microsecond=0)
    end = start + timedelta(hours=8)
    schedule = coach.optimize_schedule(start, end)
    
    for block in schedule:
        task = next(t for t in coach.tasks if t.id == block.task_id)
        print(f"{block.start.strftime('%H:%M')} - {block.end.strftime('%H:%M')}: "
              f"{task.title} [{block.energy_level.value}]")
    
    # Context grouping
    print("\n=== CONTEXT GROUPS ===")
    groups = coach.minimize_context_switching()
    for context, tasks in groups.items():
        print(f"{context}: {len(tasks)} tasks")
    
    # Report
    print("\n=== PRODUCTIVITY REPORT ===")
    report = coach.get_productivity_report()
    for key, value in report.items():
        if key != 'recommendations':
            print(f"{key}: {value}")
    
    print("\nRecommendations:")
    for rec in report['recommendations']:
        print(f"- {rec}")
