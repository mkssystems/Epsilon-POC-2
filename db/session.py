# db/session.py
from sqlalchemy.orm import sessionmaker
from config import DATABASE_URL
from sqlalchemy import create_engine

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
