import logging
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    filters, ContextTypes, ConversationHandler
)

TOKEN = "8755191668:AAHUma9bFGRiE2CedQWyUMO6UesyMRmxRro"
ADMIN_CHAT_ID = 5773143142

# States
NAME, PHONE, SIZES, SKETCH, COMMENT = range(5)

logging.basicConfig(level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [["📝 Оставить заявку"], ["ℹ️ О нас", "📞 Контакты"]]
    await update.message.reply_text(
        "👋 Добро пожаловать в *ПОЛИМАН*!\n\n"
        "Изготавливаем изделия из полипропилена в Новороссийске:\n"
        "🚐 Баки для автодома\n"
        "🏠 Накопительные ёмкости для квартир\n"
        "🛁 Купели, поддоны, нестандартные изделия\n\n"
        "Нажмите кнопку ниже чтобы оставить заявку 👇",
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )

async def info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🏭 *ПОЛИМАН* — производство изделий из листового полипропилена\n\n"
        "📍 Новороссийск\n"
        "✅ Любые размеры и формы под заказ\n"
        "✅ Работаем по чертежу или эскизу\n"
        "✅ Выезд на замер бесплатно\n"
        "✅ 3D-модель при необходимости",
        parse_mode="Markdown"
    )

async def contacts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📞 *Контакты ПОЛИМАН*\n\n"
        "Telegram: @NvrskAlexandr\n"
        "📍 Новороссийск\n\n"
        "Пишите — отвечаем быстро!",
        parse_mode="Markdown"
    )

async def start_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📝 *Оформление заявки*\n\n"
        "Шаг 1 из 5\n\n"
        "Введите ваше *имя*:",
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardRemove()
    )
    return NAME

async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["name"] = update.message.text
    await update.message.reply_text(
        "Шаг 2 из 5\n\n"
        "Введите ваш *номер телефона*:",
        parse_mode="Markdown"
    )
    return PHONE

async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["phone"] = update.message.text
    await update.message.reply_text(
        "Шаг 3 из 5\n\n"
        "Укажите *размеры* изделия\n"
        "_(длина × ширина × высота, объём или другие параметры)_:",
        parse_mode="Markdown"
    )
    return SIZES

async def get_sizes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["sizes"] = update.message.text
    keyboard = [["⏭ Пропустить"]]
    await update.message.reply_text(
        "Шаг 4 из 5\n\n"
        "Прикрепите *эскиз или фото* (если есть)\n"
        "или нажмите «Пропустить»:",
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )
    return SKETCH

async def get_sketch(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.photo:
        context.user_data["sketch"] = update.message.photo[-1].file_id
        context.user_data["has_sketch"] = True
    else:
        context.user_data["has_sketch"] = False

    await update.message.reply_text(
        "Шаг 5 из 5\n\n"
        "Добавьте *комментарий* к заявке\n"
        "_(цвет, материал, особые пожелания или «без комментариев»)_:",
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardRemove()
    )
    return COMMENT

async def get_comment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["comment"] = update.message.text
    data = context.user_data
    user = update.effective_user

    # Send to admin
    admin_msg = (
        "🔔 *НОВАЯ ЗАЯВКА — ПОЛИМАН*\n"
        "━━━━━━━━━━━━━━━━━━\n"
        f"👤 *Имя:* {data.get('name')}\n"
        f"📞 *Телефон:* {data.get('phone')}\n"
        f"📐 *Размеры:* {data.get('sizes')}\n"
        f"🖼 *Эскиз:* {'Прикреплён' if data.get('has_sketch') else 'Нет'}\n"
        f"💬 *Комментарий:* {data.get('comment')}\n"
        "━━━━━━━━━━━━━━━━━━\n"
        f"🆔 Telegram: @{user.username or 'нет'} (ID: {user.id})"
    )

    await context.bot.send_message(
        chat_id=ADMIN_CHAT_ID,
        text=admin_msg,
        parse_mode="Markdown"
    )

    # If sketch attached — forward photo too
    if data.get("has_sketch"):
        await context.bot.send_photo(
            chat_id=ADMIN_CHAT_ID,
            photo=data["sketch"],
            caption=f"Эскиз от {data.get('name')} / {data.get('phone')}"
        )

    # Confirm to user
    keyboard = [["📝 Оставить заявку"], ["ℹ️ О нас", "📞 Контакты"]]
    await update.message.reply_text(
        "✅ *Заявка принята!*\n\n"
        "Мы свяжемся с вами в ближайшее время для уточнения деталей и расчёта стоимости.\n\n"
        "Спасибо, что выбрали *ПОЛИМАН*! 🏭",
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )

    context.user_data.clear()
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [["📝 Оставить заявку"], ["ℹ️ О нас", "📞 Контакты"]]
    await update.message.reply_text(
        "Заявка отменена. Возвращайтесь когда будете готовы! 👋",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )
    context.user_data.clear()
    return ConversationHandler.END

def main():
    app = Application.builder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[
            MessageHandler(filters.Regex("^📝 Оставить заявку$"), start_order)
        ],
        states={
            NAME:    [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            PHONE:   [MessageHandler(filters.TEXT & ~filters.COMMAND, get_phone)],
            SIZES:   [MessageHandler(filters.TEXT & ~filters.COMMAND, get_sizes)],
            SKETCH:  [
                MessageHandler(filters.PHOTO, get_sketch),
                MessageHandler(filters.Regex("^⏭ Пропустить$"), get_sketch),
            ],
            COMMENT: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_comment)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(conv_handler)
    app.add_handler(MessageHandler(filters.Regex("^ℹ️ О нас$"), info))
    app.add_handler(MessageHandler(filters.Regex("^📞 Контакты$"), contacts))

    print("ПОЛИМАН бот запущен...")
    app.run_polling()

if __name__ == "__main__":
    main()
