from sqlalchemy import create_engine
from models import Base

def create_database():
    engine = create_engine('sqlite:///expenses_database.db')
    Base.metadata.create_all(engine)