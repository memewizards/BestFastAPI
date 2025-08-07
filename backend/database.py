
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = None
SessionLocal = None

if DATABASE_URL:
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
    
    if "sslmode" not in DATABASE_URL:
        DATABASE_URL += "?sslmode=require"

    try:
        engine = create_engine(
            DATABASE_URL,
            connect_args={
                "keepalives": 1,
                "keepalives_idle": 30,
                "keepalives_interval": 10,
                "keepalives_count": 5,
            },
            pool_pre_ping=True,  # Add this to check connections before use
        )
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    except Exception as e:
        print(f"❌ Failed to create database engine: {e}")
        engine = None
        SessionLocal = None
else:
    print("⚠️ DATABASE_URL not found, database features will be disabled.")

Base = declarative_base()

def get_db():
    if SessionLocal is None:
        raise Exception("Database is not configured. Please set DATABASE_URL.")
    
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()