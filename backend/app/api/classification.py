from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any

from app.services.database import get_db
from app.services.classification_service import HybridClassificationService
from app.schemas import schemas

router = APIRouter(prefix="/api/classification", tags=["classification"])

@router.post("/predict", response_model=schemas.ClassificationResponse)
def classify_expense(
    request: schemas.ClassificationRequest, 
    db: Session = Depends(get_db)
):
    """Classify expense with hybrid ML + rule-based approach"""
    try:
        classification_service = HybridClassificationService(db)
        result = classification_service.classify(request.expense_name)
        
        return schemas.ClassificationResponse(
            category=result["final_category"],
            confidence=result["final_confidence"],
            suggested_categories=result["suggested_categories"],
            metadata={
                "used_ml": result["used_ml"],
                "ml_available": result["ml_available"],
                "ml_confidence": result.get("ml_result", {}).get("confidence"),
                "rule_confidence": result.get("rule_result", {}).get("confidence")
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Classification failed: {str(e)}")

@router.post("/batch-predict")
def batch_classify_expenses(
    requests: List[schemas.ClassificationRequest],
    db: Session = Depends(get_db)
):
    """Classify multiple expenses at once"""
    try:
        classification_service = HybridClassificationService(db)
        expense_names = [req.expense_name for req in requests]
        results = classification_service.batch_classify(expense_names)
        
        return {
            "success": True,
            "results": results,
            "count": len(results)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch classification failed: {str(e)}")

@router.post("/record-correction")
def record_correction(
    correction_data: dict,
    db: Session = Depends(get_db)
):
    """Record when user corrects AI classification"""
    try:
        classification_service = HybridClassificationService(db)
        classification_service.record_correction(
            correction_data["expense_text"],
            correction_data["original_prediction"],
            correction_data["corrected_category"]
        )
        
        return {
            "success": True,
            "message": "Correction recorded for model training"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to record correction: {str(e)}")

@router.get("/classifier-info")
def get_classifier_info(db: Session = Depends(get_db)):
    """Get information about the classification system"""
    try:
        classification_service = HybridClassificationService(db)
        info = classification_service.get_classifier_info()
        
        return {
            "success": True,
            "classifier_info": info
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get classifier info: {str(e)}")

@router.get("/categories")
def get_all_categories(db: Session = Depends(get_db)):
    """Get all available categories"""
    try:
        classification_service = HybridClassificationService(db)
        categories = classification_service.rule_classifier.get_suggested_categories()
        
        return {"categories": categories}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/category-keywords/{category}")
def get_category_keywords(category: str, db: Session = Depends(get_db)):
    """Get keywords for a specific category"""
    try:
        classification_service = HybridClassificationService(db)
        keywords = classification_service.rule_classifier.get_category_keywords(category)
        
        return {"category": category, "keywords": keywords}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))