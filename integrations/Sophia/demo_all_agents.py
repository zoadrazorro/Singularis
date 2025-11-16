"""
Comprehensive demo of all Sophia agents working together.

This script demonstrates how each specialized agent can be used to optimize
different aspects of your life.
"""

from datetime import datetime, timedelta, time
from productivity_coach import ProductivityCoach, Task, Priority
from health_advisor import HealthAdvisor, SleepRecord, ExerciseSession, StressEvent, SleepQuality, StressLevel, ExerciseIntensity
from relationship_manager import RelationshipManager, Person, Interaction, RelationshipType, CommunicationType
from financial_planner import FinancialPlanner, Transaction, FinancialGoal, TransactionType, ExpenseCategory, GoalStatus
from learning_curator import LearningCurator, Skill, LearningGoal, LearningResource, StudySession, SkillLevel, LearningGoalType, ContentType, StudySessionQuality
from creative_catalyst import CreativeCatalyst, CreativeProject, CreativeSession, CreativeField, CreativePhase, MoodState


def print_section(title: str):
    """Print a formatted section header."""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def demo_productivity_coach():
    """Demo the Productivity Coach agent."""
    print_section("PRODUCTIVITY COACH")
    
    coach = ProductivityCoach()
    
    # Add tasks
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
    
    # Prioritize tasks
    print("📋 PRIORITIZED TASKS:")
    for task in coach.prioritize_tasks()[:5]:
        print(f"  {task.priority.name}: {task.title} ({task.estimated_duration}min)")
    
    # Optimize schedule
    print("\n📅 OPTIMIZED SCHEDULE (Today):")
    start = datetime.now().replace(hour=9, minute=0, second=0, microsecond=0)
    end = start + timedelta(hours=8)
    schedule = coach.optimize_schedule(start, end)
    
    for block in schedule[:5]:
        task = next(t for t in coach.tasks if t.id == block.task_id)
        print(f"  {block.start.strftime('%H:%M')}-{block.end.strftime('%H:%M')}: {task.title}")
    
    # Get report
    report = coach.get_productivity_report()
    print(f"\n📊 EFFICIENCY SCORE: {report['efficiency_score']:.1f}/100")


def demo_health_advisor():
    """Demo the Health Advisor agent."""
    print_section("HEALTH ADVISOR")
    
    advisor = HealthAdvisor()
    
    # Log sleep
    for i in range(7):
        advisor.log_sleep(SleepRecord(
            date=datetime.now() - timedelta(days=i),
            bedtime=time(23, 0),
            wake_time=time(7, 0),
            duration_hours=7.5 + (i % 2) * 0.5,
            quality=SleepQuality.GOOD if i % 2 == 0 else SleepQuality.FAIR,
            interruptions=i % 3
        ))
    
    # Log exercise
    advisor.log_exercise(ExerciseSession(
        date=datetime.now(),
        activity="Running",
        duration_minutes=30,
        intensity=ExerciseIntensity.MODERATE
    ))
    
    advisor.log_exercise(ExerciseSession(
        date=datetime.now() - timedelta(days=2),
        activity="Strength Training",
        duration_minutes=45,
        intensity=ExerciseIntensity.VIGOROUS
    ))
    
    # Log stress
    advisor.log_stress(StressEvent(
        timestamp=datetime.now(),
        level=StressLevel.MODERATE,
        triggers=["work", "deadlines"],
        coping_strategy="deep breathing"
    ))
    
    # Get report
    report = advisor.get_health_report()
    print(f"💪 HEALTH SCORE: {report['overall_score']:.1f}/100")
    
    sleep = report['sleep']
    print(f"\n😴 SLEEP:")
    print(f"  Average: {sleep['avg_duration_hours']}h")
    print(f"  Quality: {sleep['avg_quality']:.1f}/5")
    print(f"  Optimal bedtime: {sleep.get('optimal_bedtime', 'Unknown')}")
    
    exercise = report['exercise']
    if 'error' not in exercise:
        print(f"\n🏃 EXERCISE:")
        print(f"  Weekly: {exercise['avg_minutes_per_week']:.1f} min")
        print(f"  Target progress: {exercise['target_progress']:.1f}%")
    
    print("\n💡 TOP RECOMMENDATIONS:")
    for action in report['priority_actions'][:3]:
        print(f"  • {action}")


