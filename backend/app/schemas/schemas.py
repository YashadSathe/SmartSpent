from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime

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

class ExpenseResponse(ExpenseBase):
    id: int
    predicted_category: Optional[str] = None
    confidence: Optional[float] = None
    user_corrected: bool
    created_at: datetime
    
    # Pydantic V2 Syntax
    model_config = ConfigDict(from_attributes=True)

class BudgetBase(BaseModel):
    monthly_budget: float
    monthly_income: float
    model_config = ConfigDict(from_attributes=True)

class CategoryBudgetBase(BaseModel):
    category: str
    monthly_budget: float

class CategoryBudgetResponse(CategoryBudgetBase):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class ClassificationRequest(BaseModel):
    expense_name: str

class ClassificationResponse(BaseModel):
    category: str
    confidence: float
    suggested_categories: List[str] = []

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

class ReceiptItem(BaseModel):
    item_name: str
    amount: float

class ReceiptExtraction(BaseModel):
    merchant_name: str
    date: Optional[str] = None
    items: List[ReceiptItem]