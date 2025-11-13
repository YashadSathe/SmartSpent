import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.services.model_trainer import ExpenseModelTrainer
from app.services.data_generator import TrainingDataGenerator
import json

def quick_train(examples_per_category: int = 50, epochs: int = 10):
    """Quick training with generated data"""
    print("🚀 Starting quick training...")
    
    # Generate data
    print("📊 Generating training data...")
    generator = TrainingDataGenerator()
    data = generator.generate_complete_dataset(
        examples_per_category=examples_per_category, 
        use_llm="ollama"  # Change to "openai" if you have API key
    )
    
    print(f"✅ Generated {len(data)} examples")
    
    # Train model
    print("🧠 Training model...")
    trainer = ExpenseModelTrainer()
    results = trainer.train_model(data, epochs=epochs)
    
    if results["success"]:
        print(f"🎉 Training successful! Accuracy: {results['eval_accuracy']:.3f}")
    else:
        print(f"❌ Training failed: {results.get('error')}")
    
    return results

if __name__ == "__main__":
    # Run with default parameters
    quick_train(examples_per_category=50, epochs=10)