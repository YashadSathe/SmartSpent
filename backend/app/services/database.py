from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.schemas.models import Base, CategoryBudget,    DEFAULT_CATEGORIES

# SQLite Database URl
SQLALCHEMY_DATABASE_URL = "sqlite:///./expense_tracker.db"

# Create Engine
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_agrs = {"check_same-thread": False}
)

# Local Sessiom
SessionLocal = sessionmaker(autocommit = False, autoflush = True, bind = engine)

# dependency to get DB session
def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()

# cleate table and initialize data
def create_tables():
    Base.metadata.create.all(bind = engine)

    # Initialize default category budget
    db = SessionLocal()

    try:
        # Create default budget with 0 budget
        for category in DEFAULT_CATEGORIES:
            existing = db.query(CategoryBudget).filter(CategoryBudget.category == category).first()

            if not existing:
                db_catergory = CategoryBudget(category = category, monthly_budget = 0)
                db.add(db_catergory)

        db.commit
        print("Database tables created and initialized with default categories")

    except Exception as e:
        db.rollback()
        print(f"Error initializing database: {e}")
    
    finally:
        db.close()

