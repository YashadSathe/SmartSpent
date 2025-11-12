from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
import logging
from typing import Dict, Any

from app.services.database import get_db
from app.services.model_trainer import ExpenseModelTrainer
from app.services.training_data import TrainingDataCollector
from app.services.classification_service import HybridClassificationService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/training", tags=["training"])

# Global instances
model_trainer = ExpenseModelTrainer()

@router.get("/stats")
def get_training_stats(db: Session = Depends(get_db)):
    """Get statistics about collected training data"""
    try:
        collector = TrainingDataCollector(db)
        stats = collector.get_training_stats()
        
        return {
            "success": True,
            "stats": stats,
            "message": f"Collected {stats.get('total_examples', 0)} training examples"
        }
    except Exception as e:
        logger.error(f"Failed to get training stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/start-training")
def start_training(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    epochs: int = 10
):
    """
    Start model training with collected data
    Runs in background to avoid blocking API
    """
    try:
        # Get training data
        collector = TrainingDataCollector(db)
        training_data = collector.get_training_data()
        
        if len(training_data) < 50:
            raise HTTPException(
                status_code=400, 
                detail=f"Not enough training data. Need at least 50 examples, got {len(training_data)}"
            )
        
        # Start training in background
        background_tasks.add_task(
            train_model_background,
            training_data,
            epochs
        )
        
        return {
            "success": True,
            "message": f"Started training with {len(training_data)} examples",
            "training_examples": len(training_data),
            "epochs": epochs,
            "status": "training_started"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to start training: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/model-info")
def get_model_info(db: Session = Depends(get_db)):
    """Get information about the current ML model"""
    try:
        classification_service = HybridClassificationService(db)
        classifier_info = classification_service.get_classifier_info()
        
        # Get training stats
        collector = TrainingDataCollector(db)
        training_stats = collector.get_training_stats()
        
        return {
            "success": True,
            "classifier_info": classifier_info,
            "training_stats": training_stats,
            "ml_available": classifier_info["ml_model"].get("available", False)
        }
    except Exception as e:
        logger.error(f"Failed to get model info: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/retrain-if-ready")
def retrain_if_ready(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    min_examples: int = 20,
    epochs: int = 8
):
    """
    Check if we have enough new data and retrain if ready
    """
    try:
        collector = TrainingDataCollector(db)
        training_data = collector.get_training_data()
        
        if len(training_data) >= min_examples:
            # Start training
            background_tasks.add_task(
                train_model_background,
                training_data,
                epochs
            )
            
            return {
                "success": True,
                "message": f"Started retraining with {len(training_data)} examples",
                "training_examples": len(training_data),
                "retraining": True
            }
        else:
            return {
                "success": True,
                "message": f"Not enough data for retraining. Have {len(training_data)}, need {min_examples}",
                "training_examples": len(training_data),
                "retraining": False
            }
            
    except Exception as e:
        logger.error(f"Failed to check retraining: {e}")
        raise HTTPException(status_code=500, detail=str(e))

def train_model_background(training_data: list, epochs: int):
    """
    Background task for model training
    This runs separately from the API request
    """
    try:
        logger.info(f"Starting background training with {len(training_data)} examples")
        
        # Train the model
        results = model_trainer.train_model(training_data, epochs)
        
        if results["success"]:
            logger.info(f"Background training completed successfully: {results['eval_accuracy']:.3f} accuracy")
        else:
            logger.error(f"Background training failed: {results.get('error', 'Unknown error')}")
            
    except Exception as e:
        logger.error(f"Background training error: {e}")