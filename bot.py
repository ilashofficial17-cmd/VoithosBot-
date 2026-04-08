import logging
import os
from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

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


# ─────────────────────────────────────────
#  ГЛАВНОЕ МЕНЮ
# ─────────────────────────────────────────
def main_menu() -> ReplyKeyboardMarkup:
    """Главное меню с 4 кнопками."""
    keyboard = [
        ["🛍️ Заказать услуги", "📋 Виды услуг"],
        ["🤖 Демонстрация", "💡 Чем мы полезны"],
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def back_menu() -> ReplyKeyboardMarkup:
    """Кнопка назад в меню."""
    keyboard = [["⬅️ Назад в меню"]]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


# ─────────────────────────────────────────
#  /START
# ─────────────────────────────────────────
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Приветствие и главное меню."""
    logger.info(f"👤 /start от {update.effective_user.first_name}")

    await update.message.reply_text(
        "👋 Добро пожаловать в Voithos!\n\n"
        "Выберите что вас интересует:",
        reply_markup=main_menu(),
    )


# ─────────────────────────────────────────
#  /MENU
# ─────────────────────────────────────────
async def menu_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Вернуться в главное меню."""
    logger.info(f"📋 /menu от {update.effective_user.first_name}")

    await update.message.reply_text(
        "Выберите опцию:",
        reply_markup=main_menu(),
    )


# ─────────────────────────────────────────
#  ОБРАБОТКА КНОПОК
# ─────────────────────────────────────────
async def handle_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработка всех кнопок меню."""
    text = update.message.text
    logger.info(f"📨 {text} от {update.effective_user.first_name}")

    # НАЗАД В МЕНЮ
    if text == "⬅️ Назад в меню":
        await update.message.reply_text(
            "Выберите опцию:",
            reply_markup=main_menu(),
        )

    # 🛍️ ЗАКАЗАТЬ УСЛУГИ
    elif text == "🛍️ Заказать услуги":
        await update.message.reply_text(
            "🛍️ ЗАКАЗАТЬ УСЛУГИ\n\n"
            "(Контент будет здесь)",
            reply_markup=back_menu(),
        )

    # 📋 ВИДЫ УСЛУГ
    elif text == "📋 Виды услуг":
        await update.message.reply_text(
            "📋 ВИДЫ УСЛУГ\n\n"
            "(Контент будет здесь)",
            reply_markup=back_menu(),
        )

    # 🤖 ДЕМОНСТРАЦИЯ
    elif text == "🤖 Демонстрация":
        await update.message.reply_text(
            "🤖 ДЕМОНСТРАЦИЯ ИИ-КОНСУЛЬТАНТА\n\n"
            "(Контент будет здесь)",
            reply_markup=back_menu(),
        )

    # 💡 ЧЕМ МЫ ПОЛЕЗНЫ
    elif text == "💡 Чем мы полезны":
        await update.message.reply_text(
            "💡 ЧЕМ МЫ ПОЛЕЗНЫ\n\n"
            "(Контент будет здесь)",
            reply_markup=back_menu(),
        )

    # НЕИЗВЕСТНОЕ СООБЩЕНИЕ
    else:
        await update.message.reply_text(
            "Используйте кнопки меню 👇",
            reply_markup=main_menu(),
        )


# ─────────────────────────────────────────
#  ЗАПУСК
# ─────────────────────────────────────────
def main() -> None:
    logger.info("=" * 50)
    logger.info("🚀 Voithos Bot стартует...")

    app = Application.builder().token(TOKEN).build()

    # Обработчики
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("menu", menu_command))
    app.add_handler(MessageHandler(filters.TEXT, handle_buttons))

    logger.info("✅ Бот готов!")
    logger.info("=" * 50)

    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
