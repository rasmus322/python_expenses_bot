from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.error import BadRequest

async def send_message(
        update: Update, 
        text: str, 
        reply_markup: InlineKeyboardMarkup = None, 
        parse_mode: str = "HTML") -> None:
    if update.callback_query:
        try:
            await update.effective_message.edit_text(
                text, 
                parse_mode=parse_mode, 
                reply_markup=reply_markup
            )
        except BadRequest:
            await update.effective_message.reply_text(
                text,
                parse_mode=parse_mode,
                reply_markup=reply_markup
            )
            
    elif update.message:
        await update.effective_message.reply_text(
            text, 
            parse_mode=parse_mode, 
            reply_markup=reply_markup
        )

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

def get_graph_type_keyboard() -> InlineKeyboardMarkup:
    btns = [
        ("📀 Диск", "graph_pie"),
        ("📊 Столбцы", "graph_bar")
    ]

    return build_keyboard(btns)

def get_graph_action_keyboard() -> InlineKeyboardMarkup:
    btns = [
        ("🔄 Другой график", "graph_choose"),
        ("📋 В меню", "show_menu")
    ]

    return build_keyboard(btns)