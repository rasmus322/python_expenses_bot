from sqlalchemy import create_engine
from models import Base
from config import DATABASE_URI

def create_database():
    engine = create_engine(DATABASE_URI)
    Base.metadata.create_all(engine)