from functools import lru_cache
from app.models.ml_classifier import MLExpenseClassifier
import logging
from app.services.classification_service import HybridClassificationService
from app.services.database import SessionLocal

logger = logging.getLogger(__name__)

@lru_cache()
def get_ml_classifier() -> MLExpenseClassifier:
    """
    FastAPI dependency to get the shared ML classifier instance.
    lru_cache ensures this function runs only once.
    """
    logger.info("Creating shared MLExpenseClassifier instance...")
    return MLExpenseClassifier()

@lru_cache()
def get_hybrid_classifier_service() -> HybridClassificationService:
    """
    FastAPI dependency to get the shared HybridClassificationService.
    This creates the service *once* with a single DB session
    that is *only* used for the initial rule-based classifier.
    """
    logger.info("Creating shared HybridClassificationService instance...")
    # Create a temporary DB session just for the service initialization
    db = SessionLocal()
    try:
        # Inject the ML singleton into the Hybrid service
        service = HybridClassificationService(db, get_ml_classifier())
    finally:
        db.close()
    return service