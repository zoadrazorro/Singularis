# Sophia Agent Specializations - Quick Reference Guide

## Overview

Sophia is a comprehensive personal AI life assistant with 6 specialized agents, each optimizing a different aspect of your life.

## 🎯 Agent Specializations

### 1. **Productivity Coach** (`productivity_coach.py`)

**Purpose**: Optimize task management, schedule, and focus

**Key Features**:
- Task prioritization using Eisenhower Matrix + deadline urgency
- Schedule optimization based on energy levels
- Context switching minimization
- Distraction detection and prevention
- Efficiency scoring (0-100)

**Main Methods**:
```python
coach = ProductivityCoach()
coach.add_task(task)
prioritized = coach.prioritize_tasks()
schedule = coach.optimize_schedule(start_time, end_time)
report = coach.get_productivity_report()
```

**Use Cases**:
- Overwhelmed with tasks
- Frequent context switching
- Distraction problems
- Poor time management

---

### 2. **Health Advisor** (`health_advisor.py`)

**Purpose**: Optimize sleep, exercise, nutrition, and stress management

**Key Features**:
- Sleep pattern analysis and optimization
- Exercise planning (WHO guidelines: 150 min/week)
- Nutrition tracking and recommendations
- Stress detection and management strategies
- Health scoring (0-100)

**Main Methods**:
```python
advisor = HealthAdvisor()
advisor.log_sleep(sleep_record)
advisor.log_exercise(exercise_session)
advisor.log_stress(stress_event)
report = advisor.get_health_report()
```

**Use Cases**:
- Poor sleep quality
- Inconsistent exercise
- High stress levels
- Health optimization

---

### 3. **Relationship Manager** (`relationship_manager.py`)

**Purpose**: Maintain healthy social connections

**Key Features**:
- Communication frequency tracking
- Check-in suggestions based on relationship importance
- Important date reminders (birthdays, anniversaries)
- Social isolation detection
- Relationship health scoring

**Main Methods**:
```python
manager = RelationshipManager()
manager.add_person(person)
manager.log_interaction(interaction)
suggestions = manager.get_check_in_suggestions()
isolation = manager.detect_isolation_patterns()
```

**Use Cases**:
- Losing touch with friends/family
- Forgetting important dates
- Social isolation
- Relationship maintenance

---

### 4. **Financial Planner** (`financial_planner.py`)

**Purpose**: Manage money, budget, and investments

**Key Features**:
- Spending pattern analysis by category
- Budget tracking with alerts (80% threshold)
- Financial goal tracking
- Investment portfolio analysis
- Unusual spending detection
- Financial health scoring (0-100)

**Main Methods**:
```python
planner = FinancialPlanner()
planner.add_transaction(transaction)
planner.set_budget(category, monthly_limit)
planner.add_goal(financial_goal)
report = planner.get_financial_report()
```

**Use Cases**:
- Budget overruns
- Unclear spending patterns
- Financial goal tracking
- Investment planning

---

### 5. **Learning Curator** (`learning_curator.py`)

**Purpose**: Optimize learning journey and skill development

**Key Features**:
- Course recommendations based on goals and skill level
- Study schedule optimization with spaced repetition
- Knowledge gap analysis
- Reading list prioritization
- Learning analytics and progress tracking

**Main Methods**:
```python
curator = LearningCurator()
curator.add_skill(skill)
curator.add_goal(learning_goal)
curator.log_study_session(session)
schedule = curator.optimize_study_schedule(days=7)
gaps = curator.analyze_knowledge_gaps()
```

**Use Cases**:
- Career development
- Skill acquisition
- Study optimization
- Knowledge gap identification

---

### 6. **Creative Catalyst** (`creative_catalyst.py`)

**Purpose**: Support and boost creative practice

**Key Features**:
- Creative time block suggestions based on productivity patterns
- Output tracking (words, songs, sketches, etc.)
- Creative block/slump detection
- Daily inspiration delivery (quotes, prompts, challenges)
- Creative health scoring (0-100)

**Main Methods**:
```python
catalyst = CreativeCatalyst()
catalyst.add_project(creative_project)
catalyst.log_session(creative_session)
blocks = catalyst.detect_creative_slumps()
inspiration = catalyst.get_daily_inspiration()
time_blocks = catalyst.suggest_creative_time_blocks(days=7)
```

**Use Cases**:
- Creative blocks
- Inconsistent creative practice
- Lack of inspiration
- Creative project management

---

## 🚀 Quick Start

### Installation

```python
# Import all agents
from integrations.Sophia import (
    ProductivityCoach,
    HealthAdvisor,
    RelationshipManager,
    FinancialPlanner,
    LearningCurator,
    CreativeCatalyst
)
```

### Basic Usage

```python
# Initialize agents
productivity = ProductivityCoach()
health = HealthAdvisor()
relationships = RelationshipManager()
finance = FinancialPlanner()
learning = LearningCurator()
creative = CreativeCatalyst()

# Use agents as needed
productivity.add_task(task)
health.log_sleep(sleep_record)
relationships.log_interaction(interaction)
finance.add_transaction(transaction)
learning.log_study_session(session)
creative.log_session(creative_session)

# Get comprehensive reports
productivity_report = productivity.get_productivity_report()
health_report = health.get_health_report()
relationship_report = relationships.get_relationship_report()
financial_report = finance.get_financial_report()
learning_report = learning.get_learning_report()
creative_report = creative.get_creative_report()
```

