import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, MessageHandler, CommandHandler, CallbackQueryHandler, 
    ConversationHandler, filters, ContextTypes
)
from config import BOT_TOKEN
from database import create_database, add_expense, get_total_by_category
from utils import (
    send_message,
    get_main_menu_keyboard,
    get_back_to_menu_keyboard,
    get_categories_keyboard
)
from graphing import create_expenses_pie_chart

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

AMOUNT, CATEGORY = range(2)
CATEGORIES = ["Кафе", "Продукты", "Транспорт", "Развлечения", "Вредные привычки"]

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
    try:
        amount = float(update.message.text.replace(',', '.'))
        if amount <= 0:
            raise ValueError
        
        context.user_data["amount"] = amount

        await update.message.reply_text(
            f"Сумма: { amount }. Выберите категорию:", 
            reply_markup=get_categories_keyboard(CATEGORIES)
        )

        return CATEGORY
    except ValueError:
        await update.message.reply_text(f"Введите корректное положительное число. Попробуйте еще раз.")
        return AMOUNT

async def select_category(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    category = update.callback_query.data
    amount = context.user_data.get('amount')
    user_id = update.effective_user.id

    if not amount:
        await send_message(update, "Произошла ошибка. Начните с команды /start")
        return ConversationHandler.END

    add_expense(user_id, amount, category)
    context.user_data.clear()

    text = (
        "Расход записан! \n" 
        f"Сумма: { amount } \n" 
        f"Категория: { category }"
    )
    
    await send_message(
        update,
        text,
        reply_markup=get_main_menu_keyboard()
    )


    return ConversationHandler.END

######

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    stats_dict = get_total_by_category(update.effective_user.id)

    if not stats_dict:
        text = (
            "У вас нет записанных расходов! \n "
            "Ипользуйте /start чтобы записать расход."
        )
        await send_message(
            update,
            text,
            reply_markup=get_main_menu_keyboard
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
    stats_dict = get_total_by_category(update.effective_user.id)

    if not stats_dict:
        await send_message(
            update,
            "У вас пока нет записанных расходов. \n Создайте новый расход",
            reply_markup=get_main_menu_keyboard()
        )
        return

    chart_buf = create_expenses_pie_chart(stats_dict)

    await update.effective_message.reply_photo(
        photo=chart_buf,
        caption="📊 <b>График ваших расходов по категориям</b>",
        parse_mode="HTML",
        reply_markup=get_back_to_menu_keyboard()
    )

    chart_buf.close()

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

async def handle_action_btns(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    action = update.callback_query.data

    if action == "show_menu":
        await menu(update, context)
    elif action == "cmd_start":
        await restart_expense(update, context)
    elif action == "cmd_stats":
        await stats(update, context)
    elif action == "cmd_graph":
        await graph(update, context)
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
            CATEGORY: [ CallbackQueryHandler(select_category) ]
        },
        fallbacks=[ CommandHandler('cancel', cancel) ]
    )

    app.add_handler(conversation_handler)
    app.add_handler(CallbackQueryHandler(
        handle_action_btns, 
        pattern="^(show_menu|cmd_start|cmd_stats|cmd_graph|cmd_cancel)$"
    ))
    app.add_handler(CommandHandler('menu', menu))
    app.add_handler(CommandHandler('stats', stats))

    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()