import logging
import os
import httpx
from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
    ConversationHandler,
)

# ─────────────────────────────────────────
#  Настройки
# ─────────────────────────────────────────
load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CONTACT_LINK = os.getenv("CONTACT_LINK", "https://t.me/voithos")
OPENROUTER_API_KEY = os.getenv("OPEN_ROUTER")

if not TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN не установлен в .env файле")

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# Логируем наличие переменных
if OPENROUTER_API_KEY:
    logger.info("OPEN_ROUTER ключ найден ✅")
else:
    logger.warning("OPEN_ROUTER ключ не установлен ⚠️ ИИ-консультант недоступен")

# Состояния для ConversationHandler
CONSULTING = 1

COMPANY_INFO = """
🚀 VOITHOS — Автоматизация бизнеса через ИИ-консультантов

ЧТО МЫ ДЕЛАЕМ:
Мы создаём ИИ-консультантов (ботов) под конкретный бизнес. Это не просто чат-бот — это полноценный виртуальный консультант, который знает ВСЮ информацию о вашем бизнесе и консультирует клиентов как профессионал.

КАК ЭТО РАБОТАЕТ:
1. Вы предоставляете нам ВСЕ данные вашего бизнеса:
   • Описание услуг/товаров
   • Процессы и регламенты
   • FAQ и типовые вопросы
   • Прайсы, акции, условия
   • Всё, что нужно знать консультанту

2. Мы создаём код и настраиваем ИИ-агента:
   • Разрабатываем бота под вашу платформу
   • Обучаем ИИ ВСЕМ аспектам вашего бизнеса
   • Настраиваем интеграции и логику
   • Тестируем и оптимизируем

3. Результат:
   • Бот консультирует 24/7 как профессионал
   • Увеличивает конверсию и экономит время
   • Не ошибается в информации о бизнесе
   • Передаёт сложные вопросы менеджеру

ПЛАТФОРМЫ:
• Telegram (основная) — начинаем отсюда
• Другие платформы (можем расширять)

НАШИ ПРЕИМУЩЕСТВА:
✅ Автоматизаторы с опытом — делаем быстро и качественно
✅ Обучение ИИ на реальных данных вашего бизнеса
✅ Не уступаем в качестве, но работаем оперативнее
✅ Цена зависит от уровня сложности бота — обсудим лично

ПРОЦЕСС РАЗРАБОТКИ:
1. Обсуждение — узнаём о вашем бизнесе
2. Сбор данных — вы предоставляете информацию
3. Разработка — пишем и настраиваем бота
4. Обучение ИИ — загружаем все знания о бизнесе
5. Тестирование — проверяем на реальных сценариях
6. Запуск и поддержка — бот готов работать

ПРИМЕРЫ ИСПОЛЬЗОВАНИЯ:
• Консультация по услугам (парикмахерская, салон красоты)
• Помощь в выборе (интернет-магазин, услуги)
• Ответы на вопросы (юридические услуги, недвижимость)
• Приём заявок и записей (автоматизированно)
• Поддержка клиентов (первая линия)

ЦЕН:
Обсуждаем лично в зависимости от:
• Сложности бота
• Объёма данных для обучения
• Нужны ли интеграции
• Требования к функционалу
"""


# ─────────────────────────────────────────
#  Главное меню
# ─────────────────────────────────────────
def main_menu_keyboard() -> ReplyKeyboardMarkup:
    keyboard = [
        ["🚀 Заказать бота", "🤖 Виды ботов"],
        ["💡 ИИ-Консультанты", "📈 Как это поможет?"],
        ["🤖 Демонстрация", "❌ Выход"],
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)


WELCOME_TEXT = (
    "👋 *Добро пожаловать в Voithos!*\n\n"
    "Мы разрабатываем Telegram-ботов и ИИ-консультантов для бизнеса.\n\n"
    "Выберите интересующий вас раздел 👇"
)


