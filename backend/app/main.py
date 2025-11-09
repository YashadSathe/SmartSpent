from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
import datetime
from fastapi.middleware.cors import CORSMiddleware
from app.services.database import get_db, create_tables
from app.schemas import schemas, models
from app.models.rule_engine import RuleBasedClassifier
from app.api import expenses, classification, budget, dashboard


app = FastAPI(
    title="Expense Tracker API", 
    description = "AI-powered expense tracking and categorization system",
    version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # React frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(expenses.router)
app.include_router(classification.router)
app.include_router(budget.router)
app.include_router(dashboard.router)

# Initialize classifier
classifier = RuleBasedClassifier()

# Create tables on startup
@app.on_event("startup")
def on_startup():
    create_tables()

# Health check
@app.get("/")
def read_root():
    return {"message": "Expense Tracker API is running!"}

# # Expense endpoints
# @app.post("/api/expenses", response_model=schemas.ExpenseResponse)
# def create_expense(expense: schemas.ExpenseCreate, db: Session = Depends(get_db)):
#     # Auto-classify if category not provided
#     if not expense.category and expense.expense_name:
#         predicted_category, confidence = classifier.classify(expense.expense_name)
#         expense.category = predicted_category
#         expense.predicted_category = predicted_category
#         expense.confidence = confidence
    
#     # Create expense in database
#     db_expense = models.Expense(
#         expense_name=expense.expense_name,
#         amount=expense.amount,
#         category=expense.category,
#         predicted_category=getattr(expense, 'predicted_category', None),
#         confidence=getattr(expense, 'confidence', None)
#     )
    
#     db.add(db_expense)
#     db.commit()
#     db.refresh(db_expense)
    
#     return db_expense

# @app.get("/api/expenses/current-month", response_model=List[schemas.ExpenseResponse])
# def get_current_month_expenses(db: Session = Depends(get_db)):
#     # Get current month expenses
#     current_month = datetime.datetime.now().strftime("%Y-%m")
#     expenses = db.query(models.Expense).filter(
#         models.Expense.created_at >= f"{current_month}-01"
#     ).all()
    
#     return expenses

# # Classification endpoint
# @app.post("/api/classify", response_model=schemas.ClassificationResponse)
# def classify_expense(request: schemas.ClassificationRequest):
#     category, confidence = classifier.classify(request.expense_name)
#     suggested_categories = classifier.get_suggested_categories(request.expense_name)
    
#     return schemas.ClassificationResponse(
#         category=category,
#         confidence=confidence,
#         suggested_categories=suggested_categories
#     )

# # Budget endpoints
# @app.post("/api/budget/overall")
# def set_overall_budget(budget: schemas.BudgetBase, db: Session = Depends(get_db)):
#     db_budget = db.query(models.OverallBudget).first()
    
#     if db_budget:
#         db_budget.monthly_budget = budget.monthly_budget
#         db_budget.monthly_income = budget.monthly_income
#     else:
#         db_budget = models.OverallBudget(
#             monthly_budget=budget.monthly_budget,
#             monthly_income=budget.monthly_income
#         )
#         db.add(db_budget)
    
#     db.commit()
#     return {"message": "Overall budget updated successfully"}

# @app.get("/api/budget/overall")
# def get_overall_budget(db: Session = Depends(get_db)):
#     budget = db.query(models.OverallBudget).first()
#     if not budget:
#         return {"monthly_budget": 0.0, "monthly_income": 0.0}
#     return budget

# # Dashboard endpoints
# @app.get("/api/dashboard/summary")
# def get_dashboard_summary(db: Session = Depends(get_db)):
#     # Get current month
#     current_month = datetime.datetime.now().strftime("%Y-%m")
    
#     # Calculate total spent this month
#     expenses = db.query(models.Expense).filter(
#         models.Expense.created_at >= f"{current_month}-01"
#     ).all()
    
#     total_spent = sum(exp.amount for exp in expenses)
    
#     # Get overall budget
#     budget = db.query(models.OverallBudget).first()
#     total_budget = budget.monthly_budget if budget else 0
#     monthly_income = budget.monthly_income if budget else 0
    
#     # Calculate metrics
#     budget_utilization = (total_spent / total_budget * 100) if total_budget > 0 else 0
#     savings = monthly_income - total_spent if monthly_income > 0 else 0
#     savings_rate = (savings / monthly_income * 100) if monthly_income > 0 else 0
    
#     return {
#         "total_spent": total_spent,
#         "total_budget": total_budget,
#         "budget_utilization": budget_utilization,
#         "savings": savings,
#         "savings_rate": savings_rate
#     }