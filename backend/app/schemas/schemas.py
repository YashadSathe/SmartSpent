from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

# Expense Schemas
class ExpenseBase(BaseModel):
    expense_name: str
    amount: float
    category: Optional[str] = None

class ExpenseCreate(ExpenseBase):
    pass

class ExpenseUpdate(BaseModel):
    expense_name: str
    amount: float
    category: Optional[str] = None

class ExpenseResponse(BaseModel):
    id: int
    predicted_category: Optional[str] = None
    confidence: Optional[str] = None
    user_corrected: bool
    created_at:datetime

    class Config:
        orm_mode = True

# budget Schemas

class BudgetBase(BaseModel):
    monthly_budget: float
    monthly_income: float

class CategoryBudgetBase(BaseModel):
    category: str
    monthly_budget: float

class CategoryBudgetResponse(CategoryBudgetBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True

# Classification Schemas
class ClassificationRequest(BaseModel):
    expense_name: str


class ClassificationResponse(BaseModel):
    category: str
    confidence: float
    suggested_categories: list[str] = []

# Dashboard Schemas

class DashboardSummary(BaseModel):
    total_spent: float
    total_budget: float
    budget_utilization: float 
    savings: float
    savings_rate: float
    total_income: float

class CategorySpending(BaseModel):
    category: str
    spent: float
    budget: float
    remaining: float
    utilization: float

class MonthlySpending(BaseModel):
    month: str
    total_spent: float
    savings_rate: float 