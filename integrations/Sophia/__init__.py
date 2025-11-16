"""
Sophia - Personal AI Life Assistant

A comprehensive suite of specialized AI agents that help optimize different aspects of your life.

Agent Specializations:
- ProductivityCoach: Task prioritization, schedule optimization, distraction prevention
- HealthAdvisor: Sleep optimization, exercise planning, nutrition tracking, stress management
- RelationshipManager: Communication tracking, check-in suggestions, important dates, isolation detection
- FinancialPlanner: Spending patterns, budget tracking, investment suggestions, goal tracking
- LearningCurator: Course recommendations, study optimization, knowledge gap analysis, reading lists
- CreativeCatalyst: Creative time blocks, output tracking, slump detection, inspiration delivery
- DreamAnalyst: Jungian/Freudian dream analysis with Fitbit wake detection and Messenger bot integration
"""

from .productivity_coach import (
    ProductivityCoach,
    Task,
    TimeBlock,
    Priority,
    EnergyLevel,
    ContextSwitch
)

from .health_advisor import (
    HealthAdvisor,
    SleepRecord,
    ExerciseSession,
    StressEvent,
    NutritionLog,
    SleepQuality,
    StressLevel,
    ExerciseIntensity
)

from .relationship_manager import (
    RelationshipManager,
    Person,
    Interaction,
    ImportantDate,
    CheckInSuggestion,
    RelationshipType,
    CommunicationType
)

from .financial_planner import (
    FinancialPlanner,
    Transaction,
    Budget,
    FinancialGoal,
    Investment,
    TransactionType,
    ExpenseCategory,
    InvestmentType,
    GoalStatus
)

from .learning_curator import (
    LearningCurator,
    Skill,
    LearningGoal,
    LearningResource,
    StudySession,
    KnowledgeGap,
    SkillLevel,
    LearningGoalType,
    ContentType,
    StudySessionQuality
)

from .creative_catalyst import (
    CreativeCatalyst,
    CreativeProject,
    CreativeSession,
    CreativeBlock,
    Inspiration,
    CreativeField,
    CreativePhase,
    MoodState
)

from .dream_analyst import (
    DreamAnalyst,
    DreamRecord,
    DreamAnalysis,
    DreamSymbol,
    AnalysisFramework,
    DreamType,
    JungianArchetype,
    FreudianMechanism,
    EmotionalTone
)

from .fitbit_integration import (
    FitbitIntegration,
    SleepData
)

from .messenger_dream_bot import (
    MessengerDreamBot
)

from .agi_dream_analyst import (
    AGIDreamAnalyst
)

__all__ = [
    # Main agent classes
    'ProductivityCoach',
    'HealthAdvisor',
    'RelationshipManager',
    'FinancialPlanner',
    'LearningCurator',
    'CreativeCatalyst',
    'DreamAnalyst',
    
    # Productivity types
    'Task',
    'TimeBlock',
    'Priority',
    'EnergyLevel',
    'ContextSwitch',
    
    # Health types
    'SleepRecord',
    'ExerciseSession',
    'StressEvent',
    'NutritionLog',
    'SleepQuality',
    'StressLevel',
    'ExerciseIntensity',
    
    # Relationship types
    'Person',
    'Interaction',
    'ImportantDate',
    'CheckInSuggestion',
    'RelationshipType',
    'CommunicationType',
    
    # Financial types
    'Transaction',
    'Budget',
    'FinancialGoal',
    'Investment',
    'TransactionType',
    'ExpenseCategory',
    'InvestmentType',
    'GoalStatus',
    
    # Learning types
    'Skill',
    'LearningGoal',
    'LearningResource',
    'StudySession',
    'KnowledgeGap',
    'SkillLevel',
    'LearningGoalType',
    'ContentType',
    'StudySessionQuality',
    
    # Creative types
    'CreativeProject',
    'CreativeSession',
    'CreativeBlock',
    'Inspiration',
    'CreativeField',
    'CreativePhase',
    'MoodState',
    
    # Dream analysis types
    'DreamRecord',
    'DreamAnalysis',
    'DreamSymbol',
    'AnalysisFramework',
    'DreamType',
    'JungianArchetype',
    'FreudianMechanism',
    'EmotionalTone',
    
    # Integration types
    'FitbitIntegration',
    'SleepData',
    'MessengerDreamBot',
    'AGIDreamAnalyst',
]

__version__ = '2.0.0'
__author__ = 'Singularis Team'