# ─────────────────────────────────────────
#  ИИ-Консультант через OpenRouter
# ─────────────────────────────────────────
async def get_ai_response(user_message: str) -> str:
    """Получить ответ от ИИ-консультанта через OpenRouter."""
    if not OPENROUTER_API_KEY:
        return "⚠️ ИИ-консультант недоступен. API ключ не настроен."

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                    "HTTP-Referer": "https://github.com/anastasija050806-rgb/VoithosBot-",
                    "X-Title": "VoithosBot",
                },
                json={
                    "model": "claude-3.5-sonnet",
                    "messages": [
                        {
                            "role": "system",
                            "content": f"""Ты профессиональный ИИ-консультант компании Voithos.

{COMPANY_INFO}

ТВОЯ РОЛЬ:
• Консультировать людей о наших услугах разработки ИИ-ботов
• Объяснять как работают наши консультанты
• Помогать людям понять, подходит ли им наше решение
• Отвечать на вопросы о процессе разработки
• Предлагать начать с обсуждения их потребностей

СТИЛЬ ОБЩЕНИЯ:
• Дружелюбный и профессиональный тон
• Понятные объяснения (не технический жаргон где не нужно)
• Фокус на пользу для их бизнеса
• Если не уверен — предложи обсудить лично с командой
• Краткие ответы (2-3 предложения), но информативные

ЧТО ЗНАЕШЬ О НАШИХ БОТАХ:
• Они обучаются на ВСЕХ данных бизнеса клиента
• Становятся экспертами в конкретной сфере
• Консультируют 24/7 как профессионал
• Экономят время и увеличивают конверсию
• Это не просто чат-бот, а рабочий инструмент

ПРЕДЛОЖЕНИЕ К ДЕЙСТВИЮ:
Если интересует — предложи обсудить детали:
"Давайте обсудим лично что нужно именно вам. Напишите в Telegram: {CONTACT_LINK}"
"""
                        },
                        {
                            "role": "user",
                            "content": user_message
                        }
                    ],
                    "temperature": 0.7,
                    "max_tokens": 600,
                }
            )

        if response.status_code == 200:
            data = response.json()
            return data["choices"][0]["message"]["content"]
        else:
            logger.error(f"OpenRouter API error: {response.status_code} - {response.text}")
            return "⚠️ Ошибка при получении ответа от ИИ."

    except httpx.TimeoutException:
        return "⏱️ Время ответа истекло. Попробуйте позже."
    except Exception as e:
        logger.error(f"AI response error: {e}")
        return f"❌ Ошибка: {str(e)[:100]}"


# ─────────────────────────────────────────
#  Команда /start
# ─────────────────────────────────────────
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.info(f"👤 /start от {update.effective_user.first_name}")
    context.user_data["mode"] = "menu"
    await update.message.reply_text(
        WELCOME_TEXT,
        parse_mode="Markdown",
        reply_markup=main_menu_keyboard(),
    )
    logger.info("✅ /start обработан")


# ─────────────────────────────────────────
#  Команда /menu — показать главное меню
# ─────────────────────────────────────────
async def menu_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    context.user_data["mode"] = "menu"
    await update.message.reply_text(
        WELCOME_TEXT,
        parse_mode="Markdown",
        reply_markup=main_menu_keyboard(),
    )


