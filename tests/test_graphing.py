import pytest
import os
import sys
import io
from datetime import date
from graphing import create_bar_chart, create_pie_chart

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def test_create_pie_chart():
    stats = { "Кафе": 500, "Продукты": 1500 }
    min_date = date.today()
    max_date = date.today()

    res = create_pie_chart(stats, min_date, max_date)

    assert isinstance(res, io.BytesIO)
    assert res.getbuffer().nbytes > 0

def test_create_bar_chart():
    stats = { "Транспорт": 300 }
    min_date = date.today()
    max_date = date.today()

    res = create_bar_chart(stats, min_date, max_date)

    assert isinstance(res, io.BytesIO)
    assert res.getbuffer().nbytes > 0

def test_empty_stats():
    res = create_pie_chart({}, date.today(), date.today())

    assert res is None