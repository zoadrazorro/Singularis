"""
Financial Planner Agent - Spending patterns, budget tracking, investment suggestions, and goal tracking.

This agent analyzes your financial patterns, helps you stay on budget, and provides
personalized investment and savings recommendations.
"""

from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import statistics


class TransactionType(Enum):
    """Types of financial transactions."""
    INCOME = "income"
    EXPENSE = "expense"
    TRANSFER = "transfer"
    INVESTMENT = "investment"


class ExpenseCategory(Enum):
    """Expense categories."""
    HOUSING = "housing"
    TRANSPORTATION = "transportation"
    FOOD = "food"
    UTILITIES = "utilities"
    HEALTHCARE = "healthcare"
    ENTERTAINMENT = "entertainment"
    SHOPPING = "shopping"
    EDUCATION = "education"
    SAVINGS = "savings"
    DEBT_PAYMENT = "debt_payment"
    OTHER = "other"


class InvestmentType(Enum):
    """Types of investments."""
    STOCKS = "stocks"
    BONDS = "bonds"
    REAL_ESTATE = "real_estate"
    CRYPTO = "crypto"
    RETIREMENT = "retirement"
    INDEX_FUNDS = "index_funds"
    OTHER = "other"


class GoalStatus(Enum):
    """Financial goal status."""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    ON_TRACK = "on_track"
    BEHIND = "behind"
    COMPLETED = "completed"


@dataclass
class Transaction:
    """Represents a financial transaction."""
    id: str
    date: datetime
    amount: float
    transaction_type: TransactionType
    category: Optional[ExpenseCategory] = None
    description: str = ""
    merchant: str = ""
    recurring: bool = False


@dataclass
class Budget:
    """Represents a budget for a category."""
    category: ExpenseCategory
    monthly_limit: float
    current_spent: float = 0.0
    alerts_enabled: bool = True
    alert_threshold: float = 0.8  # Alert at 80% of budget


@dataclass
class FinancialGoal:
    """Represents a financial goal."""
    id: str
    name: str
    target_amount: float
    current_amount: float = 0.0
    deadline: Optional[datetime] = None
    priority: int = 5  # 1-10
    category: str = "general"
    monthly_contribution: float = 0.0
    status: GoalStatus = GoalStatus.NOT_STARTED


@dataclass
class Investment:
    """Represents an investment holding."""
    id: str
    name: str
    investment_type: InvestmentType
    amount_invested: float
    current_value: float
    purchase_date: datetime
    notes: str = ""


