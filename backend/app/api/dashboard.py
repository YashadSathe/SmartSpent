from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import datetime
from typing import List, Dict, Any

from app.services.database import get_db
from app.schemas import schemas, models

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])

@router.get("/summary", response_model=schemas.DashboardSummary)
def get_dashboard_summary(db: Session = Depends(get_db)):
    # Get current month
    now = datetime.datetime.now()
    first_day = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    # Calculate total spent this month
    expenses = db.query(models.Expense).filter(
        models.Expense.created_at >= first_day
    ).all()
    
    total_spent = sum(exp.amount for exp in expenses)
    
    # Get overall budget
    budget = db.query(models.OverallBudget).first()
    total_budget = budget.monthly_budget if budget else 0.0
    monthly_income = budget.monthly_income if budget else 0.0
    
    # Calculate metrics
    budget_utilization = round((total_spent / total_budget * 100), 2) if total_budget > 0 else 0.0
    savings = round(monthly_income - total_spent, 2) if monthly_income > 0 else 0.0
    savings_rate = round((savings / monthly_income * 100), 2) if monthly_income > 0 else 0.0
    
    return {
        "total_spent": round(total_spent, 2),
        "total_budget": total_budget,
        "budget_utilization": budget_utilization,
        "savings": savings,
        "savings_rate": savings_rate,
        "total_income": monthly_income
    }

@router.get("/category-spending")
def get_category_spending(db: Session = Depends(get_db)):
    # Get current month
    now = datetime.datetime.now()
    first_day = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    # Get expenses for current month
    expenses = db.query(models.Expense).filter(
        models.Expense.created_at >= first_day
    ).all()
    
    # Calculate spending per category
    category_spending: Dict[str, float] = {}
    for expense in expenses:
        category_spending[expense.category] = category_spending.get(expense.category, 0) + expense.amount
    
    # Get category budgets
    category_budgets = db.query(models.CategoryBudget).all()
    budget_dict = {budget.category: budget.monthly_budget for budget in category_budgets}
    
    # Prepare response
    result = []
    for category in models.DEFAULT_CATEGORIES:
        spent = round(category_spending.get(category, 0.0), 2)
        budget = budget_dict.get(category, 0.0)
        remaining = round(budget - spent, 2)
        utilization = round((spent / budget * 100), 2) if budget > 0 else 0.0
        
        result.append({
            "category": category,
            "spent": spent,
            "budget": budget,
            "remaining": remaining,
            "utilization": utilization
        })
    
    return result

@router.get("/recent-expenses")
def get_recent_expenses(db: Session = Depends(get_db)):
    expenses = db.query(models.Expense).order_by(
        models.Expense.created_at.desc()
    ).limit(10).all()
    
    return expenses