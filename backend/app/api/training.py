from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
import logging
from typing import Dict, Any
from app.services.database import get_db
from app.services.model_trainer import ExpenseModelTrainer
from app.services.training_data import TrainingDataCollector
from app.services.classification_service import HybridClassificationService
from app.services.data_generator import TrainingDataGenerator

# Import the new dependency
from app.dependencies import get_hybrid_classifier_service

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
    epochs: int = 10,
    # Get the singleton service
    classifier: HybridClassificationService = Depends(get_hybrid_classifier_service)
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
            epochs,
            classifier  # <-- Pass the singleton service
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
def get_model_info(
    db: Session = Depends(get_db),
    classifier: HybridClassificationService = Depends(get_hybrid_classifier_service)
):
    """Get information about the current ML model"""
    try:
        classifier_info = classifier.get_classifier_info()
        
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
    epochs: int = 8,
    classifier: HybridClassificationService = Depends(get_hybrid_classifier_service)
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
                epochs,
                classifier # <-- Pass the singleton service
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

# Update the function signature
def train_model_background(training_data: list, epochs: int, classifier_service: HybridClassificationService):
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
            
            # --- THIS IS THE FIX ---
            logger.info("Reloading ML model in main application...")
            classifier_service.reload_model()
            # -----------------------

        else:
            logger.error(f"Background training failed: {results.get('error', 'Unknown error')}")
            
    except Exception as e:
        logger.error(f"Background training error: {e}")

@router.post("/generate-data")
def generate_training_data(
    background_tasks: BackgroundTasks,
    examples_per_category: int = 50,
    use_llm: str = "ollama"
):
    """Generate synthetic training data"""
    try:
        generator = TrainingDataGenerator()
        
        # Generate in background
        background_tasks.add_task(
            generate_data_background,
            examples_per_category,
            use_llm
        )
        
        return {
            "success": True,
            "message": f"Started generating {examples_per_category} examples per category using {use_llm}",
            "total_categories": len(generator.categories),
            "expected_examples": examples_per_category * len(generator.categories)
        }
        
    except Exception as e:
        logger.error(f"Data generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/train-with-generated-data")
def train_with_generated_data(
    background_tasks: BackgroundTasks,
    examples_per_category: int = 50,
    epochs: int = 10,
    use_llm: str = "ollama",
    classifier: HybridClassificationService = Depends(get_hybrid_classifier_service)
):
    """Generate data and train model in one go"""
    try:
        background_tasks.add_task(
            generate_and_train_background,
            examples_per_category,
            epochs,
            use_llm,
            classifier # <-- Pass the singleton service
        )
        
        return {
            "success": True,
            "message": f"Started training with {examples_per_category} examples per category for {epochs} epochs",
            "total_expected_examples": examples_per_category * 12,  # 12 categories
            "training_epochs": epochs
        }
        
    except Exception as e:
        logger.error(f"Training with generated data failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

def generate_data_background(examples_per_category: int, use_llm: str):
    """Background task for data generation"""
    try:
        generator = TrainingDataGenerator()
        data = generator.generate_complete_dataset(examples_per_category, use_llm)
        generator.save_generated_data(data, "auto_generated_dataset.json")
        logger.info(f"Background data generation completed: {len(data)} examples")
    except Exception as e:
        logger.error(f"Background data generation failed: {e}")

# Update the function signature
def generate_and_train_background(examples_per_category: int, epochs: int, use_llm: str, classifier_service: HybridClassificationService):
    """Background task for generate + train pipeline"""
    try:
        # Generate data
        generator = TrainingDataGenerator()
        data = generator.generate_complete_dataset(examples_per_category, use_llm)
        
        # Train model
        trainer = ExpenseModelTrainer()
        results = trainer.train_model(data, epochs)
        
        if results["success"]:
            logger.info(f"Generate+train pipeline successful: {results['eval_accuracy']:.3f} accuracy")
            
            # --- THIS IS THE FIX ---
            logger.info("Reloading ML model in main application...")
            classifier_service.reload_model()
            # -----------------------
            
        else:
            logger.error(f"Generate+train pipeline failed: {results.get('error')}")
            
    except Exception as e:
        logger.error(f"Generate+train pipeline failed: {e}")