from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
import datetime

Base = declarative_base

class Expense(Base):
    __tablename__ = "Expenses"

    id = Column(Integer, primary_key = True, index = True)
    expense_name = Column(String(220), nullable = False)
    amount = Column(Float, nullable = False)
    catagory = Column(String(100), nullable = False)
    predicted_category = Column(String(100), nullable = True)
    confidence = Column(Float, nullable = True)
    user_corrected = Column(Boolean, default = False)
    created_at = Column(DateTime(timezone = True), server_default = func.now())
    updated_at = Column(DateTime(timezone = True), onupdate = func.now())

class CategoryBudget(Base):
    __tablename__ = "Category_Budgets"

    id = Column(Integer, primary_key = True, index = True)
    category = Column(String, unique = True, nullable = False) 
    monthly_budget = Column(Float, nullable = False, default = 0.0)
    created_at = Column(DateTime(timezone = True),  server_default = func.now())

class OverallBudget(Base):
    __tablename__ = "Overall_Budgets"

    id =Column(Integer, primary_key = True, default = 1)
    monthly_budget = Column(Float, default = 0.0)
    monthly_income = Column(Float, default = 0.0)
    created_at = Column(DateTime(timezone = True), server_default = func.now())
    updated_at = Column(DateTime(timezone = True), onupdate = func.now())

class LearningCorrection(Base):
    __tablename__ = "learning_Correction"

    id = Column(Integer, primary_key = True, index = True)
    expense_text = Column(Text, nullable = False)
    original_prediction = Column(String(100))
    corrected_category = Column(String(100))
    learned_at = Column(DateTime(timezone = True),server_default = func.now())

# Pre-populate catrgories
DEFAULT_CATEGORIES = [
    "Food", "Drinks", "Transport", "Shopping", "Entertainment", "Bills", "Healthcare", "Education", "Travel", "Groceries", "Personal Care", "Others" 
]