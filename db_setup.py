from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, Date, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import date, datetime
Base = declarative_base()
print("✅ Database ready")
engine = create_engine('sqlite:///racing_ai.db')
Base.metadata.create_all(engine)
