import logging
import json
import os
from typing import List, Dict, Any
import requests
import time

logger = logging.getLogger(__name__)

class TrainingDataGenerator:
    """
    Generate synthetic training data using various LLM APIs
    Creates diverse expense examples for all categories
    """
    
    def __init__(self):
        self.categories = [
            "Food", "Drinks", "Transport", "Shopping", 
            "Entertainment", "Bills", "Healthcare", "Education",
            "Travel", "Groceries", "Personal Care", "Other"
        ]
        
        # LLM configuration
        self.llm_configs = {
            "openai": {
                "url": "https://api.openai.com/v1/chat/completions",
                "headers": {
                    "Authorization": f"Bearer {os.getenv('OPENAI_API_KEY', '')}",
                    "Content-Type": "application/json"
                }
            },
            "ollama": {
                "url": "http://localhost:11434/api/generate",
                "headers": {
                    "Content-Type": "application/json"
                }
            }
        }
    
    def generate_with_openai(self, category: str, examples_per_category: int = 50) -> List[Dict[str, str]]:
        """Generate training data using OpenAI API"""
        try:
            prompt = self._build_generation_prompt(category, examples_per_category)
            
            payload = {
                "model": "gpt-3.5-turbo",
                "messages": [
                    {
                        "role": "system",
                        "content": "You are an expert at generating realistic expense descriptions for training machine learning models."
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                "temperature": 0.8,
                "max_tokens": 2000
            }
            
            response = requests.post(
                self.llm_configs["openai"]["url"],
                headers=self.llm_configs["openai"]["headers"],
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                content = response.json()["choices"][0]["message"]["content"]
                return self._parse_generated_data(content, category)
            else:
                logger.error(f"OpenAI API error: {response.status_code} - {response.text}")
                return []
                
        except Exception as e:
            logger.error(f"OpenAI generation failed: {e}")
            return []
    
    def generate_with_ollama(self, category: str, examples_per_category: int = 50) -> List[Dict[str, str]]:
        """Generate training data using local Ollama"""
        try:
            prompt = self._build_generation_prompt(category, examples_per_category)
            
            payload = {
                "model": "llama2",  # or "mistral", "codellama" based on what you have
                "prompt": prompt,
                "stream": False
            }
            
            response = requests.post(
                self.llm_configs["ollama"]["url"],
                headers=self.llm_configs["ollama"]["headers"],
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                content = response.json()["response"]
                return self._parse_generated_data(content, category)
            else:
                logger.error(f"Ollama API error: {response.status_code} - {response.text}")
                return []
                
        except Exception as e:
            logger.error(f"Ollama generation failed: {e}")
            return []
    
    def _build_generation_prompt(self, category: str, count: int) -> str:
        """Build prompt for generating training data"""
        return f"""
Generate {count} diverse and realistic expense descriptions for the category "{category}".
The descriptions should be short (2-5 words) and represent common real-world expenses.

For category: {category}

Examples for different categories:
- Food: "pizza hut", "mcdonalds burger", "restaurant dinner", "street food"
- Transport: "uber ride", "bus ticket", "train fare", "petrol"
- Shopping: "amazon purchase", "clothing store", "electronics", "online shopping"

Now generate {count} specific examples for {category}. Return ONLY a JSON array of strings:

["example1", "example2", "example3", ...]

Make the examples diverse, realistic, and cover different contexts within {category}.
"""
    
    def _parse_generated_data(self, content: str, category: str) -> List[Dict[str, str]]:
        """Parse LLM response into training data format"""
        try:
            # Extract JSON array from response
            start_idx = content.find('[')
            end_idx = content.rfind(']') + 1
            
            if start_idx == -1 or end_idx == 0:
                logger.error(f"Could not parse JSON from response: {content}")
                return []
            
            json_str = content[start_idx:end_idx]
            examples = json.loads(json_str)
            
            # Convert to training data format
            training_data = []
            for example in examples:
                if isinstance(example, str) and example.strip():
                    training_data.append({
                        "text": example.strip(),
                        "label": category,
                        "source": "synthetic",
                        "timestamp": time.time()
                    })
            
            logger.info(f"Generated {len(training_data)} examples for {category}")
            return training_data
            
        except Exception as e:
            logger.error(f"Failed to parse generated data: {e}")
            return []
    
    def generate_complete_dataset(self, examples_per_category: int = 50, use_llm: str = "ollama") -> List[Dict[str, str]]:
        """Generate complete training dataset for all categories"""
        all_data = []
        
        for category in self.categories:
            logger.info(f"Generating data for {category}...")
            
            if use_llm == "openai":
                category_data = self.generate_with_openai(category, examples_per_category)
            else:
                category_data = self.generate_with_ollama(category, examples_per_category)
            
            all_data.extend(category_data)
            
            # Be nice to the API
            time.sleep(1)
        
        logger.info(f"Generated total {len(all_data)} examples across {len(self.categories)} categories")
        return all_data
    
    def save_generated_data(self, data: List[Dict[str, str]], filename: str = "synthetic_training_data.json"):
        """Save generated data to file"""
        try:
            filepath = f"training_data/{filename}"
            os.makedirs("training_data", exist_ok=True)
            
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Saved {len(data)} examples to {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Failed to save generated data: {e}")
            return None