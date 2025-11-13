import logging
from typing import List, Dict, Any
from datetime import datetime
import json
import os
from sqlalchemy.orm import Session
from app.schemas.models import LearningCorrection

logger = logging.getLogger(__name__)

# collect training data from user for ML training
class TrainingDataCollector:
    def __init__(self, db: Session):
        self.db = db
        self.training_file = "training_data/expense_classification.jsonl"
        os.makedirs("training_data", exist_ok=True)

    def record_correction(self, expense_text: str, original_prediction: str, corrected_category: str):
        try:
            # save in db for persistence
            correction = LearningCorrection(
                expense_text = expense_text,
                original_prediction = original_prediction,
                corrected_category = corrected_category
            )
            self.db.add(correction)
            self.db.commit()

            # save to json for easy training
            training_example = {
                "text": expense_text,
                "label": corrected_category,
                "original_prediction": original_prediction,
                "timestamp": datetime.now().isoformat() + "Z"
            }

            with open(self.training_file, "a", encoding = "uft-8") as f:
                f.write(json.dumps(training_example) + "\n")

            logger.info(f"Recorded training example: '{expense_text}' -> '{corrected_category}'")

        except Exception as e:
            logger.error(f"Failed to record training data: {e}")
            self.db.rollback()

    def get_training_data(self, limit: int = None):
        try:
            corrections = self.db.query(LearningCorrection).all()
            if limit:
                corrections = corrections[:limit]

            training_data = []
            for correction in corrections:
                training_data.append({
                    "text": corrections.expense_text,
                    "label": corrections.corrected_category,
                    "original_prediction": corrections.original_predictions,
                    "timestamp": correction.learned_at.isoformat() + "Z"
                })

            return training_data
        
        except Exception as e:
            logging.error(f"Failed to retrieve training data: {e}")
            return []
    
    # get statistics about training data(collected)
    def get_training_status(self) -> Dict[str: Any]:
        try:
            total_examples = self.db.query(LearningCorrection).count()

            # count examples per category
            category_counts = {}
            corrections = self.bd.query(LearningCorrection).all()
            for correction in corrections:
                category = correction.corrected_category
                category_counts[category] = category_counts.get(category, 0) + 1

            return {
                "Total_examples": total_examples,
                "Category_distribution": category_counts,
                "training_file_exists": os.path.exists(self.training_file)
            }
        
        except Exception as e:
            logger.error(f"Failed to get training stats: {e}")
            return {}