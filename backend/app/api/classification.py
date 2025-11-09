from fastapi import APIRouter
from app.schemas import schemas
from app.models.rule_engine import RuleBasedClassifier

router = APIRouter(prefix="/api/classification", tags=["classification"])
classifier = RuleBasedClassifier()

@router.post("/predict", response_model=schemas.ClassificationResponse)
def classify_expense(request: schemas.ClassificationRequest):
    category, confidence = classifier.classify(request.expense_name)
    suggested_categories = classifier.get_suggested_categories(request.expense_name)
    
    return schemas.ClassificationResponse(
        category=category,
        confidence=confidence,
        suggested_categories=suggested_categories
    )

@router.get("/categories")
def get_all_categories():
    categories = classifier.get_suggested_categories()
    return {"categories": categories}

@router.get("/category-keywords/{category}")
def get_category_keywords(category: str):
    keywords = classifier.get_category_keywords(category)
    return {"category": category, "keywords": keywords}