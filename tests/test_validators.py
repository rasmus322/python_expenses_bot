import pytest
import os
import sys
from validators import validate_expense_amount

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def test_valid_integer():
    is_valid, res = validate_expense_amount("100")
    assert is_valid is True
    assert res == 100.0

def test_valid_float_with_coma():
    is_valid, res = validate_expense_amount("100,50")
    assert is_valid is True
    assert res == 100.50

def test_invalid_string():
    is_valid, res = validate_expense_amount("str")
    assert is_valid is False
    assert "не число" in res

def test_invalid_negative():
    is_valid, res = validate_expense_amount("-100")
    assert is_valid is False
    assert "больше нуля" in res

def test_invalid_infinity():
    is_valid, res = validate_expense_amount("inf")
    assert is_valid is False
    assert "бесконечностью" in res

def test_invalid_too_large():
    is_valid, res = validate_expense_amount("10000000000")
    assert is_valid is False
    assert "слишком большая" in res