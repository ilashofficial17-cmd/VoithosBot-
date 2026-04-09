import logging
import os
from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    CallbackQueryHandler,
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
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🤖 AI-Бот", callback_data="service_aibot")],
            [InlineKeyboardButton("⚙️ Автоматизация", callback_data="service_auto")],
            [InlineKeyboardButton("🎯 Таргетированная реклама", callback_data="service_ads")],
        ])

        await update.message.reply_text(
            "📋 *НАШИ УСЛУГИ*\n\n"
            "Мы помогаем бизнесу расти с помощью технологий\.\n"
            "Каждое решение — под ваши задачи и цели\.\n\n"
            "Выберите услугу, чтобы узнать подробнее 👇",
            parse_mode="MarkdownV2",
            reply_markup=keyboard,
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
#  ИНЛАЙН-КНОПКИ УСЛУГ
# ─────────────────────────────────────────
def services_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура выбора услуг."""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🤖 AI-Бот", callback_data="service_aibot")],
        [InlineKeyboardButton("⚙️ Автоматизация", callback_data="service_auto")],
        [InlineKeyboardButton("🎯 Таргетированная реклама", callback_data="service_ads")],
    ])


SERVICES = {
    "service_aibot": (
        "🤖 *AI\-БОТ*\n\n"
        "Умный помощник, который работает за тебя 24/7\n\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "📦 *Что входит:*\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        "▸ Бот на любой платформе на выбор:\n"
        "  Telegram, Instagram, Facebook или сайт\n"
        "▸ AI\-консультант, обученный под\n"
        "  твой бизнес и бренд\n"
        "▸ Автоматический сбор контактов\n"
        "  в Google Sheets или другие программы\n"
        "▸ Поддержка любого языка\n\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "✨ *Можно добавить:*\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        "➕ Онлайн\-запись и бронирование\n"
        "➕ Автоматические напоминания клиентам\n"
        "➕ Генерация изображений прямо в боте\n"
        "➕ Реакция на комментарии и сторис\n"
        "➕ Интеграция с CRM\-системой\n"
        "➕ Воронка продаж\n"
        "➕ Поддержка и обновления после запуска"
    ),
    "service_auto": (
        "⚙️ *АВТОМАТИЗАЦИЯ*\n\n"
        "Убираем рутину — бизнес работает сам\n\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "📦 *Что входит:*\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        "▸ Аудит твоих процессов: находим\n"
        "  где теряется время и деньги\n"
        "▸ Автоматизация одного ключевого процесса\n"
        "  _Например: заявка → уведомление →_\n"
        "  _таблица → ответ клиенту_\n\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "✨ *Можно добавить:*\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        "➕ Автоматизация дополнительных процессов\n"
        "➕ Интеграция между платформами и сервисами\n"
        "➕ Авто\-отчёты и аналитика\n"
        "➕ Автоматическое выставление счетов\n"
        "➕ Интеграция с CRM\-системой\n"
        "➕ Поддержка и обновления после запуска"
    ),
    "service_ads": (
        "🎯 *ТАРГЕТИРОВАННАЯ РЕКЛАМА*\n\n"
        "Реклама, которая приводит реальных клиентов\n"
        "_Рекламный бюджет оплачивается отдельно_\n\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "📦 *Что входит:*\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        "▸ Настройка рекламного кабинета с нуля\n"
        "▸ Ведение рекламы на одной или более\n"
        "  платформ: Meta, Google и TikTok\n"
        "▸ Креативы — баннеры и тексты объявлений\n"
        "▸ Настройка аудиторий и таргетинга\n"
        "▸ Постоянная оптимизация кампаний\n\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "✨ *Можно добавить:*\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        "➕ AI\-генерация рекламных материалов\n"
        "➕ A/B тестирование объявлений\n"
        "➕ Ретаргетинг — возвращаем тех,\n"
        "  кто уже интересовался\n"
        "➕ Landing page под рекламную кампанию\n"
        "➕ Управление рекламным бюджетом"
    ),
}


async def handle_service_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработка нажатий на инлайн-кнопки услуг."""
    query = update.callback_query
    await query.answer()

    data = query.data

    if data in SERVICES:
        back_kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("⬅️ Назад к услугам", callback_data="back_to_services")],
        ])
        await query.message.edit_text(
            SERVICES[data],
            parse_mode="MarkdownV2",
            reply_markup=back_kb,
        )

    elif data == "back_to_services":
        await query.message.edit_text(
            "📋 *НАШИ УСЛУГИ*\n\n"
            "Мы помогаем бизнесу расти с помощью технологий\.\n"
            "Каждое решение — под ваши задачи и цели\.\n\n"
            "Выберите услугу, чтобы узнать подробнее 👇",
            parse_mode="MarkdownV2",
            reply_markup=services_keyboard(),
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
    app.add_handler(CallbackQueryHandler(handle_service_callback))
    app.add_handler(order_handler)

    logger.info("✅ Бот готов!")
    logger.info("=" * 50)

    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