def demo_relationship_manager():
    """Demo the Relationship Manager agent."""
    print_section("RELATIONSHIP MANAGER")
    
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
    
    manager.add_person(Person(
        id="3",
        name="College Friend",
        relationship_type=RelationshipType.FRIEND,
        importance=7
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
    
    # Get check-in suggestions
    print("📞 CHECK-IN SUGGESTIONS:")
    suggestions = manager.get_check_in_suggestions(5)
    for sug in suggestions[:3]:
        print(f"  • {sug.person_name}: {sug.reason} (Priority: {sug.priority}/10)")
    
    # Get upcoming dates
    print("\n🎂 UPCOMING IMPORTANT DATES:")
    upcoming = manager.get_upcoming_dates(60)
    for date_info in upcoming[:3]:
        print(f"  • {date_info['person_name']}: {date_info['event_type']} in {date_info['days_until']} days")
    
    # Isolation check
    isolation = manager.detect_isolation_patterns(30)
    print(f"\n🏠 SOCIAL HEALTH:")
    print(f"  Level: {isolation['isolation_level']}")
    print(f"  Interactions/week: {isolation['interactions_per_week']}")
    if isolation['warnings']:
        print(f"  Warnings: {len(isolation['warnings'])}")


def demo_financial_planner():
    """Demo the Financial Planner agent."""
    print_section("FINANCIAL PLANNER")
    
    planner = FinancialPlanner()
    planner.monthly_income = 5000
    
    # Add transactions
    planner.add_transaction(Transaction(
        id="1",
        date=datetime.now() - timedelta(days=5),
        amount=1200,
        transaction_type=TransactionType.EXPENSE,
        category=ExpenseCategory.HOUSING,
        description="Rent"
    ))
    
    planner.add_transaction(Transaction(
        id="2",
        date=datetime.now() - timedelta(days=3),
        amount=150,
        transaction_type=TransactionType.EXPENSE,
        category=ExpenseCategory.FOOD,
        description="Groceries"
    ))
    
    planner.add_transaction(Transaction(
        id="3",
        date=datetime.now() - timedelta(days=1),
        amount=50,
        transaction_type=TransactionType.EXPENSE,
        category=ExpenseCategory.ENTERTAINMENT,
        description="Movie night"
    ))
    
    # Set budgets
    planner.set_budget(ExpenseCategory.HOUSING, 1300)
    planner.set_budget(ExpenseCategory.FOOD, 500)
    planner.set_budget(ExpenseCategory.ENTERTAINMENT, 200)
    
    # Add goal
    planner.add_goal(FinancialGoal(
        id="1",
        name="Emergency Fund",
        target_amount=15000,
        current_amount=5000,
        deadline=datetime.now() + timedelta(days=365),
        monthly_contribution=500,
        status=GoalStatus.IN_PROGRESS
    ))
    
    # Get report
    report = planner.get_financial_report()
    print(f"💰 FINANCIAL HEALTH: {report['financial_health_score']:.1f}/100")
    print(f"\n📊 THIS MONTH:")
    print(f"  Income: ${report['monthly_income']:.2f}")
    print(f"  Expenses: ${report['monthly_expenses']:.2f}")
    print(f"  Savings Rate: {report['savings_rate']:.1f}%")
    
    print("\n🎯 BUDGET STATUS:")
    for category, status in list(report['budget_status'].items())[:3]:
        print(f"  {category}: ${status['spent']:.2f} / ${status['limit']:.2f} ({status['percentage']:.1f}%)")
    
    if report['budget_alerts']:
        print("\n⚠️ ALERTS:")
        for alert in report['budget_alerts'][:2]:
            print(f"  • {alert}")


def demo_learning_curator():
    """Demo the Learning Curator agent."""
    print_section("LEARNING CURATOR")
    
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
    
    # Add resources
    curator.add_resource(LearningResource(
        id="1",
        title="Deep Learning Specialization",
        content_type=ContentType.COURSE,
        skill_id="ml",
        difficulty=SkillLevel.INTERMEDIATE,
        estimated_hours=40,
        rating=4.9
    ))
    
    curator.add_resource(LearningResource(
        id="2",
        title="Python Cookbook",
        content_type=ContentType.BOOK,
        skill_id="python",
        difficulty=SkillLevel.ADVANCED,
        estimated_hours=20,
        rating=4.7
    ))
    
    # Log study sessions
    curator.log_study_session(StudySession(
        timestamp=datetime.now() - timedelta(days=1),
        skill_id="python",
        resource_id="2",
        duration_minutes=90,
        quality=StudySessionQuality.GOOD,
        topics_covered=["decorators", "generators"]
    ))
    
    curator.log_study_session(StudySession(
        timestamp=datetime.now() - timedelta(days=3),
        skill_id="ml",
        resource_id="1",
        duration_minutes=120,
        quality=StudySessionQuality.EXCELLENT,
        topics_covered=["neural networks"],
        breakthrough=True
    ))
    
    # Get report
    report = curator.get_learning_report(30)
    print(f"📚 LEARNING STATS:")
    print(f"  Total hours: {report['total_study_hours']}")
    print(f"  Hours/week: {report['avg_hours_per_week']}")
    print(f"  Session quality: {report['avg_session_quality']:.1f}/5")
    print(f"  Breakthrough moments: {report['breakthrough_moments']}")
    
    print("\n🎯 GOAL PROGRESS:")
    for goal in report['goal_progress'][:2]:
        print(f"  • {goal['goal']}: {goal['progress']:.1f}%")
    
    # Get study schedule
    print("\n📅 STUDY SCHEDULE (Next 3 Days):")
    schedule = curator.optimize_study_schedule(3)
    for session in schedule[:3]:
        print(f"  {session['date']}: {session['skill_name']} ({session['duration_hours']}h)")


def demo_creative_catalyst():
    """Demo the Creative Catalyst agent."""
    print_section("CREATIVE CATALYST")
    
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
    
    catalyst.add_project(CreativeProject(
        id="2",
        title="Album Recording",
        field=CreativeField.MUSIC,
        phase=CreativePhase.IDEATION,
        started=datetime.now() - timedelta(days=10)
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
    
    catalyst.log_session(CreativeSession(
        timestamp=datetime.now() - timedelta(days=5),
        project_id="2",
        field=CreativeField.MUSIC,
        duration_minutes=120,
        output_count=3,  # songs
        mood=MoodState.INSPIRED,
        breakthrough=True
    ))
    
    # Get report
    report = catalyst.get_creative_report(30)
    print(f"🎨 CREATIVE HEALTH: {report['creative_health_score']:.1f}/100")
    
    output = report['creative_output']
    if 'error' not in output:
        print(f"\n📊 OUTPUT:")
        print(f"  Total hours: {output['total_hours']}")
        print(f"  Sessions/week: {output['sessions_per_week']:.1f}")
        print(f"  Breakthrough moments: {output['breakthrough_moments']}")
        print(f"  Consistency: {output['consistency_score']:.1f}%")
    
    print(f"\n📁 PROJECTS:")
    print(f"  Active: {report['active_projects']}")
    for phase, count in report['projects_by_phase'].items():
        if count > 0:
            print(f"  {phase}: {count}")
    
    # Daily inspiration
    inspiration = report['daily_inspiration']
    print(f"\n✨ DAILY INSPIRATION:")
    print(f"  Quote: {inspiration['quote']}")
    print(f"  Prompt: {inspiration['prompt']}")
    
    # Time blocks
    print("\n⏰ SUGGESTED CREATIVE TIME (Next 3 Days):")
    for block in report['time_block_suggestions'][:3]:
        print(f"  {block['day']}: {block['time_slot']} - {block['project']}")


def main():
    """Run all demos."""
    print("\n" + "=" * 80)
    print("  SOPHIA - PERSONAL AI LIFE ASSISTANT")
    print("  Comprehensive Demo of All Agent Specializations")
    print("=" * 80)
    
    demo_productivity_coach()
    demo_health_advisor()
    demo_relationship_manager()
    demo_financial_planner()
    demo_learning_curator()
    demo_creative_catalyst()
    
    print_section("DEMO COMPLETE")
    print("All 6 specialized agents are working together to optimize your life!")
    print("\nNext steps:")
    print("  1. Integrate with real data sources (calendar, health apps, banking, etc.)")
    print("  2. Set up automated data collection")
    print("  3. Configure personalized preferences for each agent")
    print("  4. Enable notifications and reminders")
    print("  5. Build a unified dashboard to view all insights")
    print("\n" + "=" * 80 + "\n")


if __name__ == "__main__":
    main()
