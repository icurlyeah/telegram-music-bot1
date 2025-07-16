from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from datetime import datetime, timedelta

BOT_TOKEN = '7853937473:AAEFMDYSFML3T18yxu_XsLT54-q5_flmUeE'
ADMINS = [303542406, 458198861]

STYLE_KEYBOARD = ReplyKeyboardMarkup(
    keyboard=[
        ["🎤 Рэп", "🎶 Поп", "🎸 Рок"],
        ["🔥 Хип-хоп", "🔫 Дрилл", "🎧 Техно"],
        ["🎷 Джаз", "🕺 Рок-н-ролл", "🎻 Классика"],
        ["🎹 Блюз", "🕊 Соул", "🪩 Диско"],
        ["🌌 Лоуфай", "🪗 Фолк", "🤷 Другое"]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)

ACTION_KEYBOARD = ReplyKeyboardMarkup(
    keyboard=[["🔙 Назад", "🗑 Сбросить заявку"]],
    resize_keyboard=True
)

CONFIRM_KEYBOARD = ReplyKeyboardMarkup(
    keyboard=[
        ["✅ Отправить", "✏ Изменить текст"],
        ["🔙 Назад", "🗑 Сбросить заявку"]
    ],
    resize_keyboard=True
)

GENRES = [
    "🎤 Рэп", "🎶 Поп", "🎸 Рок", "🔥 Хип-хоп", "🔫 Дрилл", "🎧 Техно",
    "🎷 Джаз", "🕺 Рок-н-ролл", "🎻 Классика", "🎹 Блюз", "🕊 Соул", "🪩 Диско",
    "🌌 Лоуфай", "🪗 Фолк"
]

# Хранилище заявок по пользователям
user_requests = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text(
        "Привет! 👋\nВыбери стиль трека кнопкой ниже 🎵",
        reply_markup=STYLE_KEYBOARD
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    text = update.message.text.strip()
    user_id = user.id
    username = f"@{user.username}" if user.username else "Без username"

    now = datetime.now()
    today_key = now.strftime('%Y-%m-%d')
    user_data = user_requests.setdefault(user_id, {})
    user_data.setdefault(today_key, [])

    if len(user_data[today_key]) >= 5 and not context.user_data.get("awaiting_confirmation"):
        await update.message.reply_text("❗ Вы уже отправили 5 заявок сегодня. Приходи завтра!")
        return

    if context.user_data.get("awaiting_custom_style"):
        if text == "🔙 Назад":
            context.user_data.clear()
            await update.message.reply_text("⬅ Вернулись к выбору жанра", reply_markup=STYLE_KEYBOARD)
            return
        context.user_data["style"] = text
        context.user_data.pop("awaiting_custom_style")
        await update.message.reply_text(
            f"✅ Стиль сохранён: {text}\nТеперь отправь текст трека.",
            reply_markup=ACTION_KEYBOARD
        )
        return

    if text == "🔙 Назад":
        context.user_data.clear()
        await update.message.reply_text("⬅ Вернулись к выбору жанра", reply_markup=STYLE_KEYBOARD)
        return

    if text == "🗑 Сбросить заявку":
        context.user_data.clear()
        await update.message.reply_text("Заявка сброшена. Начни заново 🔁", reply_markup=STYLE_KEYBOARD)
        return

    if text == "✅ Отправить" and context.user_data.get("awaiting_confirmation"):
        style = context.user_data.get("style", "Не указан")
        text_content = context.user_data.get("text", "Нет текста")
        formatted_msg = (
            f"🎧 <b>Заявка от:</b> {username} (ID: <code>{user_id}</code>)\n"
            f"🎼 <b>Стиль:</b> {style}\n"
            f"📝 <b>Текст:</b>\n{text_content}"
        )
        for admin_id in ADMINS:
            await context.bot.send_message(chat_id=admin_id, text=formatted_msg, parse_mode="HTML")

        user_data[today_key].append(now)

        await update.message.reply_text(
            "✅ Спасибо! Твоя заявка принята.\nРезультаты и релизы мы публикуем в канале 👇",
            reply_markup=ReplyKeyboardRemove()
        )

        await update.message.reply_text(
            "Перейти в канал",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(text="@musexfm", url="https://t.me/musexfm")],
                [InlineKeyboardButton(text="Оставить новую заявку", callback_data="new_request")]
            ])
        )
        context.user_data.clear()
        return

    if text == "✏ Изменить текст" and context.user_data.get("awaiting_confirmation"):
        old_text = context.user_data.get("text", "")
        context.user_data.pop("awaiting_confirmation")
        await update.message.reply_text(
            f"✏ Ты можешь изменить предыдущий текст или ввести новый.\n\n"
            f"<em>Предыдущий текст:</em>\n<code>{old_text}</code>",
            parse_mode="HTML"
        )
        return

    if text in GENRES:
        context.user_data["style"] = text
        await update.message.reply_text(
            f"Ты выбрал стиль: {text} 🎶\nТеперь отправь текст для трека.",
            reply_markup=ACTION_KEYBOARD
        )
        return

    if text == "🤷 Другое":
        context.user_data["awaiting_custom_style"] = True
        await update.message.reply_text(
            "Напиши свой жанр 🎼 (например: Инди, Панк, Гранж...)\n\nИли нажми 🔙 Назад, чтобы вернуться.",
            reply_markup=ReplyKeyboardMarkup(keyboard=[["🔙 Назад"]], resize_keyboard=True)
        )
        return

    style = context.user_data.get("style", "Не указан")
    context.user_data["text"] = text
    preview = (
        f"🎼 <b>Стиль:</b> {style}\n"
        f"📝 <b>Текст:</b>\n{text}"
    )
    await update.message.reply_text(
        f"👀 Предпросмотр заявки:\n\n{preview}\n\nНажми ✅ чтобы отправить или ✏ чтобы изменить текст.",
        parse_mode="HTML",
        reply_markup=CONFIRM_KEYBOARD
    )
    context.user_data["awaiting_confirmation"] = True
    return

from telegram.ext import CallbackQueryHandler, Application

import asyncio

async def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(lambda update, context: start(update.callback_query, context), pattern="^new_request$"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("✅ Бот запущен. Полная логика готова.")
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
