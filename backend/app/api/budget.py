from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.services.database import get_db
from app.schemas import schemas, models

router = APIRouter(prefix="/api/budget", tags=["budget"])

# Overall Budget Endpoints
@router.post("/overall")
def set_overall_budget(budget: schemas.BudgetBase, db: Session = Depends(get_db)):
    db_budget = db.query(models.OverallBudget).first()
    
    if db_budget:
        db_budget.monthly_budget = budget.monthly_budget
        db_budget.monthly_income = budget.monthly_income
    else:
        db_budget = models.OverallBudget(
            monthly_budget=budget.monthly_budget,
            monthly_income=budget.monthly_income
        )
        db.add(db_budget)
    
    db.commit()
    return {"message": "Overall budget updated successfully"}

@router.get("/overall", response_model=schemas.BudgetBase)
def get_overall_budget(db: Session = Depends(get_db)):
    budget = db.query(models.OverallBudget).first()
    if not budget:
        return {"monthly_budget": 0.0, "monthly_income": 0.0}
    return budget

# Category Budget Endpoints
@router.post("/category", response_model=schemas.CategoryBudgetResponse)
def set_category_budget(
    budget: schemas.CategoryBudgetBase, 
    db: Session = Depends(get_db)
):
    # Check if category exists in our predefined list
    if budget.category not in models.DEFAULT_CATEGORIES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid category. Must be one of: {models.DEFAULT_CATEGORIES}"
        )
    
    db_budget = db.query(models.CategoryBudget).filter(
        models.CategoryBudget.category == budget.category
    ).first()
    
    if db_budget:
        db_budget.monthly_budget = budget.monthly_budget
    else:
        db_budget = models.CategoryBudget(
            category=budget.category,
            monthly_budget=budget.monthly_budget
        )
        db.add(db_budget)
    
    db.commit()
    db.refresh(db_budget)
    return db_budget

@router.get("/categories", response_model=List[schemas.CategoryBudgetResponse])
def get_all_category_budgets(db: Session = Depends(get_db)):
    budgets = db.query(models.CategoryBudget).all()
    return budgets

@router.get("/category/{category}")
def get_category_budget(category: str, db: Session = Depends(get_db)):
    budget = db.query(models.CategoryBudget).filter(
        models.CategoryBudget.category == category
    ).first()
    
    if not budget:
        return {"category": category, "monthly_budget": 0.0}
    
    return budget