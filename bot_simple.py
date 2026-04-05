import logging
import os
from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CONTACT_LINK = os.getenv("CONTACT_LINK", "https://t.me/voithos")

if not TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN не установлен!")

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


def main_menu() -> ReplyKeyboardMarkup:
    keyboard = [
        ["🚀 Заказать", "🤖 Виды ботов"],
        ["💡 ИИ-Консультанты", "📈 Преимущества"],
        ["❌ Выход"],
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "👋 Добро пожаловать в Voithos!\n\nВыберите раздел:",
        reply_markup=main_menu(),
    )


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = update.message.text

    if text == "🚀 Заказать":
        await update.message.reply_text(
            f"📩 Свяжитесь с нами: {CONTACT_LINK}",
            reply_markup=main_menu(),
        )
    elif text == "❌ Выход":
        await update.message.reply_text("До встречи! 👋")
    else:
        await update.message.reply_text(
            "Используйте кнопки меню 👇",
            reply_markup=main_menu(),
        )


def main() -> None:
    logger.info("=" * 50)
    logger.info("🚀 Voithos Bot (SIMPLE) стартует...")

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT, handle_text))

    logger.info("✅ Бот готов!")
    logger.info("=" * 50)

    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