# ─────────────────────────────────────────
#  Обработчик нажатий на кнопки меню
# ─────────────────────────────────────────
async def handle_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обработчик выбора из главного меню."""
    text = update.message.text
    logger.info(f"📨 Сообщение: '{text}' от {update.effective_user.first_name}")

    try:
    if text == "🚀 Заказать бота":
        msg = (
            "📩 *Заказать бота*\n\n"
            "Мы готовы разработать бота под любую задачу вашего бизнеса!\n\n"
            "Свяжитесь с нами — расскажите о своей идее, "
            "и мы предложим оптимальное решение.\n\n"
            f"👉 [Написать нам]({CONTACT_LINK})"
        )
        await update.message.reply_text(msg, parse_mode="Markdown", reply_markup=main_menu_keyboard())

    # Виды ботов
    elif text == "🤖 Виды ботов":
        msg = (
            "🤖 *Виды ботов, которые мы разрабатываем*\n\n"
            "• *ИИ-консультант* — отвечает на вопросы клиентов 24/7\n"
            "• *Бот для записи* — принимает заявки и бронирования\n"
            "• *Интернет-магазин* — продаёт товары прямо в Telegram\n"
            "• *CRM-бот* — управляет клиентской базой\n"
            "• *Рассылки и уведомления* — держит клиентов в курсе\n"
            "• *Бот для HR* — автоматизирует найм и онбординг\n\n"
            "_Нет нужного? Мы разработаем под ваши задачи!_"
        )
        await update.message.reply_text(msg, parse_mode="Markdown", reply_markup=main_menu_keyboard())

    # ИИ-Консультанты (информация)
    elif text == "💡 ИИ-Консультанты":
        msg = (
            "💡 *Как работают ИИ-Консультанты?*\n\n"
            "1️⃣ *Обучение на вашей базе знаний*\n"
            "   Загружаем информацию о вашем бизнесе, товарах и услугах.\n\n"
            "2️⃣ *Понимание естественного языка*\n"
            "   Клиент пишет свободным текстом — бот понимает суть вопроса.\n\n"
            "3️⃣ *Мгновенные ответы*\n"
            "   Бот отвечает за секунды, без ожидания оператора.\n\n"
            "4️⃣ *Передача сложных вопросов менеджеру*\n"
            "   Если бот не знает ответа — он уведомит живого сотрудника.\n\n"
            "5️⃣ *Постоянное улучшение*\n"
            "   Бот учится на новых вопросах и становится умнее."
        )
        await update.message.reply_text(msg, parse_mode="Markdown", reply_markup=main_menu_keyboard())

    # Как это поможет бизнесу
    elif text == "📈 Как это поможет?":
        msg = (
            "📈 *Как это поможет вашему бизнесу?*\n\n"
            "✅ *Экономия времени* — бот обрабатывает сотни запросов одновременно\n\n"
            "✅ *Снижение затрат* — меньше операторов на рутинных задачах\n\n"
            "✅ *Работа 24/7* — клиенты получают ответы в любое время\n\n"
            "✅ *Рост конверсии* — мгновенный отклик удерживает клиента\n\n"
            "✅ *Сбор данных* — аналитика по вопросам и поведению клиентов\n\n"
            "✅ *Масштабируемость* — бот справляется с любым объёмом запросов\n\n"
            "_Средний ROI от внедрения бота — окупаемость за 1–3 месяца._"
        )
        await update.message.reply_text(msg, parse_mode="Markdown", reply_markup=main_menu_keyboard())

    # Демонстрация (ИИ-консультант)
    elif text == "🤖 Демонстрация":
        context.user_data["mode"] = "consulting"
        await update.message.reply_text(
            "🤖 *Демонстрация ИИ-Консультанта*\n\n"
            "Задайте любой вопрос о наших услугах. Введите /menu для возврата в главное меню.",
            parse_mode="Markdown",
            reply_markup=ReplyKeyboardRemove()
        )
        return CONSULTING

    # Выход
    elif text == "❌ Выход":
        await update.message.reply_text("До встречи! 👋", reply_markup=ReplyKeyboardRemove())
        logger.info(f"👋 Выход {update.effective_user.first_name}")
        return -1

        logger.info(f"✅ Обработан: {text}")
    except Exception as e:
        logger.error(f"❌ Ошибка при обработке '{text}': {e}", exc_info=True)
        await update.message.reply_text("Ошибка! Используйте меню.", reply_markup=main_menu_keyboard())

    return -1


# ─────────────────────────────────────────
#  Обработчик режима консультации
# ─────────────────────────────────────────
async def consulting_mode(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обработчик ИИ-консультанта в режиме демонстрации."""
    user_message = update.message.text

    # Проверка на команду выхода
    if user_message == "/menu":
        context.user_data["mode"] = "menu"
        await update.message.reply_text(
            WELCOME_TEXT,
            parse_mode="Markdown",
            reply_markup=main_menu_keyboard(),
        )
        return -1

    # Показываем, что бот печатает
    await update.message.chat.send_action("typing")

    # Получаем ответ от ИИ
    response = await get_ai_response(user_message)

    await update.message.reply_text(
        response,
        parse_mode="Markdown",
    )

    return CONSULTING


# ─────────────────────────────────────────
#  Запуск
# ─────────────────────────────────────────
def main() -> None:
    try:
        logger.info("=" * 50)
        logger.info("🚀 Инициализация Voithos Bot")
        logger.info(f"Token установлен: {'✅' if TOKEN else '❌'}")
        logger.info(f"Contact Link: {CONTACT_LINK}")
        logger.info(f"OpenRouter API: {'✅' if OPENROUTER_API_KEY else '❌'}")

        app = Application.builder().token(TOKEN).build()
        logger.info("✅ Приложение Telegram создано")

        # ConversationHandler для управления состояниями
        conv_handler = ConversationHandler(
            entry_points=[
                CommandHandler("start", start),
                CommandHandler("menu", menu_command),
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_menu),
            ],
            states={
                CONSULTING: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, consulting_mode),
                ],
            },
            fallbacks=[
                CommandHandler("menu", menu_command),
                MessageHandler(filters.Regex("^/menu$"), menu_command),
            ],
        )

        app.add_handler(conv_handler)
        logger.info("✅ Обработчики добавлены")

        logger.info("=" * 50)
        logger.info("✅ Voithos Bot запущен и готов к работе!")
        logger.info("=" * 50)
        app.run_polling(allowed_updates=Update.ALL_TYPES)
    except Exception as e:
        logger.error("=" * 50)
        logger.error(f"❌ КРИТИЧЕСКАЯ ОШИБКА: {e}")
        logger.error("=" * 50)
        logger.error("Полная информация об ошибке:", exc_info=True)
        raise


if __name__ == "__main__":
    main()
