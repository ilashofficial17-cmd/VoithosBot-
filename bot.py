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
    ConversationHandler,
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

# Состояния для ConversationHandler
WAITING_NAME = 1
WAITING_CONTACT = 2


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
            "Оставьте заявку и наш консультант свяжется с вами.\n\n"
            "Как вас зовут?",
        )
        return WAITING_NAME

    # 📋 ВИДЫ УСЛУГ
    elif text == "📋 Виды услуг":
        msg = (
            "📋 *ВИДЫ УСЛУГ*\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "🤖 *1. AI-БОТ*\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "Умный помощник который работает за тебя 24/7\n\n"
            "*Основное:*\n"
            "• Бот на 1 платформе (Telegram / IG / FB / сайт)\n"
            "• AI-консультант под твой бизнес\n"
            "• Сбор контактов → Google Sheets\n"
            "• 1 язык\n"
            "• Настройка под бренд\n"
            "• Срок: 7–10 дней\n\n"
            "*Дополнительные опции:*\n"
            "➕ +1 платформа — €300\n"
            "➕ +1 язык — €200\n"
            "➕ Онлайн-запись и бронирование — €400\n"
            "➕ Напоминания клиентам — €200\n"
            "➕ Генерация изображений в боте — €600\n"
            "➕ Реакция на комментарии / сторис — €350\n"
            "➕ Подключение к CRM — €400\n"
            "➕ Воронка продаж — €300\n"
            "➕ Поддержка и обновления — €150/мес\n\n"
            "💡 _Наведи на интересующую услугу для подробного описания_"
        )

        # Вторая часть сообщения (АВТОМАТИЗАЦИЯ)
        msg2 = (
            "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "⚙️ *2. АВТОМАТИЗАЦИЯ*\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "Убираем ручную работу — всё работает само\n\n"
            "*Основное:*\n"
            "• Аудит процессов бизнеса\n"
            "• Автоматизация 1 ключевого процесса\n"
            "• Например: заявка → уведомление → таблица → ответ клиенту\n"
            "• Срок: 5–7 дней\n\n"
            "*Дополнительные опции:*\n"
            "➕ +1 процесс — €400\n"
            "➕ Интеграция между платформами — €300\n"
            "➕ Авто-отчёты и аналитика — €350\n"
            "➕ Авто-выставление счетов — €300\n"
            "➕ Email / SMS рассылки — €250\n"
            "➕ Подключение к CRM — €400\n"
            "➕ Поддержка и обновления — €120/мес"
        )

        # Третья часть сообщения (ТАРГЕТИРОВАННАЯ РЕКЛАМА)
        msg3 = (
            "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "🎯 *3. ТАРГЕТИРОВАННАЯ РЕКЛАМА*\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "Реклама которая приводит реальных клиентов\n\n"
            "*Основное (€500/мес):*\n"
            "_не включая рекламный бюджет_\n\n"
            "• Настройка рекламного кабинета\n"
            "• 1 платформа (Meta / Google)\n"
            "• До 3 креативов в месяц\n"
            "• Аудитории и таргетинг\n"
            "• Еженедельный отчёт\n"
            "• Оптимизация кампаний\n\n"
            "*Дополнительные опции:*\n"
            "➕ +1 платформа — €200/мес\n"
            "➕ +3 креатива — €150\n"
            "➕ AI-генерация креативов — €200/мес\n"
            "➕ A/B тестирование — €150/мес\n"
            "➕ Ретаргетинг — €200/мес\n"
            "➕ Landing page под кампанию — €600 разово\n"
            "➕ Управление бюджетом — 10–15% от бюджета"
        )

        await update.message.reply_text(msg, parse_mode="Markdown")
        await update.message.reply_text(msg2, parse_mode="Markdown")
        await update.message.reply_text(msg3, parse_mode="Markdown", reply_markup=back_menu())

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
#  ФОРМА ЗАКАЗА - СБОР ИМЕНИ
# ─────────────────────────────────────────
async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Сбор имени клиента."""
    name = update.message.text
    context.user_data["name"] = name
    logger.info(f"📝 Имя: {name}")

    await update.message.reply_text(
        f"Спасибо, {name}!\n\n"
        "Теперь поделитесь контактом:\n\n"
        "• Телефон (например: +380501234567)\n"
        "• Или Telegram: @username"
    )
    return WAITING_CONTACT


# ─────────────────────────────────────────
#  ФОРМА ЗАКАЗА - СБОР КОНТАКТА
# ─────────────────────────────────────────
async def get_contact(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Сбор контакта и сохранение заявки."""
    contact = update.message.text
    name = context.user_data.get("name", "Unknown")

    logger.info(f"📞 Заявка: {name} | {contact}")

    await update.message.reply_text(
        f"✅ Спасибо!\n\n"
        f"Ваша заявка принята:\n"
        f"• Имя: {name}\n"
        f"• Контакт: {contact}\n\n"
        f"Наш консультант свяжется с вами в течение 24 часов.",
        reply_markup=main_menu(),
    )
    return -1


# ─────────────────────────────────────────
#  ЗАПУСК
# ─────────────────────────────────────────
def main() -> None:
    logger.info("=" * 50)
    logger.info("🚀 Voithos Bot стартует...")

    app = Application.builder().token(TOKEN).build()

    # ConversationHandler для формы заказа
    order_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.TEXT, handle_buttons)],
        states={
            WAITING_NAME: [MessageHandler(filters.TEXT, get_name)],
            WAITING_CONTACT: [MessageHandler(filters.TEXT, get_contact)],
        },
        fallbacks=[
            CommandHandler("menu", menu_command),
            MessageHandler(filters.Regex("^⬅️ Назад в меню$"), menu_command),
        ],
    )

    # Обработчики
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("menu", menu_command))
    app.add_handler(order_handler)

    logger.info("✅ Бот готов!")
    logger.info("=" * 50)

    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
