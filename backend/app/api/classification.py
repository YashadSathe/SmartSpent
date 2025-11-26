from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from app.services.database import get_db
from app.services.classification_service import HybridClassificationService
from app.schemas import schemas
from app.services.training_data import TrainingDataCollector # Added this import

# --- THIS IS THE FIX ---
# We now import from the new 'dependencies.py' file, not 'main.py'
from app.dependencies import get_hybrid_classifier_service
# ---------------------

router = APIRouter(prefix="/api/classification", tags=["classification"])

@router.post("/predict", response_model=schemas.ClassificationResponse)
def classify_expense(
    request: schemas.ClassificationRequest, 
    # Use the new singleton service
    classifier: HybridClassificationService = Depends(get_hybrid_classifier_service)
):
    """Classify expense with hybrid ML + rule-based approach"""
    try:
        result = classifier.classify(request.expense_name)
        
        return schemas.ClassificationResponse(
            category=result["final_category"],
            confidence=result["final_confidence"],
            suggested_categories=result["suggested_categories"]
            # I've removed the 'metadata' key as it's not in your Pydantic schema
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Classification failed: {str(e)}")

@router.post("/batch-predict")
def batch_classify_expenses(
    requests: List[schemas.ClassificationRequest],
    classifier: HybridClassificationService = Depends(get_hybrid_classifier_service)
):
    """Classify multiple expenses at once"""
    try:
        expense_names = [req.expense_name for req in requests]
        results = classifier.batch_classify(expense_names)
        
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
    # We still need a *new* DB session here to write the correction
    db: Session = Depends(get_db),
    classifier: HybridClassificationService = Depends(get_hybrid_classifier_service)
):
    """Record when user corrects AI classification"""
    try:
        # Create a new service instance *with this request's DB session*
        # to safely write to the database.
        correction_service = HybridClassificationService(db, classifier.ml_classifier)
        
        correction_service.record_correction(
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
def get_classifier_info(
    db: Session = Depends(get_db), # We need the DB for the stats part
    classifier: HybridClassificationService = Depends(get_hybrid_classifier_service)
):
    """Get information about the classification system"""
    try:
        info = classifier.get_classifier_info()

        # Get training stats
        collector = TrainingDataCollector(db)
        training_stats = collector.get_training_stats()
        
        return {
            "success": True,
            "classifier_info": info,
            "training_stats": training_stats,
            "ml_available": info["ml_model"].get("available", False)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get classifier info: {str(e)}")

@router.get("/categories")
def get_all_categories(
    classifier: HybridClassificationService = Depends(get_hybrid_classifier_service)
):
    """Get all available categories"""
    try:
        categories = classifier.rule_classifier.get_suggested_categories()
        
        return {"categories": categories}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/category-keywords/{category}")
def get_category_keywords(
    category: str, 
    classifier: HybridClassificationService = Depends(get_hybrid_classifier_service)
):
    """Get keywords for a specific category"""
    try:
        keywords = classifier.rule_classifier.get_category_keywords(category)
        
        return {"category": category, "keywords": keywords}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))