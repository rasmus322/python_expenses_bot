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

def get_total_by_category(user_id: int) -> dict:
    session = start_session()

    try:
        res = session.query(
            Expense.category, func.sum(Expense.amount)) \
                .filter(Expense.user_id == user_id) \
                .group_by(Expense.category).all()

        return { category: float(total) for category, total in res }
    finally:
        session.close()

def get_expenses_stats(user_id: int) -> tuple[dict, date, date] | None:
    session = start_session()

    try:
        count = session.query(Expense).filter(Expense.user_id == user_id).count()
        if count == 0:
            return None

        sum_res = session.query(Expense.category, func.sum(Expense.amount)) \
            .filter(Expense.user_id == user_id) \
            .group_by(Expense.category).all()

        stats = { category: float(total) for category, total in sum_res }

        date_res = session.query(func.min(Expense.date), func.max(Expense.date)) \
            .filter(Expense.user_id == user_id).first()

        return stats, date_res[0], date_res[1]
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