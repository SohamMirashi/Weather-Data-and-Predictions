# database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from dotenv import load_dotenv

load_dotenv()  # reads .env if present

DATABASE_URL = "mysql+pymysql://root:SSM123@localhost:3306/weather_info"

# create engine (synchronous)
engine = create_engine(DATABASE_URL, echo=True, future=True)

# create a configured "Session" class
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

Base = declarative_base()
