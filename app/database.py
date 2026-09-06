from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base
from config import database_url
engine = create_engine(database_url)

SessionLocal = sessionmaker(bind=engine)

Base = declarative_base()