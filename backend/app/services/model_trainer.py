import logging
import os
import json
from typing import List, Dict, Any, Tuple
import torch
from transformers import (
    AutoTokenizer, 
    AutoModelForSequenceClassification,
    TrainingArguments,
    Trainer,
    EarlyStoppingCallback
)
from sklearn.metrics import accuracy_score, precision_recall_fscore_support
import numpy as np
from datasets import Dataset, DatasetDict
import evaluate

logger = logging.getLogger(__name__)


# Handles fine-tuning of DeBERTa model on expense classification data
class ExpenseModelTrainer:    
    def __init__(self):
        self.model_name = "microsoft/deberta-v3-small"
        self.tokenizer = None
        self.model = None
        self.category_mapping = {
            "Food": 0, "Drinks": 1, "Transport": 2, "Shopping": 3,
            "Entertainment": 4, "Bills": 5, "Healthcare": 6, "Education": 7,
            "Travel": 8, "Groceries": 9, "Personal Care": 10, "Other": 11
        }
        self.reverse_category_mapping = {v: k for k, v in self.category_mapping.items()}
    
    # Load tokenizer and model
    def load_model(self):
        try:
            logger.info(f"Loading model: {self.model_name}")
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModelForSequenceClassification.from_pretrained(
                self.model_name,
                num_labels=len(self.category_mapping),
                id2label=self.reverse_category_mapping,
                label2id=self.category_mapping
            )
            logger.info("Model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            raise
    
    def prepare_dataset(self, training_data: List[Dict[str, Any]]) -> DatasetDict:
        """Prepare training data for model training"""
        try:
            texts = [item["text"] for item in training_data]
            labels = [self.category_mapping[item["label"]] for item in training_data]
            
            # Tokenize the data
            encodings = self.tokenizer(
                texts, 
                truncation=True, 
                padding=True, 
                max_length=128,
                return_tensors="pt"
            )
            
            # Create dataset
            dataset = Dataset.from_dict({
                'input_ids': encodings['input_ids'],
                'attention_mask': encodings['attention_mask'],
                'labels': labels
            })
            
            # Split into train/validation (80/20)
            train_test_split = dataset.train_test_split(test_size=0.2, seed=42)
            
            logger.info(f"Dataset prepared: {len(train_test_split['train'])} train, {len(train_test_split['test'])} test")
            return train_test_split
            
        except Exception as e:
            logger.error(f"Failed to prepare dataset: {e}")
            raise
    
    def compute_metrics(self, eval_pred):
        """Compute metrics for evaluation"""
        predictions, labels = eval_pred
        predictions = np.argmax(predictions, axis=1)
        
        precision, recall, f1, _ = precision_recall_fscore_support(labels, predictions, average='weighted')
        accuracy = accuracy_score(labels, predictions)
        
        return {
            'accuracy': accuracy,
            'f1': f1,
            'precision': precision,
            'recall': recall
        }
    
    # Fine-tune the model on expense classification data
    def train_model(self, training_data: List[Dict[str, Any]], epochs: int = 10) -> Dict[str, Any]:  
        try:
            if len(training_data) < 50:
                return {
                    "success": False,
                    "error": f"Not enough training data. Need at least 50 examples, got {len(training_data)}"
                }
            
            self.load_model()
            dataset = self.prepare_dataset(training_data)
            
            # Training arguments
            training_args = TrainingArguments(
                output_dir="./models/expense_classifier",
                overwrite_output_dir=True,
                num_train_epochs=epochs,
                per_device_train_batch_size=8,
                per_device_eval_batch_size=8,
                warmup_steps=100,
                weight_decay=0.01,
                logging_dir="./logs",
                logging_steps=10,
                evaluation_strategy="epoch",
                save_strategy="epoch",
                load_best_model_at_end=True,
                metric_for_best_model="accuracy",
                greater_is_better=True,
                save_total_limit=2,
                report_to=None,  # Disable wandb/tensorboard
            )
            
            # Initialize trainer
            trainer = Trainer(
                model=self.model,
                args=training_args,
                train_dataset=dataset["train"],
                eval_dataset=dataset["test"],
                compute_metrics=self.compute_metrics,
                callbacks=[EarlyStoppingCallback(early_stopping_patience=3)]
            )
            
            # Start training
            logger.info("Starting model training...")
            train_result = trainer.train()
            
            # Save the model
            trainer.save_model()
            self.tokenizer.save_pretrained("./models/expense_classifier")
            
            # Get final metrics
            eval_results = trainer.evaluate()
            
            results = {
                "success": True,
                "training_examples": len(training_data),
                "train_accuracy": train_result.metrics.get("train_accuracy", 0),
                "eval_accuracy": eval_results.get("eval_accuracy", 0),
                "eval_f1": eval_results.get("eval_f1", 0),
                "eval_loss": eval_results.get("eval_loss", 0),
                "model_saved": True,
                "model_path": "./models/expense_classifier"
            }
            
            logger.info(f"Training completed: {results['eval_accuracy']:.3f} accuracy")
            return results
            
        except Exception as e:
            logger.error(f"Model training failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    # Determine if we have enough new data to retrain
    def should_retrain(self, training_data: List[Dict[str, Any]], min_new_examples: int = 20) -> bool:
        return len(training_data) >= min_new_examples