class FinancialPlanner:
    """
    Financial Planner Agent that helps manage money, budget, and investments.
    
    Features:
    - Track spending patterns and categorize expenses
    - Monitor budget vs reality with alerts
    - Provide investment suggestions based on goals
    - Track progress toward financial goals
    - Detect unusual spending patterns
    """
    
    def __init__(self):
        self.transactions: List[Transaction] = []
        self.budgets: Dict[ExpenseCategory, Budget] = {}
        self.goals: Dict[str, FinancialGoal] = {}
        self.investments: List[Investment] = []
        
        # Financial profile
        self.monthly_income: float = 0.0
        self.emergency_fund_target: float = 0.0  # 3-6 months expenses
        self.risk_tolerance: str = "moderate"  # conservative, moderate, aggressive
    
    # ============================================================================
    # TRANSACTION MANAGEMENT
    # ============================================================================
    
    def add_transaction(self, transaction: Transaction) -> None:
        """Add a transaction."""
        self.transactions.append(transaction)
        
        # Update budget if it's an expense
        if transaction.transaction_type == TransactionType.EXPENSE and transaction.category:
            if transaction.category in self.budgets:
                self.budgets[transaction.category].current_spent += transaction.amount
    
    def get_transactions(self, 
                        start_date: Optional[datetime] = None,
                        end_date: Optional[datetime] = None,
                        category: Optional[ExpenseCategory] = None) -> List[Transaction]:
        """Get filtered transactions."""
        filtered = self.transactions
        
        if start_date:
            filtered = [t for t in filtered if t.date >= start_date]
        if end_date:
            filtered = [t for t in filtered if t.date <= end_date]
        if category:
            filtered = [t for t in filtered if t.category == category]
        
        return filtered
    
    # ============================================================================
    # SPENDING ANALYSIS
    # ============================================================================
    
    def analyze_spending_patterns(self, days: int = 30) -> Dict:
        """
        Analyze spending patterns over the last N days.
        
        Returns breakdown by category, trends, and insights.
        """
        cutoff = datetime.now() - timedelta(days=days)
        expenses = [t for t in self.transactions 
                   if t.transaction_type == TransactionType.EXPENSE and t.date > cutoff]
        
        if not expenses:
            return {'error': 'No expense data available'}
        
        # Total spending
        total_spent = sum(t.amount for t in expenses)
        avg_daily = total_spent / days
        avg_monthly = avg_daily * 30
        
        # Category breakdown
        category_totals = {}
        for expense in expenses:
            if expense.category:
                cat = expense.category.value
                category_totals[cat] = category_totals.get(cat, 0) + expense.amount
        
        # Sort by amount
        category_breakdown = sorted(
            [{'category': k, 'amount': v, 'percentage': (v/total_spent)*100} 
             for k, v in category_totals.items()],
            key=lambda x: x['amount'],
            reverse=True
        )
        
        # Detect recurring expenses
        recurring_expenses = [t for t in expenses if t.recurring]
        recurring_total = sum(t.amount for t in recurring_expenses)
        
        # Compare to previous period
        previous_cutoff = cutoff - timedelta(days=days)
        previous_expenses = [t for t in self.transactions 
                            if t.transaction_type == TransactionType.EXPENSE 
                            and previous_cutoff < t.date < cutoff]
        previous_total = sum(t.amount for t in previous_expenses)
        
        spending_change = ((total_spent - previous_total) / previous_total * 100) if previous_total else 0
        
        return {
            'total_spent': round(total_spent, 2),
            'avg_daily_spending': round(avg_daily, 2),
            'projected_monthly': round(avg_monthly, 2),
            'category_breakdown': category_breakdown,
            'recurring_expenses': round(recurring_total, 2),
            'spending_change_vs_previous': round(spending_change, 1),
            'insights': self._generate_spending_insights(expenses, category_breakdown, spending_change)
        }
    
    def _generate_spending_insights(self, 
                                    expenses: List[Transaction],
                                    category_breakdown: List[Dict],
                                    spending_change: float) -> List[str]:
        """Generate insights about spending patterns."""
        insights = []
        
        # Spending trend
        if spending_change > 20:
            insights.append(f"⚠️ Spending increased {spending_change:.1f}% compared to previous period")
        elif spending_change < -20:
            insights.append(f"✅ Great job! Spending decreased {abs(spending_change):.1f}%")
        
        # Top spending categories
        if category_breakdown:
            top_category = category_breakdown[0]
            insights.append(f"Top spending: {top_category['category']} (${top_category['amount']:.2f}, {top_category['percentage']:.1f}%)")
            
            # Check if any category is disproportionately high
            if top_category['percentage'] > 40:
                insights.append(f"⚠️ {top_category['category']} is {top_category['percentage']:.1f}% of spending - consider reducing")
        
        # Unusual transactions
        amounts = [t.amount for t in expenses]
        if amounts:
            avg_amount = statistics.mean(amounts)
            large_transactions = [t for t in expenses if t.amount > avg_amount * 3]
            if large_transactions:
                insights.append(f"⚠️ {len(large_transactions)} unusually large transactions detected")
        
        return insights
    
    def detect_unusual_spending(self, days: int = 7) -> List[Dict]:
        """Detect unusual spending patterns."""
        cutoff = datetime.now() - timedelta(days=days)
        recent_expenses = [t for t in self.transactions 
                          if t.transaction_type == TransactionType.EXPENSE and t.date > cutoff]
        
        # Get historical average for comparison
        historical_cutoff = cutoff - timedelta(days=90)
        historical_expenses = [t for t in self.transactions 
                              if t.transaction_type == TransactionType.EXPENSE 
                              and historical_cutoff < t.date < cutoff]
        
        if not historical_expenses:
            return []
        
        unusual = []
        
        # Check for unusually large transactions
        historical_amounts = [t.amount for t in historical_expenses]
        avg_amount = statistics.mean(historical_amounts)
        std_amount = statistics.stdev(historical_amounts) if len(historical_amounts) > 1 else 0
        
        for expense in recent_expenses:
            if expense.amount > avg_amount + (2 * std_amount):  # 2 standard deviations
                unusual.append({
                    'transaction': expense,
                    'reason': f'Unusually large amount (${expense.amount:.2f} vs avg ${avg_amount:.2f})',
                    'severity': 'high' if expense.amount > avg_amount * 3 else 'medium'
                })
        
        # Check for unusual category spending
        for category in ExpenseCategory:
            recent_cat = sum(t.amount for t in recent_expenses if t.category == category)
            historical_cat = sum(t.amount for t in historical_expenses if t.category == category)
            
            if historical_cat > 0:
                avg_cat_weekly = historical_cat / (90 / 7)
                if recent_cat > avg_cat_weekly * 2:
                    unusual.append({
                        'category': category.value,
                        'reason': f'Spending in {category.value} is 2x normal (${recent_cat:.2f} vs avg ${avg_cat_weekly:.2f})',
                        'severity': 'medium'
                    })
        
        return unusual
    
    # ============================================================================
    # BUDGET MANAGEMENT
    # ============================================================================
    
    def set_budget(self, category: ExpenseCategory, monthly_limit: float) -> None:
        """Set or update budget for a category."""
        if category in self.budgets:
            self.budgets[category].monthly_limit = monthly_limit
        else:
            self.budgets[category] = Budget(
                category=category,
                monthly_limit=monthly_limit
            )
    
    def check_budget_status(self) -> Dict:
        """Check status of all budgets."""
        status = {}
        
        # Get current month's spending
        month_start = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        month_expenses = [t for t in self.transactions 
                         if t.transaction_type == TransactionType.EXPENSE 
                         and t.date >= month_start]
        
        for category, budget in self.budgets.items():
            # Calculate current spending
            spent = sum(t.amount for t in month_expenses if t.category == category)
            remaining = budget.monthly_limit - spent
            percentage = (spent / budget.monthly_limit * 100) if budget.monthly_limit > 0 else 0
            
            # Determine status
            if percentage >= 100:
                budget_status = "OVER_BUDGET"
            elif percentage >= budget.alert_threshold * 100:
                budget_status = "WARNING"
            elif percentage >= 50:
                budget_status = "ON_TRACK"
            else:
                budget_status = "UNDER_BUDGET"
            
            status[category.value] = {
                'limit': budget.monthly_limit,
                'spent': round(spent, 2),
                'remaining': round(remaining, 2),
                'percentage': round(percentage, 1),
                'status': budget_status
            }
        
        return status
    
    def get_budget_alerts(self) -> List[str]:
        """Get budget alerts for categories approaching or exceeding limits."""
        alerts = []
        budget_status = self.check_budget_status()
        
        for category, status in budget_status.items():
            if status['status'] == 'OVER_BUDGET':
                alerts.append(f"🔴 {category}: OVER BUDGET by ${abs(status['remaining']):.2f}")
            elif status['status'] == 'WARNING':
                alerts.append(f"⚠️ {category}: {status['percentage']:.1f}% of budget used (${status['remaining']:.2f} remaining)")
        
        return alerts
    
    # ============================================================================
    # FINANCIAL GOALS
    # ============================================================================
    
    def add_goal(self, goal: FinancialGoal) -> None:
        """Add a financial goal."""
        self.goals[goal.id] = goal
    
    def update_goal_progress(self, goal_id: str, amount: float) -> None:
        """Update progress toward a goal."""
        if goal_id in self.goals:
            self.goals[goal_id].current_amount += amount
            self._update_goal_status(goal_id)
    
    def _update_goal_status(self, goal_id: str) -> None:
        """Update goal status based on progress."""
        goal = self.goals[goal_id]
        
        if goal.current_amount >= goal.target_amount:
            goal.status = GoalStatus.COMPLETED
            return
        
        if goal.current_amount == 0:
            goal.status = GoalStatus.NOT_STARTED
            return
        
        # Calculate if on track
        if goal.deadline:
            months_remaining = (goal.deadline - datetime.now()).days / 30
            if months_remaining > 0:
                required_monthly = (goal.target_amount - goal.current_amount) / months_remaining
                
                if goal.monthly_contribution >= required_monthly * 0.9:
                    goal.status = GoalStatus.ON_TRACK
                else:
                    goal.status = GoalStatus.BEHIND
            else:
                goal.status = GoalStatus.BEHIND
        else:
            goal.status = GoalStatus.IN_PROGRESS
    
    def analyze_goal_progress(self, goal_id: str) -> Dict:
        """Analyze progress toward a specific goal."""
        if goal_id not in self.goals:
            return {'error': 'Goal not found'}
        
        goal = self.goals[goal_id]
        progress_percentage = (goal.current_amount / goal.target_amount * 100) if goal.target_amount > 0 else 0
        remaining = goal.target_amount - goal.current_amount
        
        # Calculate timeline
        if goal.monthly_contribution > 0:
            months_to_completion = remaining / goal.monthly_contribution
        else:
            months_to_completion = None
        
        # Check if on track for deadline
        on_track = True
        if goal.deadline:
            months_until_deadline = (goal.deadline - datetime.now()).days / 30
            if months_to_completion and months_to_completion > months_until_deadline:
                on_track = False
        
        return {
            'goal_name': goal.name,
            'target_amount': goal.target_amount,
            'current_amount': goal.current_amount,
            'remaining': round(remaining, 2),
            'progress_percentage': round(progress_percentage, 1),
            'monthly_contribution': goal.monthly_contribution,
            'months_to_completion': round(months_to_completion, 1) if months_to_completion else 'Unknown',
            'deadline': goal.deadline.strftime('%Y-%m-%d') if goal.deadline else 'No deadline',
            'on_track': on_track,
            'status': goal.status.value,
            'recommendations': self._generate_goal_recommendations(goal, on_track, months_to_completion)
        }
    
    def _generate_goal_recommendations(self, 
                                      goal: FinancialGoal,
                                      on_track: bool,
                                      months_to_completion: Optional[float]) -> List[str]:
        """Generate recommendations for achieving a goal."""
        recs = []
        
        if goal.status == GoalStatus.COMPLETED:
            recs.append("🎉 Goal completed! Consider setting a new goal.")
            return recs
        
        if not on_track and goal.deadline:
            months_remaining = (goal.deadline - datetime.now()).days / 30
            required_monthly = (goal.target_amount - goal.current_amount) / months_remaining if months_remaining > 0 else 0
            recs.append(f"⚠️ Behind schedule. Increase monthly contribution to ${required_monthly:.2f}")
        
        if goal.monthly_contribution == 0:
            recs.append("Set up automatic monthly contributions to stay on track")
        
        # Suggest ways to increase contributions
        if goal.monthly_contribution < (goal.target_amount - goal.current_amount) / 12:
            recs.append("Look for areas to cut spending and redirect to this goal")
            recs.append("Consider a side income stream to accelerate progress")
        
        return recs
    
    # ============================================================================
    # INVESTMENT SUGGESTIONS
    # ============================================================================
    
    def add_investment(self, investment: Investment) -> None:
        """Add an investment to portfolio."""
        self.investments.append(investment)
    
    def analyze_portfolio(self) -> Dict:
        """Analyze investment portfolio."""
        if not self.investments:
            return {'error': 'No investments tracked'}
        
        total_invested = sum(i.amount_invested for i in self.investments)
        total_current = sum(i.current_value for i in self.investments)
        total_return = total_current - total_invested
        return_percentage = (total_return / total_invested * 100) if total_invested > 0 else 0
        
        # Breakdown by type
        type_breakdown = {}
        for investment in self.investments:
            inv_type = investment.investment_type.value
            if inv_type not in type_breakdown:
                type_breakdown[inv_type] = {'invested': 0, 'current': 0}
            type_breakdown[inv_type]['invested'] += investment.amount_invested
            type_breakdown[inv_type]['current'] += investment.current_value
        
        # Calculate diversification score (higher is better)
        diversification_score = len(type_breakdown) / len(InvestmentType) * 100
        
        return {
            'total_invested': round(total_invested, 2),
            'total_current_value': round(total_current, 2),
            'total_return': round(total_return, 2),
            'return_percentage': round(return_percentage, 2),
            'diversification_score': round(diversification_score, 1),
            'type_breakdown': type_breakdown,
            'recommendations': self._generate_investment_recommendations(type_breakdown, diversification_score)
        }
    
    def _generate_investment_recommendations(self, 
                                            type_breakdown: Dict,
                                            diversification_score: float) -> List[str]:
        """Generate investment recommendations."""
        recs = []
        
        # Diversification
        if diversification_score < 30:
            recs.append("⚠️ Low diversification. Consider spreading investments across more asset types.")
        elif diversification_score < 50:
            recs.append("Consider adding more asset types for better diversification")
        
        # Risk-based recommendations
        if self.risk_tolerance == "conservative":
            recs.extend([
                "Focus on bonds and index funds for stability",
                "Keep 3-6 months expenses in emergency fund",
                "Consider high-yield savings accounts"
            ])
        elif self.risk_tolerance == "moderate":
            recs.extend([
                "Balance between stocks (60%) and bonds (40%)",
                "Consider low-cost index funds (S&P 500, total market)",
                "Maintain emergency fund before aggressive investing"
            ])
        else:  # aggressive
            recs.extend([
                "Higher stock allocation (80-90%) for growth",
                "Consider individual stocks alongside index funds",
                "Explore growth sectors (tech, healthcare, renewable energy)"
            ])
        
        # General recommendations
        recs.extend([
            "Maximize employer 401(k) match if available",
            "Consider tax-advantaged accounts (IRA, Roth IRA)",
            "Rebalance portfolio annually"
        ])
        
        return recs[:5]
    
    def suggest_investment_allocation(self, amount: float) -> Dict[str, float]:
        """Suggest how to allocate a lump sum investment."""
        allocation = {}
        
        if self.risk_tolerance == "conservative":
            allocation = {
                'bonds': amount * 0.50,
                'index_funds': amount * 0.30,
                'savings': amount * 0.20
            }
        elif self.risk_tolerance == "moderate":
            allocation = {
                'index_funds': amount * 0.50,
                'stocks': amount * 0.25,
                'bonds': amount * 0.20,
                'savings': amount * 0.05
            }
        else:  # aggressive
            allocation = {
                'stocks': amount * 0.50,
                'index_funds': amount * 0.30,
                'crypto': amount * 0.10,
                'bonds': amount * 0.10
            }
        
        return {k: round(v, 2) for k, v in allocation.items()}
    
    # ============================================================================
    # FINANCIAL HEALTH REPORT
    # ============================================================================
    
    def get_financial_report(self) -> Dict:
        """Generate comprehensive financial report."""
        spending = self.analyze_spending_patterns(30)
        budget_status = self.check_budget_status()
        
        # Calculate savings rate
        month_start = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        month_income = sum(t.amount for t in self.transactions 
                          if t.transaction_type == TransactionType.INCOME and t.date >= month_start)
        month_expenses = spending.get('total_spent', 0)
        savings_rate = ((month_income - month_expenses) / month_income * 100) if month_income > 0 else 0
        
        # Goal progress
        goal_summary = {
            'total_goals': len(self.goals),
            'completed': len([g for g in self.goals.values() if g.status == GoalStatus.COMPLETED]),
            'on_track': len([g for g in self.goals.values() if g.status == GoalStatus.ON_TRACK]),
            'behind': len([g for g in self.goals.values() if g.status == GoalStatus.BEHIND])
        }
        
        # Portfolio
        portfolio = self.analyze_portfolio() if self.investments else None
        
        return {
            'monthly_income': round(month_income, 2),
            'monthly_expenses': round(month_expenses, 2),
            'savings_rate': round(savings_rate, 1),
            'spending_analysis': spending,
            'budget_status': budget_status,
            'budget_alerts': self.get_budget_alerts(),
            'goal_summary': goal_summary,
            'portfolio': portfolio,
            'financial_health_score': self._calculate_financial_health_score(savings_rate, budget_status, goal_summary),
            'top_recommendations': self._get_top_financial_recommendations()
        }
    
    def _calculate_financial_health_score(self, 
                                         savings_rate: float,
                                         budget_status: Dict,
                                         goal_summary: Dict) -> float:
        """Calculate overall financial health score (0-100)."""
        score = 0
        
        # Savings rate (0-30 points)
        if savings_rate >= 20:
            score += 30
        elif savings_rate >= 10:
            score += 20
        elif savings_rate >= 5:
            score += 10
        
        # Budget adherence (0-30 points)
        if budget_status:
            over_budget = sum(1 for s in budget_status.values() if s['status'] == 'OVER_BUDGET')
            on_track = sum(1 for s in budget_status.values() if s['status'] in ['ON_TRACK', 'UNDER_BUDGET'])
            total = len(budget_status)
            score += (on_track / total * 30) if total > 0 else 0
        
        # Goal progress (0-20 points)
        if goal_summary['total_goals'] > 0:
            goal_score = (goal_summary['completed'] + goal_summary['on_track']) / goal_summary['total_goals'] * 20
            score += goal_score
        
        # Investment diversification (0-20 points)
        if self.investments:
            portfolio = self.analyze_portfolio()
            score += (portfolio['diversification_score'] / 100 * 20)
        
        return round(score, 1)
    
    def _get_top_financial_recommendations(self) -> List[str]:
        """Get top financial recommendations."""
        recs = []
        
        # Check emergency fund
        if not self.emergency_fund_target or self.emergency_fund_target == 0:
            recs.append("🔴 Set up emergency fund (3-6 months expenses)")
        
        # Check budget alerts
        alerts = self.get_budget_alerts()
        if alerts:
            recs.extend(alerts[:2])
        
        # Check goals
        behind_goals = [g for g in self.goals.values() if g.status == GoalStatus.BEHIND]
        if behind_goals:
            recs.append(f"⚠️ {len(behind_goals)} financial goals are behind schedule")
        
        # Check savings rate
        report = self.get_financial_report()
        if report['savings_rate'] < 10:
            recs.append("Increase savings rate to at least 10-20% of income")
        
        return recs[:5]


if __name__ == "__main__":
    # Demo usage
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
    
    # Set budgets
    planner.set_budget(ExpenseCategory.HOUSING, 1300)
    planner.set_budget(ExpenseCategory.FOOD, 500)
    
    # Add goal
    planner.add_goal(FinancialGoal(
        id="1",
        name="Emergency Fund",
        target_amount=15000,
        current_amount=5000,
        deadline=datetime.now() + timedelta(days=365),
        monthly_contribution=500
    ))
    
    # Generate report
    print("=== FINANCIAL REPORT ===")
    report = planner.get_financial_report()
    print(f"Monthly Income: ${report['monthly_income']}")
    print(f"Monthly Expenses: ${report['monthly_expenses']}")
    print(f"Savings Rate: {report['savings_rate']}%")
    print(f"Financial Health Score: {report['financial_health_score']}/100")
    
    print("\nTop Recommendations:")
    for rec in report['top_recommendations']:
        print(f"  - {rec}")
