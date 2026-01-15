from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

DATABASE_URL = "sqlite:///./neuroflow.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()


# -------------------------
# DB DEPENDENCY (FIX 🔥)
# -------------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()





