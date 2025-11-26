from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile
from sqlalchemy.orm import Session
from typing import List, Optional
import datetime
from app.services.classification_service import HybridClassificationService
from app.services.database import get_db
from app.schemas import schemas, models
from app.models.rule_engine import RuleBasedClassifier
from app.services.receipt_scanner import ReceiptScannerService
from app.dependencies import get_hybrid_classifier_service

router = APIRouter(prefix="/api/expenses", tags=["expenses"])

@router.post("/", response_model=schemas.ExpenseResponse)
def create_expense(
    expense: schemas.ExpenseCreate, 
    db: Session = Depends(get_db),
    # Use the new singleton service
    classifier: HybridClassificationService = Depends(get_hybrid_classifier_service)
):
    
    # Auto-classify if category not provided
    predicted_category = None
    confidence = None
    used_ml = False
    
    if not expense.category and expense.expense_name:
        # Use the singleton classifier
        classification_result = classifier.classify(expense.expense_name)
        predicted_category = classification_result["final_category"]
        confidence = classification_result["final_confidence"]
        used_ml = classification_result["used_ml"]
        expense.category = predicted_category
    
    # Create expense in database
    db_expense = models.Expense(
        expense_name=expense.expense_name,
        amount=expense.amount,
        category=expense.category,
        predicted_category=predicted_category,
        confidence=confidence
    )
    
    db.add(db_expense)
    db.commit()
    db.refresh(db_expense)
    
    return db_expense

@router.post("/{expense_id}/record-correction")
def record_category_correction(
    expense_id: int,
    correction_data: dict,
    db: Session = Depends(get_db),
    # Get the singleton service
    classifier: HybridClassificationService = Depends(get_hybrid_classifier_service)
):
    """Record when user corrects the category of an expense"""
    db_expense = db.query(models.Expense).filter(models.Expense.id == expense_id).first()
    if not db_expense:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expense not found"
        )
    
    # Create a new service instance
    correction_service = HybridClassificationService(db, classifier.ml_classifier)
    
    # Record the correction for ML training
    correction_service.record_correction(
        db_expense.expense_name,
        db_expense.predicted_category or db_expense.category,  # What AI predicted
        correction_data["corrected_category"]  # What user set it to
    )
    
    # Mark the expense as user-corrected
    db_expense.user_corrected = True
    db.commit()
    
    return {"message": "Correction recorded for model training"}

@router.get("/", response_model=List[schemas.ExpenseResponse])
def get_all_expenses(
    skip: int = 0, 
    limit: int = 100,
    db: Session = Depends(get_db)
):
    expenses = db.query(models.Expense).order_by(models.Expense.created_at.desc()).offset(skip).limit(limit).all()
    return expenses

@router.get("/current-month", response_model=List[schemas.ExpenseResponse])
def get_current_month_expenses(db: Session = Depends(get_db)):
    # Get current month
    now = datetime.datetime.now()
    first_day = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    expenses = db.query(models.Expense).filter(
        models.Expense.created_at >= first_day
    ).order_by(models.Expense.created_at.desc()).all()
    
    return expenses

@router.get("/{expense_id}", response_model=schemas.ExpenseResponse)
def get_expense(expense_id: int, db: Session = Depends(get_db)):
    expense = db.query(models.Expense).filter(models.Expense.id == expense_id).first()
    if not expense:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expense not found"
        )
    return expense

@router.put("/{expense_id}", response_model=schemas.ExpenseResponse)
def update_expense(
    expense_id: int,
    expense_update: schemas.ExpenseUpdate,
    db: Session = Depends(get_db)
):
    db_expense = db.query(models.Expense).filter(models.Expense.id == expense_id).first()
    if not db_expense:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expense not found"
        )
    
    # Update fields if provided
    if expense_update.expense_name is not None:
        db_expense.expense_name = expense_update.expense_name
    if expense_update.amount is not None:
        db_expense.amount = expense_update.amount
    if expense_update.category is not None:
        # If category is changed, mark as user corrected
        if expense_update.category != db_expense.predicted_category:
            db_expense.user_corrected = True
        db_expense.category = expense_update.category
    
    db_expense.updated_at = datetime.datetime.now()
    
    db.commit()
    db.refresh(db_expense)
    
    return db_expense

@router.delete("/{expense_id}")
def delete_expense(expense_id: int, db: Session = Depends(get_db)):
    db_expense = db.query(models.Expense).filter(models.Expense.id == expense_id).first()
    if not db_expense:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expense not found"
        )
    
    db.delete(db_expense)
    db.commit()
    
    return {"message": "Expense deleted successfully"}

@router.post("/upload-receipt", response_model=dict)
async def upload_receipt(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    classifier: HybridClassificationService = Depends(get_hybrid_classifier_service)
):
    try:
        contents = await file.read()
        
        # Extract data using Gemini
        scanner = ReceiptScannerService()
        extraction = scanner.scan_receipt(contents)
        
        saved_expenses = []
        
        # Handle Date Parsing
        expense_date = datetime.datetime.now()
        if extraction.date:
            try:
                # Simple ISO format parser
                expense_date = datetime.datetime.fromisoformat(str(extraction.date).replace('Z', ''))
            except Exception:
                pass
        
        # Process items
        for item in extraction.items:
            classification = classifier.classify(item.item_name)
            
            new_expense = models.Expense(
                expense_name=f"{extraction.merchant_name} - {item.item_name}",
                amount=item.amount,
                category=classification["final_category"],
                predicted_category=classification["final_category"],
                confidence=classification["final_confidence"],
                created_at=expense_date
            )
            
            db.add(new_expense)
            saved_expenses.append(new_expense)
            
        db.commit()
        
        return {
            "message": f"Successfully processed receipt from {extraction.merchant_name}",
            "items_count": len(saved_expenses),
            "extracted_data": extraction
        }
        
    except Exception as e:
        print(f"UPLOAD ERROR: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Receipt scanning failed: {str(e)}")