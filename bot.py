import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, MessageHandler, CommandHandler, CallbackQueryHandler, 
    ConversationHandler, filters, ContextTypes
)
from config import BOT_TOKEN
from database import create_database, add_expense, get_total_by_category
from datetime import date

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

AMOUNT, CATEGORY = range(2)

CATEGORIES = ["Кафе", "Продукты", "Транспорт", "Развлечения", "Вредные привычки"]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Привет! Это бот для подсчета расходов. Введите сумму расхода:")
    return AMOUNT

async def restart_expense(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()

    await query.edit_message_text("➕ Введите сумму нового расхода:")
    return AMOUNT

async def get_amount(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = update.message.text

    try:
        amount = float(text.replace(',', '.'))
        if amount <= 0:
            raise ValueError
        
        context.user_data["amount"] = amount

        keyboard = [[InlineKeyboardButton(category, callback_data=category)] for category in CATEGORIES]

        await update.message.reply_text(f"Сумма: { amount }. Выберите категорию:", reply_markup=InlineKeyboardMarkup(keyboard))

        return CATEGORY
    except ValueError:
        await update.message.reply_text(f"Введите корректное положительное число. Попробуйте еще раз.")
        return AMOUNT

async def select_category(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()

    category = query.data
    amount = context.user_data.get('amount')
    user_id = update.effective_user.id

    if not amount:
        await query.edit_message_text("Произошла ошибка. Начните с команды /start")
        return ConversationHandler.END

    add_expense(user_id, amount, category)

    keyboard = [
        [
            InlineKeyboardButton("➕ Новый расход", callback_data="new_expense")
        ],
        [
            InlineKeyboardButton("📋 Меню", callback_data="show_menu")
        ]
    ]

    await query.edit_message_text(text=f"Расход записан! \n Сумма: { amount } \n Категория: { category }", reply_markup=InlineKeyboardMarkup(keyboard))

    context.user_data.clear()

    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Действие отменено")
    context.user_data.clear()
    return ConversationHandler.END

async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = (
        "<b>Доступные команды:</b>\n\n"
        "/start — Начать запись нового расхода\n"
        "/menu — Показать это меню\n"
        "/stats — Посмотреть статистику трат\n"
        "/graph — Посмотреть график трат\n"
        "/cancel — Отменить текущее действие\n"
    )
    await update.message.reply_text(text, parse_mode="HTML")

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    stats_dict = get_total_by_category(user_id)

    keyboard = [
        [InlineKeyboardButton("➕ Новый расход", callback_data="new_expense")],
        [InlineKeyboardButton("📋 Открыть меню", callback_data="show_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if not stats_dict:
        await update.message.reply_text(
            "У вас нет записанных расходов! \n " \
            "Ипользуйте /start чтобы записать расход.",
            reply_markup=reply_markup
        )
        return

    text = "📊 <b>Ваша статистика трат:</b>\n\n"
    total_amount = 0.0

    sorted_stats = sorted(stats_dict.items(), key=lambda item: item[1], reverse=True)

    for category, amount in sorted_stats:
        text += f"<b>*</b> { category }: <b>{amount:.2f}</b>\n"
        total_amount += amount

    text += f"\n <b>Итого потрачено:</b> {total_amount:.2f}"

    await update.message.reply_text(text, parse_mode="HTML", reply_markup=reply_markup)

async def handle_action_btns(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    action = query.data

    if action == "show_menu":
        text = (
                "<b>Доступные команды:</b>\n\n"
                "/start — Начать запись нового расхода\n"
                "/menu — Показать это меню\n"
                "/stats — Посмотреть статистику трат\n"
                "/graph — Посмотреть график трат\n"
                "/cancel — Отменить текущее действие\n"
            )
        
        await query.edit_message_text(text, parse_mode="HTML")

def main() -> None:
    create_database()
    app = Application.builder().token(BOT_TOKEN).build()

    conversation_handler = ConversationHandler(
        entry_points=[
            CommandHandler('start', start),
            CallbackQueryHandler(restart_expense, pattern="^new_expense$")
        ],
        states={
            AMOUNT: [ MessageHandler(filters.TEXT & ~filters.COMMAND, get_amount) ],
            CATEGORY: [ CallbackQueryHandler(select_category) ]
        },
        fallbacks=[ CommandHandler('cancel', cancel) ]
    )

    app.add_handler(conversation_handler)
    app.add_handler(CallbackQueryHandler(handle_action_btns, pattern="^(new_expense|show_menu)$"))
    app.add_handler(CommandHandler('menu', menu))
    app.add_handler(CommandHandler('stats', stats))

    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()