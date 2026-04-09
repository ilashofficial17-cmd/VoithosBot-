import logging
import os
from openai import AsyncOpenAI
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
CONTACT_LINK = os.getenv("CONTACT_LINK", "https://t.me/Foxsiiiii")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

if not TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN не установлен!")

# OpenRouter клиент
ai_client = AsyncOpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY or "",
)

AI_MODEL = os.getenv("AI_MODEL", "openai/gpt-4o-mini")

SYSTEM_PROMPT = """Ты — AI-консультант компании Aicore (Applied AI for Growth). Твоя задача — помочь клиенту разобраться в услугах и подобрать подходящее решение.

Говори дружелюбно, на «ты», коротко и по делу. Не выдумывай цены — если спрашивают точную стоимость, предложи связаться с менеджером (@Foxsiiiii).

Вот услуги Aicore:

1. AI-БОТ
Умный помощник, который работает 24/7.
Что входит: бот на любой платформе (Telegram, Instagram, Facebook, сайт), AI-консультант обученный под бизнес и бренд клиента, автоматический сбор контактов в Google Sheets или другие программы, поддержка любого языка.
Можно добавить: онлайн-запись и бронирование, автоматические напоминания клиентам, генерация изображений в боте, реакция на комментарии и сторис, интеграция с CRM, воронка продаж, поддержка и обновления после запуска.

2. АВТОМАТИЗАЦИЯ
Убираем рутину — бизнес работает сам.
Что входит: аудит процессов (находим где теряется время и деньги), автоматизация одного ключевого процесса (например: заявка → уведомление → таблица → ответ клиенту).
Можно добавить: автоматизация дополнительных процессов, интеграция между платформами и сервисами, авто-отчёты и аналитика, автоматическое выставление счетов, интеграция с CRM, поддержка после запуска.

3. ТАРГЕТИРОВАННАЯ РЕКЛАМА
Реклама, которая приводит реальных клиентов. Рекламный бюджет оплачивается отдельно.
Что входит: настройка рекламного кабинета с нуля, ведение рекламы на платформах Meta, Google и TikTok, креативы (баннеры и тексты), настройка аудиторий и таргетинга, постоянная оптимизация кампаний.
Можно добавить: AI-генерация рекламных материалов, A/B тестирование, ретаргетинг, landing page под кампанию, управление рекламным бюджетом.

Если клиент готов заказать — направь его к менеджеру: @Foxsiiiii
Отвечай только на вопросы об услугах Aicore. Если спрашивают о чём-то постороннем — вежливо верни к теме."""

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# Состояния для ConversationHandler
DEMO_CHAT = 1


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
        "👋 Добро пожаловать в Aicore!\n\n"
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
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("📩 Связаться", url="https://t.me/Foxsiiiii")],
            [InlineKeyboardButton("📝 Заполнить форму", callback_data="order_form")],
        ])

        await update.message.reply_text(
            "🛍️ *ЗАКАЗАТЬ УСЛУГИ*\n\n"
            "Выберите удобный способ 👇",
            parse_mode="MarkdownV2",
            reply_markup=keyboard,
        )

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
        if not OPENROUTER_API_KEY:
            await update.message.reply_text(
                "⚠️ AI-консультант временно недоступен.",
                reply_markup=main_menu(),
            )
            return None

        context.user_data["demo_history"] = []

        demo_kb = ReplyKeyboardMarkup(
            [["❌ Завершить демо"]],
            resize_keyboard=True,
        )
        await update.message.reply_text(
            "🤖 *ДЕМО AI\-КОНСУЛЬТАНТА*\n\n"
            "Сейчас вы общаетесь с AI\-помощником Aicore\.\n"
            "Он знает всё о наших услугах и поможет\n"
            "подобрать решение под ваш бизнес\.\n\n"
            "Спросите что угодно, например:\n"
            "▸ _«Мне нужен бот для Instagram»_\n"
            "▸ _«Как автоматизировать заявки?»_\n"
            "▸ _«Какая реклама мне подойдёт?»_\n\n"
            "Напишите ваш вопрос 👇",
            parse_mode="MarkdownV2",
            reply_markup=demo_kb,
        )
        return DEMO_CHAT

    # 💡 ЧЕМ МЫ ПОЛЕЗНЫ
    elif text == "💡 Чем мы полезны":
        await update.message.reply_text(
            "💡 *ЧЕМ МЫ ПОЛЕЗНЫ*\n\n"
            "Знакомо?\n\n"
            "━━━━━━━━━━━━━━━━━━━━━\n\n"
            "😩 *Клиент написал ночью — а ты спишь*\n"
            "Пока ты отдыхаешь, конкурент уже ответил\.\n"
            "▸ Наш AI\-бот отвечает за *2 секунды*\n"
            "  — днём и ночью, без выходных\n\n"
            "😩 *Часы уходят на рутину*\n"
            "Заявки, таблицы, напоминания, счета\.\.\.\n"
            "▸ Автоматизация экономит *15\+ часов*\n"
            "  *в неделю* — ты занимаешься бизнесом,\n"
            "  а не копипастом\n\n"
            "😩 *Реклама крутится — клиентов нет*\n"
            "Бюджет сливается, а заявок ноль\.\n"
            "▸ Настраиваем таргет так, чтобы\n"
            "  каждый евро приносил *реальных клиентов*\n\n"
            "━━━━━━━━━━━━━━━━━━━━━\n\n"
            "📊 *Несколько цифр:*\n\n"
            "▸ *70%* клиентов уходят, если не получили\n"
            "  ответ в первые 5 минут\n"
            "▸ Бизнесы с автоматизацией растут\n"
            "  *в 2 раза быстрее* конкурентов\n"
            "▸ AI\-бот заменяет *3\-5 менеджеров*\n"
            "  и не просит зарплату\n\n"
            "━━━━━━━━━━━━━━━━━━━━━\n\n"
            "🚀 *Мы делаем так, чтобы твой бизнес*\n"
            "*работал быстрее, умнее и без лишних рук\.*",
            parse_mode="MarkdownV2",
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

    elif data == "order_form":
        await query.message.edit_text(
            "📝 *ФОРМА ЗАЯВКИ*\n\n"
            "Скоро здесь будет ссылка на форму\.\n"
            "Пока можете написать нам напрямую 👇",
            parse_mode="MarkdownV2",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📩 Связаться", url="https://t.me/Foxsiiiii")],
            ]),
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
#  ДЕМО AI-КОНСУЛЬТАНТ
# ─────────────────────────────────────────
async def handle_demo_chat(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обработка сообщений в режиме демо AI-чата."""
    text = update.message.text

    # Выход из демо
    if text == "❌ Завершить демо":
        context.user_data.pop("demo_history", None)
        await update.message.reply_text(
            "👋 Демо завершено!\n\n"
            "Понравилось? Такого AI-консультанта мы можем\n"
            "сделать и для вашего бизнеса.",
            reply_markup=main_menu(),
        )
        return ConversationHandler.END

    # Собираем историю
    history = context.user_data.get("demo_history", [])
    history.append({"role": "user", "content": text})

    # Отправляем "печатает..."
    await update.message.chat.send_action("typing")

    try:
        response = await ai_client.chat.completions.create(
            model=AI_MODEL,
            messages=[{"role": "system", "content": SYSTEM_PROMPT}] + history,
            max_tokens=500,
        )
        reply = response.choices[0].message.content
        history.append({"role": "assistant", "content": reply})

        # Ограничиваем историю последними 20 сообщениями
        if len(history) > 20:
            history = history[-20:]
        context.user_data["demo_history"] = history

        await update.message.reply_text(reply)

    except Exception as e:
        logger.error(f"OpenRouter ошибка: {e}")
        await update.message.reply_text(
            "⚠️ Не удалось получить ответ. Попробуйте ещё раз."
        )

    return DEMO_CHAT


# ─────────────────────────────────────────
#  ЗАПУСК
# ─────────────────────────────────────────
def main() -> None:
    logger.info("=" * 50)
    logger.info("🚀 Aicore Bot стартует...")

    app = Application.builder().token(TOKEN).build()

    # ConversationHandler для меню, формы и демо
    conv_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.TEXT & ~filters.COMMAND, handle_buttons)],
        states={
            DEMO_CHAT: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_demo_chat)],
        },
        fallbacks=[
            CommandHandler("start", start),
            CommandHandler("menu", menu_command),
        ],
    )

    # Обработчики
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("menu", menu_command))
    app.add_handler(CallbackQueryHandler(handle_service_callback))
    app.add_handler(conv_handler)

    logger.info("✅ Бот готов!")
    logger.info("=" * 50)

    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
