import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, MessageHandler, CommandHandler, CallbackQueryHandler, 
    ConversationHandler, filters, ContextTypes
)
import traceback
from config import BOT_TOKEN
from constants import CATEGORIES
from database import (
    create_database, 
    add_expense, 
    get_total_by_category, 
    get_expenses_stats,
    clear_user_expenses
)
from utils import (
    send_message,
    get_main_menu_keyboard,
    get_back_to_menu_keyboard,
    get_categories_keyboard,
    get_graph_type_keyboard,
    get_graph_action_keyboard,
    get_clear_confirmation_keyboard
)
from graphing import create_bar_chart, create_pie_chart
from validators import validate_expense_amount

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

AMOUNT, CATEGORY_PAGE, CATEGORY_TEXT = range(3)

async def global_error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logging.error("Exception while handling an update:", exc_info=context.error)

    if update and isinstance(update, Update) and update.effective_message:
        await update.effective_message.reply_text(
            "Произошла непредвиденная ошибка на сервере."
            "Попробуйте повторить позже."
        )

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await send_message(update, "Привет! Это бот для подсчета расходов. Введите сумму расхода:")
    return AMOUNT

async def restart_expense(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await send_message(
        update,
        "➕ Введите сумму нового расхода:",
        reply_markup=get_back_to_menu_keyboard()
    )
    return AMOUNT

async def get_amount(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    is_valid, res = validate_expense_amount(update.message.text)

    if not is_valid:
        await send_message(
            update,
            f"{ res } \n\n Попробуйте еще раз, или используйте /cancel для отмены."
        )
        return AMOUNT

    context.user_data["amount"] = res

    await send_message(
        update,
        f"Сумма: {res:.2f}. Выберите категорию:",
        reply_markup=get_categories_keyboard(0, CATEGORIES)
    )

    return CATEGORY_PAGE

async def save_expense_and_show_menu(
        update: Update, 
        context: ContextTypes.DEFAULT_TYPE, 
        category: str) -> int:
    amount = context.user_data.get('amount')
    user_id = update.effective_user.id

    add_expense(user_id, amount, category)
    context.user_data.clear()

    text = f"✅ Расход записан! \n Сумма: { amount } \n Категория: { category }"
    await send_message(update, text, reply_markup=get_main_menu_keyboard())

    return ConversationHandler.END

async def request_clear_history(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await send_message(
        update,
        "Это действие удалит записи всех ваших расходов<b>!!!</b> \n"
        "Статистика и графики будут обнулены. \n \n"
        "Вы уверены?",
        reply_markup=get_clear_confirmation_keyboard(),
        parse_mode="HTML"
    )

######

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    stats_dict = get_total_by_category(update.effective_user.id)

    if not stats_dict:
        text = (
            "У вас нет записанных расходов! \n "
            "Ипользуйте кнопку '➕ Новый расход' чтобы записать расход."
        )
        await send_message(
            update,
            text,
            reply_markup=get_main_menu_keyboard()
        )
        return

    text = "📊 <b>Ваша статистика трат:</b>\n\n"
    total_amount = 0.0

    sorted_stats = sorted(stats_dict.items(), key=lambda item: item[1], reverse=True)

    for category, amount in sorted_stats:
        text += f"<b>*</b> { category }: <b>{amount:.2f}</b>\n"
        total_amount += amount

    text += f"\n <b>Итого потрачено:</b> {total_amount:.2f}"

    await send_message(update, text, reply_markup=get_back_to_menu_keyboard())

async def graph(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    result = get_expenses_stats(update.effective_user.id)

    if result is None:
        await send_message(
            update,
            "У вас пока нет записанных расходов. \n Создайте новый расход",
            reply_markup=get_main_menu_keyboard()
        )
        return

    context.user_data['chart_stats'] = result

    await send_message(
        update,
        "📊 Выберите тип графика:",
        reply_markup=get_graph_type_keyboard()
    )

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data.clear()

    await send_message(
        update,
        "Действие отменено",
        reply_markup=get_main_menu_keyboard()
    )
    
    return ConversationHandler.END

######

async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await send_message(
        update,
        "<b>Главное меню</b> \n \n Выберите действие:",
        reply_markup=get_main_menu_keyboard()
    )

async def handle_graph_select(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    stats_data = context.user_data.get('chart_stats')

    if not stats_data:
        await send_message(
            update,
            "Данные не актуальны. Запросите график заново",
            reply_markup=get_main_menu_keyboard()
        )
        return
    
    stats_dict, min_date, max_date = stats_data
    query = update.callback_query

    await query.answer()

    if query.data == "graph_pie":
        chart_buf = create_pie_chart(stats_dict, min_date, max_date)
        caption = "📀 Распределение расходов по категориям"
    elif query.data == "graph_bar":
        chart_buf = create_bar_chart(stats_dict, min_date, max_date)
        caption = "📊 Сравнение сумм по категориям"
    else:
        return

    await update.effective_message.reply_photo(
        photo=chart_buf,
        caption=caption,
        reply_markup=get_graph_action_keyboard()
    )

    chart_buf.close()

async def handle_graph_action(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    action = query.data

    await query.answer()

    if action == "graph_choose":
        await send_message(
            update,
            "📊 Выберите тип графика:",
            reply_markup=get_graph_type_keyboard()
        )
    elif action == "show_menu":
        await menu(update, context)

async def handle_category_pagination(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    data = query.data

    if data.startswith("category_nav"):
        page = int(data.split("_")[2])
        await query.edit_message_reply_markup(reply_markup=get_categories_keyboard(page, CATEGORIES))
        return CATEGORY_PAGE
    elif data == "category_type":
        await query.edit_message_text(
            "✏️ Напишите название категории текстом. \n \n "
            f"Доступные: {', '.join(CATEGORIES)}",
            reply_markup=get_back_to_menu_keyboard()
        )
        return CATEGORY_TEXT
    elif data.startswith("category_"):
        category = data[9:]
        return await save_expense_and_show_menu(update, context, category)

    return ConversationHandler.END

async def handle_category_text_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = update.message.text.strip().lower()

    matches = [ category for category in CATEGORIES if text in category.lower() ]

    if len(matches) == 1:
        return await save_expense_and_show_menu(update, context, matches[0])
    elif len(matches) > 1:
        keyboard = [
            [InlineKeyboardButton(match, callback_data=f"category_{ match }")] for match in matches
        ]
        await update.message.reply_text(
            "Совпало несколько вариантов:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return CATEGORY_PAGE
    else:
        await update.message.reply_text(
            f"❌ Категория '{ text }' не найдена.",
            reply_markup=get_back_to_menu_keyboard()
        )
        return CATEGORY_TEXT

async def handle_clear_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id

    if query.data == "confirm_clear":
        deleted_count = clear_user_expenses(user_id)
        await query.edit_message_text(
            f"🗑 История расходов успешно очищена.\n Удалено записей: { deleted_count }",
            reply_markup=get_main_menu_keyboard()
        )
    elif query.data == "cancel_clear":
        await query.edit_message_text(
            "Удаление отменено.",
            reply_markup=get_main_menu_keyboard()
        )


async def handle_action_btns(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    action = query.data

    if action == "show_menu":
        await menu(update, context)
    elif action == "cmd_start":
        await restart_expense(update, context)
    elif action == "cmd_stats":
        await stats(update, context)
    elif action == "cmd_graph":
        await graph(update, context)
    elif action == "cmd_clear":
        await request_clear_history(update, context)
    elif action == "cmd_cancel":
        await cancel(update, context)

######

def main() -> None:
    create_database()
    app = Application.builder().token(BOT_TOKEN).build()

    conversation_handler = ConversationHandler(
        entry_points=[
            CommandHandler('start', start),
            CallbackQueryHandler(restart_expense, pattern="^new_expense$"),
            CallbackQueryHandler(restart_expense, pattern="^cmd_start$")
        ],
        states={
            AMOUNT: [ MessageHandler(filters.TEXT & ~filters.COMMAND, get_amount) ],
            CATEGORY_PAGE: [ CallbackQueryHandler(handle_category_pagination, pattern="^category_") ],
            CATEGORY_TEXT: [ MessageHandler(filters.TEXT & ~filters.COMMAND, handle_category_text_input) ]
        },
        fallbacks=[ CommandHandler('cancel', cancel) ]
    )

    app.add_handler(conversation_handler)

    app.add_handler(CallbackQueryHandler(
        handle_action_btns, 
        pattern="^(show_menu|cmd_start|cmd_stats|cmd_graph|cmd_cancel|cmd_clear)$"
    ))

    app.add_handler(CallbackQueryHandler(
        handle_graph_select,
        pattern="^graph_(pie|bar)$"
    ))

    app.add_handler(CallbackQueryHandler(
        handle_graph_action,
        pattern="^(graph_choose|show_menu)$"
    ))

    app.add_handler(CallbackQueryHandler(
        handle_clear_confirmation,
        pattern="^(confirm_clear|cancel_clear)$"
    ))

    app.add_handler(CommandHandler('menu', menu))
    app.add_handler(CommandHandler('stats', stats))
    app.add_handler(CommandHandler('graph', graph))
    app.add_handler(CommandHandler('clear', request_clear_history))

    app.add_error_handler(global_error_handler)

    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()