### Run Demo

```bash
cd integrations/Sophia
python demo_all_agents.py
```

---

## 📊 Scoring Systems

All agents use 0-100 scoring systems for easy comparison:

- **Productivity**: Efficiency Score (completion rate - penalties for distractions/switches)
- **Health**: Overall Health Score (sleep + exercise + stress + nutrition)
- **Relationships**: Relationship Health Score (frequency + quality + consistency)
- **Finance**: Financial Health Score (savings rate + budget adherence + goals + diversification)
- **Learning**: Learning Progress (consistency + volume + quality + breakthroughs)
- **Creative**: Creative Health Score (consistency + volume + mood + breakthroughs - blocks)

---

## 🎨 Color-Coded Alerts

All agents use consistent alert levels:

- 🔴 **CRITICAL/URGENT**: Immediate action required (score < 40, severe issues)
- 🟡 **WARNING/IMPORTANT**: Attention needed (score 40-60, moderate issues)
- 🟢 **GOOD/HEALTHY**: On track (score 60-80, minor improvements)
- ✅ **EXCELLENT**: Optimal performance (score > 80)

---

## 🔗 Integration Points

### Data Sources (Future)
- **Productivity**: Calendar APIs, task management tools (Todoist, Asana)
- **Health**: Fitness trackers (Apple Health, Fitbit), sleep apps
- **Relationships**: Contact lists, messaging apps, calendar
- **Finance**: Banking APIs (Plaid), investment platforms
- **Learning**: Course platforms (Coursera, Udemy), reading apps
- **Creative**: Project management tools, time tracking

### Notifications
- Daily summary reports
- Budget alerts (80% threshold)
- Check-in reminders
- Important date notifications
- Creative block warnings
- Goal progress updates

### Dashboard
- Unified view of all 6 agents
- Cross-agent insights (e.g., stress affecting productivity)
- Trend visualization
- Actionable recommendations

---

## 🧠 Advanced Features

### Cross-Agent Intelligence

Agents can inform each other:
- High stress (Health) → Reduce task load (Productivity)
- Social isolation (Relationships) → Schedule social activities
- Budget overrun (Finance) → Reduce entertainment spending
- Creative block (Creative) → Take a learning break (Learning)
- Poor sleep (Health) → Adjust study schedule (Learning)

### Personalization

Each agent learns from your patterns:
- Optimal work times
- Productive energy levels
- Preferred communication methods
- Spending habits
- Learning styles
- Creative rhythms

### Predictive Insights

Agents detect patterns before problems occur:
- Productivity slumps
- Health decline
- Relationship drift
- Budget overruns
- Learning plateaus
- Creative blocks

---

## 📝 Data Models

Each agent uses well-defined data models:

- **Productivity**: Task, TimeBlock, ContextSwitch
- **Health**: SleepRecord, ExerciseSession, StressEvent, NutritionLog
- **Relationships**: Person, Interaction, ImportantDate
- **Finance**: Transaction, Budget, FinancialGoal, Investment
- **Learning**: Skill, LearningGoal, LearningResource, StudySession
- **Creative**: CreativeProject, CreativeSession, CreativeBlock, Inspiration

All models use Python dataclasses for type safety and clarity.

---

## 🛠️ Customization

### Configuration Options

Each agent supports customization:

```python
# Productivity
coach.check_in_intervals = {...}  # Custom intervals by relationship type

# Health
advisor.target_sleep_hours = 8.0
advisor.target_exercise_minutes_per_week = 150

# Relationships
manager.check_in_intervals = {...}  # Custom intervals

# Finance
planner.monthly_income = 5000
planner.risk_tolerance = "moderate"  # conservative, moderate, aggressive

# Learning
curator.preferred_study_times = [(time(9,0), time(11,0))]
curator.max_daily_study_hours = 3.0

# Creative
catalyst.preferred_creative_times = [(time(6,0), time(9,0))]
catalyst.target_weekly_hours = 10.0
```

---

## 📚 Documentation

Each module includes:
- Comprehensive docstrings
- Type hints
- Example usage in `__main__`
- Demo script (`demo_all_agents.py`)

---

## 🎯 Roadmap

### Phase 1: Core Functionality ✅
- All 6 agents implemented
- Basic tracking and analysis
- Scoring systems
- Recommendations

### Phase 2: Integration (Next)
- Real data source connections
- Automated data collection
- Notification system
- Unified dashboard

### Phase 3: Intelligence
- Cross-agent insights
- Predictive analytics
- Machine learning models
- Personalized recommendations

### Phase 4: Automation
- Automatic task scheduling
- Smart reminders
- Proactive suggestions
- Goal auto-adjustment

---

## 💡 Tips for Best Results

1. **Consistency**: Log data regularly for accurate insights
2. **Honesty**: Accurate data = better recommendations
3. **Action**: Review reports and act on recommendations
4. **Patience**: Patterns emerge over time (2-4 weeks)
5. **Balance**: Use all 6 agents for holistic life optimization
6. **Customize**: Adjust thresholds and preferences to your needs

---

## 🤝 Contributing

To add new features:
1. Follow existing code patterns
2. Add type hints
3. Include docstrings
4. Update this guide
5. Add tests

---

## 📄 License

Part of the Singularis project.

---

## 📞 Support

For questions or issues, refer to the main Singularis documentation.
