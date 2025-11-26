from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
import datetime
from fastapi.middleware.cors import CORSMiddleware
from app.services.database import get_db, create_tables, SessionLocal
from app.schemas import schemas, models
from app.models.rule_engine import RuleBasedClassifier
from app.api import expenses, classification, budget, dashboard, training
from app.dependencies import get_hybrid_classifier_service


app = FastAPI(
    title="Expense Tracker API", 
    description = "AI-powered expense tracking and categorization system",
    version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # React frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(expenses.router)
app.include_router(classification.router)
app.include_router(budget.router)
app.include_router(dashboard.router)
app.include_router(training.router)

# Initialize classifier
classifier = RuleBasedClassifier()

# Create tables on startup
@app.on_event("startup")
def on_startup():
    create_tables()

    get_hybrid_classifier_service()

# Health check
@app.get("/")
def read_root():
    return {"message": "Expense Tracker API is running!"}
