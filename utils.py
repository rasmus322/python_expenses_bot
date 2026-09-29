from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

async def send_message(
        update: Update, 
        text: str, 
        reply_markup: InlineKeyboardMarkup = None, 
        parse_mode: str = "HTML") -> None:
    if update.callback_query:
        await update.callback_query.edit_message_text(text, parse_mode=parse_mode, reply_markup=reply_markup)
    elif update.message:
        await update.message.reply_text(text, parse_mode=parse_mode, reply_markup=reply_markup)

def build_keyboard(btns_data: list[tuple[str, str]], n_cols: int = 2) -> InlineKeyboardMarkup:
    keyboard = []

    for i in range(0, len(btns_data), n_cols):
        row = [
            InlineKeyboardButton(text=btn[0], callback_data=btn[1])
            for btn in btns_data[i:i + n_cols]
        ]
        keyboard.append(row)

    return InlineKeyboardMarkup(keyboard)

def get_main_menu_keyboard() -> InlineKeyboardMarkup:
    btns = [
        ("➕ Новый расход", "cmd_start"),
        ("📊 Статистика", "cmd_stats"),
        ("📈 График", "cmd_graph"),
        ("❌ Отмена", "cmd_cancel")
    ]

    return build_keyboard(btns)

def get_back_to_menu_keyboard() -> InlineKeyboardMarkup:
    return build_keyboard([("📋 В меню", "show_menu")], n_cols=1)

def get_categories_keyboard(categories: list[str]) -> InlineKeyboardMarkup:
    btns = [(category, category) for category in categories]

    return build_keyboard(btns)