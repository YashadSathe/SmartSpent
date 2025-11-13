#!/usr/bin/env python3
"""
Standalone training script for fine-tuning the expense classification model
Can be run independently of the main application
"""

import sys
import os
import logging
import json
from datetime import datetime

# Add backend to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.model_trainer import ExpenseModelTrainer
from app.services.data_generator import TrainingDataGenerator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("training.log"),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

def load_training_data(data_source: str = "synthetic") -> list:
    """Load training data from specified source"""
    if data_source == "synthetic":
        # Generate synthetic data
        generator = TrainingDataGenerator()
        data = generator.generate_complete_dataset(examples_per_category=80, use_llm="ollama")
        generator.save_generated_data(data, "synthetic_dataset.json")
        return data
    elif data_source == "file":
        # Load from existing file
        try:
            with open("training_data/synthetic_training_data.json", "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            logger.error("Training data file not found. Generate data first.")
            return []
    else:
        logger.error(f"Unknown data source: {data_source}")
        return []

def main():
    """Main training function"""
    logger.info("Starting model training process...")
    
    # Configuration
    config = {
        "data_source": "synthetic",  # "synthetic" or "file"
        "epochs": 15,
        "examples_per_category": 80,
        "save_model": True
    }
    
    # Step 1: Load or generate training data
    logger.info("Loading training data...")
    training_data = load_training_data(config["data_source"])
    
    if not training_data:
        logger.error("No training data available. Exiting.")
        return
    
    logger.info(f"Loaded {len(training_data)} training examples")
    
    # Step 2: Initialize trainer
    trainer = ExpenseModelTrainer()
    
    # Step 3: Train the model
    logger.info(f"Starting training with {len(training_data)} examples for {config['epochs']} epochs...")
    
    results = trainer.train_model(training_data, epochs=config["epochs"])
    
    # Step 4: Report results
    if results["success"]:
        logger.info("🎉 Training completed successfully!")
        logger.info(f"📊 Final accuracy: {results['eval_accuracy']:.3f}")
        logger.info(f"📊 Final F1 score: {results['eval_f1']:.3f}")
        logger.info(f"💾 Model saved to: {results['model_path']}")
        
        # Save training report
        report = {
            "training_date": datetime.now().isoformat(),
            "config": config,
            "results": results,
            "training_examples": len(training_data),
            "categories_covered": list(set([item["label"] for item in training_data]))
        }
        
        with open("training_data/training_report.json", "w") as f:
            json.dump(report, f, indent=2)
            
        logger.info("📄 Training report saved to training_data/training_report.json")
        
    else:
        logger.error(f"❌ Training failed: {results.get('error', 'Unknown error')}")

if __name__ == "__main__":
    main()