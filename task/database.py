from sqlalchemy import  create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import os

DATABASE_URL = os.getenv("DATABASE_URL","postgresql://postgres:admin@localhost:5432/taskdb")

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(bind=engine, autocommit = False, autoflush=False)

Base = declarative_base()

def get_db():
    db = SessionLocal()  # Assuming SessionLocal is defined for your DB session
    try:
        yield db
    finally:
        db.close()


