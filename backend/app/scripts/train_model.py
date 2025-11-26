import sys
import os
import logging
import json
from datetime import datetime
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.services.model_trainer import ExpenseModelTrainer

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

def load_training_data():
    """Load data from the static JSON file"""
    file_path = "training_data/training_data.json"
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            print(f"✅ Loaded {len(data)} examples from {file_path}")
            return data
    except FileNotFoundError:
        print(f"❌ Error: {file_path} not found. Please create it first.")
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
    training_data = load_training_data()
    
    if not training_data:
        logger.error("No training data available. Exiting.")
        return
    
    logger.info(f"Loaded {len(training_data)} training examples")
    
    # Train the model
    trainer = ExpenseModelTrainer()
    results = trainer.train_model(training_data, epochs=10)
    
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