import math

def validate_expense_amount(text: str) -> tuple[bool, float | str]:
    clean_text = text.replace(',', '.').strip()

    try:
        amount = float(clean_text)
    except ValueError:
        return False, "Это не число, введите число!"

    if math.isnan(amount):
        return False, "Некорректное числовое значение!"

    if math.isinf(amount):
        return False, "Сумма не может быть бесконечностью!"

    if amount <= 0:
        return False, "Сумма должна быть больше нуля!"

    if amount >= 10_000_000:
        return False, "Сумма слишком большая! Лимит: 10 000 000"

    return True, amount