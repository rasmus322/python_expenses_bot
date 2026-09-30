from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
from models import Base, Expense
from config import DATABASE_URI
from datetime import date

engine = create_engine(DATABASE_URI)
start_session = sessionmaker(bind=engine)

def create_database():
    Base.metadata.create_all(engine)

def add_expense(user_id: int, amount: float, category: str) -> None:
    session = start_session()

    try:
        new_expense = Expense(
            user_id = user_id,
            amount = amount,
            category = category,
            date = date.today()
        )

        session.add(new_expense)
        session.commit()
    finally:
        session.close()

def get_expenses(user_id: int) -> list[Expense]:
    session = start_session()

    try:
        return session.query(Expense).filter(Expense.user_id == user_id).all()
    finally:
        session.close()

def get_total_by_category(user_id: int) -> dict:
    session = start_session()

    try:
        expenses = session.query(Expense).filter(Expense.user_id == user_id).all()
        stats = {}
        for expense in expenses:
            stats[expense.category] = stats.get(expense.category, 0) + expense.amount
        return stats
    finally:
        session.close()

def get_expenses_stats(user_id: int) -> tuple[dict, date, date] | None:
    session = start_session()

    try:
        expenses = session.query(Expense).filter(Expense.user_id == user_id).all()

        if not expenses:
            return None

        stats = {}

        for expense in expenses:
            stats[expense.category] = stats.get(expense.category, 0) + expense.amount

        all_dates = [expense.date for expense in expenses if expense.date is not None]
        min_date = min(all_dates)
        max_date = max(all_dates)

        return stats, min_date, max_date
    finally:
        session.close()

def clear_user_expenses(user_id: int) -> int:
    session = start_session()

    try:
        deleted_expenses = session.query(Expense).filter(Expense.user_id == user_id).delete()
        session.commit()
        return deleted_expenses
    finally:
        session.close()