import logging
import torch
from transformers import AutoTokenizer, AutoModelforSequenceClassification
from typing import Tuple, Dict, Any
import os

logger = logging.getlogger(__name__)

class MLExpenseClassifier:
    def __init__(self, model_path = None):
        self.model_path = model_path or "./models/expense_classifier"
        self.tokenizer = None
        self.model = None
        self.category_mapping = {
            0: "Food", 1: "Drinks", 2: "Transport", 3: "Shopping", 4: "Entertainment", 5: "Bills", 6: "Healthcare", 7: "Education", 8: "Travel", 9: "Groceries", 10: "Personal Care", 11: "Other"
        }
        self._load_model()

    # load fine tuned model
    def load_model(self):
        try:
            if os.path.exists(self.model_path):
                logger.info(f"Loading fine-tuned model from {self.model_path}")
                self.tokenizer = AutoTokenizer.from_pretrained(self.model_path)
                self.model = AutoModelforSequenceClassification.from_pretrained(self.model_path)
                self.model.eval()  # Set to evaluation mode
                logger.info("Fine-tuned model loaded successfully")
            else:
                logger.warning("No fine-tuned model found. Using rule-based fallback.")
                self.model = None
                
        except Exception as e:
            logger.error(f"Failed to load ML model: {e}")
            self.model = None
    
    def is_available(self) -> bool:
        """Check if ML model is available"""
        return self.model is not None
    
    def classify(self, expense_name: str) -> Tuple[str, float]:
        """Classify expense using ML model"""
        if not self.is_available():
            raise RuntimeError("ML model not available")
        
        try:
            # Tokenize input
            inputs = self.tokenizer(
                expense_name,
                return_tensors="pt",
                truncation=True,
                padding=True,
                max_length=128
            )
            
            # Model prediction
            with torch.no_grad():
                outputs = self.model(**inputs)
                probabilities = torch.softmax(outputs.logits, dim=-1)
                predicted_class = torch.argmax(probabilities, dim=1).item()
                confidence = probabilities[0][predicted_class].item()
            
            category = self.category_mapping.get(predicted_class, "Other")
            
            logger.debug(f"ML classification: '{expense_name}' -> '{category}' ({confidence:.3f})")
            return category, round(confidence, 3)
            
        except Exception as e:
            logger.error(f"ML classification failed: {e}")
            raise
    
    def batch_classify(self, expense_names: List[str]) -> List[Tuple[str, float]]:
        """Classify multiple expenses at once (more efficient)"""
        if not self.is_available():
            raise RuntimeError("ML model not available")
        
        try:
            # Tokenize all inputs
            inputs = self.tokenizer(
                expense_names,
                return_tensors="pt",
                truncation=True,
                padding=True,
                max_length=128
            )
            
            # Batch prediction
            with torch.no_grad():
                outputs = self.model(**inputs)
                probabilities = torch.softmax(outputs.logits, dim=-1)
                predicted_classes = torch.argmax(probabilities, dim=1)
                confidences = probabilities[torch.arange(probabilities.size(0)), predicted_classes]
            
            results = []
            for class_idx, confidence in zip(predicted_classes, confidences):
                category = self.category_mapping.get(class_idx.item(), "Other")
                results.append((category, round(confidence.item(), 3)))
            
            return results
            
        except Exception as e:
            logger.error(f"Batch classification failed: {e}")
            raise
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the loaded model"""
        if not self.is_available():
            return {"available": False}
        
        return {
            "available": True,
            "model_path": self.model_path,
            "model_type": type(self.model).__name__,
            "num_categories": len(self.category_mapping),
            "categories": list(self.category_mapping.values())
        }