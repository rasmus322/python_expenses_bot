import pytest
import os
import sys
from datetime import date
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, Expense

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

TEST_DATABASE_URI = "sqlite:///:memory:"
test_engine = create_engine(TEST_DATABASE_URI)
TestingSessionLocal = sessionmaker(bind=test_engine)

@pytest.fixture
def db_session():
    Base.metadata.create_all(bind=test_engine)
    session = TestingSessionLocal()
    
    yield session

    session.close()
    Base.metadata.drop_all(bind=test_engine)

def test_add_and_get_expense(db_session):
    user_id = 12345
    amount = 100
    category = "Продукты"

    new_expense = Expense(user_id=user_id, amount=amount, category=category, date=date.today())
    db_session.add(new_expense)
    db_session.commit()

    expenses = db_session.query(Expense).filter(Expense.user_id == user_id).all()

    assert len(expenses) == 1
    assert expenses[0].category == "Продукты"
    assert expenses[0].amount == 100.0

def test_clear_user_expenses(db_session):
    user_id_first = 11111
    user_id_second = 22222

    db_session.add(Expense(user_id=user_id_first, amount="100", category="Продукты", date=date.today()))
    db_session.add(Expense(user_id=user_id_second, amount="200", category="Транспорт", date=date.today()))
    db_session.commit()

    deleted_count = db_session.query(Expense).filter(Expense.user_id == user_id_first).delete()
    db_session.commit()

    assert deleted_count == 1

    remaining = db_session.query(Expense).filter(Expense.user_id == user_id_second).all()

    assert len(remaining) == 1
    assert remaining[0].amount == 200.0
    assert remaining[0].category == "Транспорт"