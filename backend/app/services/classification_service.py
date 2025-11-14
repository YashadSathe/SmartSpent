import logging
from typing import Tuple, List, Dict, Any
from app.models.rule_engine import RuleBasedClassifier
from app.models.ml_classifier import MLExpenseClassifier
from app.services.training_data import TrainingDataCollector

logger = logging.getLogger(__name__)

class HybridClassificationService:
    """
    Hybrid classification service that combines:
    1. ML model (when available and confident)
    2. Rule-based fallback (when ML not available or low confidence)
    3. Learning from user corrections
    """
    
    def __init__(self, db_session):
        self.rule_classifier = RuleBasedClassifier()
        self.ml_classifier = MLExpenseClassifier()
        self.training_collector = TrainingDataCollector(db_session)
        self.ml_confidence_threshold = 0.7  # Use ML if confidence >= 70%
    
    def classify(self, expense_name: str, use_ml: bool = True) -> Dict[str, Any]:
        """
        Classify expense using hybrid approach
        Returns detailed classification results
        """
        try:
            # Step 1: Try ML classification if available and enabled
            ml_result = None
            if use_ml and self.ml_classifier.is_available():
                try:
                    ml_category, ml_confidence = self.ml_classifier.classify(expense_name)
                    ml_result = {
                        "category": ml_category,
                        "confidence": ml_confidence,
                        "method": "ml"
                    }
                    
                    # If ML confidence is high, use it directly
                    if ml_confidence >= self.ml_confidence_threshold:
                        logger.info(f"Using ML classification (confidence: {ml_confidence})")
                        return {
                            **ml_result,
                            "final_category": ml_category,
                            "final_confidence": ml_confidence,
                            "used_ml": True,
                            "ml_available": True
                        }
                        
                except Exception as e:
                    logger.warning(f"ML classification failed, falling back to rules: {e}")
                    ml_result = {"error": str(e), "method": "ml"}
            
            # Step 2: Use rule-based classification as fallback
            rule_category, rule_confidence = self.rule_classifier.classify(expense_name)
            rule_result = {
                "category": rule_category,
                "confidence": rule_confidence,
                "method": "rule_based"
            }
            
            # Determine final result
            final_category = rule_category
            final_confidence = rule_confidence
            used_ml = False
            
            # If ML result exists but wasn't confident enough, we can still consider it
            if ml_result and "category" in ml_result:
                # If ML and rules agree, boost confidence
                if ml_result["category"] == rule_category:
                    final_confidence = max(ml_result["confidence"], rule_confidence)
                    used_ml = True
                # If ML is somewhat confident (>50%), consider it
                elif ml_result["confidence"] > 0.5:
                    final_category = ml_result["category"]
                    final_confidence = ml_result["confidence"]
                    used_ml = True
            
            result = {
                "final_category": final_category,
                "final_confidence": final_confidence,
                "used_ml": used_ml,
                "ml_available": self.ml_classifier.is_available(),
                "ml_result": ml_result,
                "rule_result": rule_result,
                "suggested_categories": self.rule_classifier.get_suggested_categories(expense_name)
            }
            
            logger.debug(f"Hybrid classification: '{expense_name}' -> '{final_category}' (ML: {used_ml})")
            return result
            
        except Exception as e:
            logger.error(f"Hybrid classification failed: {e}")
            # Ultimate fallback
            fallback_category, fallback_confidence = self.rule_classifier.classify(expense_name)
            return {
                "final_category": fallback_category,
                "final_confidence": fallback_confidence,
                "used_ml": False,
                "ml_available": False,
                "ml_result": {"error": str(e)},
                "rule_result": {
                    "category": fallback_category,
                    "confidence": fallback_confidence,
                    "method": "rule_based"
                },
                "suggested_categories": self.rule_classifier.get_suggested_categories(expense_name),
                "error": "Classification service error"
            }
    
    def record_correction(self, expense_text: str, original_prediction: str, corrected_category: str):
        """
        Record when user corrects a classification
        This data will be used for model training
        """
        try:
            self.training_collector.record_correction(
                expense_text, 
                original_prediction, 
                corrected_category
            )
            logger.info(f"Recorded correction: '{expense_text}' {original_prediction}->{corrected_category}")
        except Exception as e:
            logger.error(f"Failed to record correction: {e}")
    
    def get_training_stats(self) -> Dict[str, Any]:
        """Get statistics about training data"""
        try:
            return self.training_collector.get_training_stats()
        except Exception as e:
            logger.error(f"Failed to get training stats: {e}")
            return {}
    
    def get_classifier_info(self) -> Dict[str, Any]:
        """Get information about both classifiers"""
        ml_info = self.ml_classifier.get_model_info() if hasattr(self.ml_classifier, 'get_model_info') else {}
        
        return {
            "rule_based": {
                "available": True,
                "categories": self.rule_classifier.get_suggested_categories()
            },
            "ml_model": ml_info,
            "hybrid_settings": {
                "ml_confidence_threshold": self.ml_confidence_threshold,
                "ml_available": self.ml_classifier.is_available() if hasattr(self.ml_classifier, 'is_available') else False
            }
        }
    
    def reload_model(self):
        """Forces the classifier to reload the model from disk."""
        logger.info(f"Reloading model from {self.model_path}...")
        self._load_model()

    def batch_classify(self, expense_names: List[str], use_ml: bool = True) -> List[Dict[str, Any]]:
        """Classify multiple expenses efficiently"""
        results = []
        for expense_name in expense_names:
            results.append(self.classify(expense_name, use_ml))
        return results