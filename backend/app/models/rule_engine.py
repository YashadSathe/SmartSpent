from typing import Tuple, List, Dict

class RuleBasedClassifier:
    def __init__(self):
        self.category_rules: Dict[str, List[str]] = {
            "Food": [
                "pizza", "burger", "restaurant", "cafe", "meal", "food", "dinner", "lunch", "breakfast", "eat", "pav bhaji", "dominos", "mcdonalds", "kfc", "subway", "food court", "dining"
            ],
            "Drinks": [
                 "coffee", "tea", "beer", "alcohol", "wine", "whisky", "vodka", "juice", "soda", "coke", "pepsi", "slushie", "smoothie", "bubble tea", "starbucks", "cafe", "bar", "pub", "brewery", "water", "drink", "beverage"
            ],
            "Transport": [
                "uber", "ola", "taxi", "bus", "train", "metro", "fuel", "petrol", "diesel", "auto", "rickshaw", "travel", "commute", "railway", "airport", "cab", "ride"
            ],
            "Shopping": [
                "amazon", "flipkart", "myntra", "shop", "purchase", "buy", "mall", "market", "shopping", "order", "online", "store"
            ],
            "Entertainment": [
                "netflix", "movie", "cinema", "game", "concert", "theater", "streaming", "spotify", "youtube", "prime", "music", "film"
            ],
            "Bills": [
                "electricity", "internet", "water", "bill", "subscription", "mobile", "phone", "broadband", "utility", "rent", "maintenance"
            ],
            "Healthcare": [
                "hospital", "medical", "medicine", "doctor", "pharmacy", "clinic", "checkup", "health", "dental", "insurance"
            ],
            "Education": [
                "book", "course", "college", "tuition", "stationery", "university", "study", "education", "school", "coaching"
            ],
            "Travel": [
                "flight", "hotel", "vacation", "trip", "holiday", "tour", "booking", "resort", "travel", "tourism"
            ],
            "Groceries": [
                "grocery", "vegetable", "fruit", "milk", "bread", "eggs", "bigbasket", "grofers", "supermarket", "kirana", "provisions"
            ],
            "Personal Care": [
                "salon", "haircut", "shampoo", "soap", "cosmetic", "beauty", "spa", "massage", "gym", "fitness", "skincare"
            ]
        }
    
    def classify(self, expense_name: str) -> tuple[str, float]:
        """Classify expense and return (category, confidence)"""
        if not expense_name or not expense_name.strip():
            return "Others", 0.1        
        expense_lower = expense_name.lower().strip()
    
        # Check category for keyword matches
        matches = []
    
        for category, keywords in self.category_rules.items():
            for keyword in keywords:
                if keyword in expense_lower:
                    # Calculate match score based on keyword length and position
                    match_score = len(keyword) * 10
                    matches.append((category, match_score))
    
        if matches:
            # Find the match with highest score
            best_match = max(matches, key = lambda x: x[1])
            category = best_match[0]
    
            # Calculate confidence
            confidence = min(0.95, 0.7 + (best_match[1] * 0.001))
            return category, round(confidence, 2)
        
        # If no match found, return Others category with low confidence
        return "Others", 0.3
    
    def get_suggested_categories(self, expense_name: str = "") -> List[str]:
        """Get all available categories for manual selection"""
        return list(self.category_rules.keys()) + ["Others"]
        
    def get_category_keywords(self, category: str) -> List[str]:
        """Get keywords for a specific category"""
        return self.category_rules.get(category, [])