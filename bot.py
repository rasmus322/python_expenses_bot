import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, MessageHandler, CommandHandler, CallbackQueryHandler, 
    ConversationHandler, filters, ContextTypes
)
from config import BOT_TOKEN

logging.basicConfig(format='$(asctime)s - $(name)s - $(levelname)s - $(message)s', level=logging.INFO)

AMOUNT, CATEGORY = range(2)

CATEGORIES = ["Кафе", "Продукты", "Транспорт", "Развлечения", "Вредные привычки"]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Привет! Это бот для подсчета расходов. Введите сумму расхода:")
    return AMOUNT

async def get_amount(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = update.message.text

    try:
        amount = float(text.replace(',', '.'))
        if amount <= 0:
            raise ValueError("Сумма должна быть > 0")
        
        context.user_data["amount"] = amount

        keyboard = [[InlineKeyboardButton(category, callback_data=category)] for category in CATEGORIES]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(f"Сумма: { amount }. Выберите категорию:", reply_markup=reply_markup)

        return CATEGORY
    except ValueError as error:
        await update.message.reply_text(f"Введите корректное число! Попробуйте еще раз: {error}")
        return AMOUNT

async def select_category(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()

    cateogry = query.data
    amount = context.user_data.get('amount')

    if not amount:
        await update.message.reply_text(f"Сумма не была записана... \n Пожалуйста начните с команды /start")
        return ConversationHandler.END

    await query.edit_message_text(text=f"Расход записан! \n Сумма: { amount } \n Категория: { cateogry }")

    context.user_data.clear()

    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Действие отменено")
    context.user_data.clear()
    return ConversationHandler.END

def main() -> None:
    app = Application.builder().token(BOT_TOKEN).build()

    conversation_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            AMOUNT: [ MessageHandler(filters.TEXT & ~filters.COMMAND, get_amount) ],
            CATEGORY: [ CallbackQueryHandler(select_category) ]
        },
        fallbacks=[ CommandHandler('cancel', cancel) ]
    )

    app.add_handler(conversation_handler)

    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()