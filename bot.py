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

from locales import detect_lang, t, TEXTS

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

SYSTEM_PROMPT = """\
Ты — Aicore, живой консультант в Telegram. Ты не бот, ты — человек из команды, который реально шарит в AI, автоматизации и рекламе.

## Твой характер
- Ты общаешься как реальный чувак в чате. Без пафоса, без корпоративного булшита.
- Пишешь коротко. Одно-два предложения. Иногда три, если тема сложная.
- Ты можешь пошутить, если к месту. Но не клоун — ты эксперт.
- Говоришь «сделаем», «разберёмся», «погнали» — не «Мы предоставляем комплексные решения».
- Если чего-то не знаешь — честно скажи и предложи связаться с менеджером.
- Эмодзи — максимум 1 на сообщение, и то не всегда.

## Как ведёшь диалог
- Первым делом спроси: чем занимается человек и что у него болит. Не грузи услугами сразу.
- Один вопрос за раз. Не допрос.
- Когда понял проблему — объясни как конкретно ЕМУ это поможет. Не абстрактно.
- Можешь привести пример: «У нас один салон красоты поставил бота — за неделю 50 записей без менеджера».
- Не читай лекции. Клиент спросил — ответь чётко.

## Услуги Aicore

AI-БОТ: Бот для бизнеса 24/7. Telegram, Instagram, Facebook, сайт. Обучаем под бренд, собирает контакты, консультирует клиентов сам. Допы: запись, напоминания, генерация картинок, CRM, воронка, реакция на сторис.

АВТОМАТИЗАЦИЯ: Находим где в бизнесе теряется время, и убираем ручную работу. Заявка пришла → менеджер узнал → данные в таблице → клиент получил ответ. Автопилот. Допы: доп. процессы, интеграции, отчёты, счета, CRM.

ТАРГЕТ: Реклама в Meta, Google, TikTok. Креативы, аудитории, оптимизация. Бюджет отдельно. Допы: AI-креативы, A/B тесты, ретаргетинг, лендинг.

## Правила
- Цены не называй. Скажи «зависит от задачи, давай обсудим с менеджером — @Foxsiiiii».
- Когда клиент готов — «Напиши @Foxsiiiii, он подберёт под тебя».
- Не по теме — мягко верни. Без нравоучений.
- Ты демо-версия. Если спросят — скажи что такого же бота можем сделать для его бизнеса.
- ВСЕГДА отвечай на языке клиента. Пишет на английском — отвечай на английском. На немецком — на немецком."""

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
def main_menu(context) -> ReplyKeyboardMarkup:
    """Главное меню с 4 кнопками."""
    keyboard = [
        [t(context, "btn_order"), t(context, "btn_services")],
        [t(context, "btn_demo"), t(context, "btn_useful")],
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def back_menu(context) -> ReplyKeyboardMarkup:
    """Кнопка назад в меню."""
    keyboard = [[t(context, "btn_back")]]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def lang_keyboard() -> InlineKeyboardMarkup:
    """Кнопки выбора языка."""
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru"),
            InlineKeyboardButton("🇬🇧 English", callback_data="lang_en"),
            InlineKeyboardButton("🇩🇪 Deutsch", callback_data="lang_de"),
        ],
    ])


# ─────────────────────────────────────────
#  /START
# ─────────────────────────────────────────
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Приветствие с автодетектом языка и выбором."""
    logger.info(f"👤 /start от {update.effective_user.first_name}")

    # Автодетект языка из Telegram
    lang = detect_lang(update.effective_user)
    context.user_data["lang"] = lang

    await update.message.reply_text(
        t(context, "welcome"),
        reply_markup=main_menu(context),
    )
    await update.message.reply_text(
        "🌐 Change language / Сменить язык:",
        reply_markup=lang_keyboard(),
    )


# ─────────────────────────────────────────
#  /MENU
# ─────────────────────────────────────────
async def menu_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Вернуться в главное меню."""
    logger.info(f"📋 /menu от {update.effective_user.first_name}")

    if "lang" not in context.user_data:
        context.user_data["lang"] = detect_lang(update.effective_user)

    await update.message.reply_text(
        t(context, "choose_option"),
        reply_markup=main_menu(context),
    )


# ─────────────────────────────────────────
#  ОБРАБОТКА КНОПОК
# ─────────────────────────────────────────
async def handle_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработка всех кнопок меню."""
    text = update.message.text

    if "lang" not in context.user_data:
        context.user_data["lang"] = detect_lang(update.effective_user)

    logger.info(f"📨 {text} от {update.effective_user.first_name}")

    # НАЗАД В МЕНЮ
    if text == t(context, "btn_back"):
        await update.message.reply_text(
            t(context, "choose_option"),
            reply_markup=main_menu(context),
        )

    # 🛍️ ЗАКАЗАТЬ УСЛУГИ
    elif text == t(context, "btn_order"):
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(t(context, "btn_contact"), url="https://t.me/Foxsiiiii")],
            [InlineKeyboardButton(t(context, "btn_form"), callback_data="order_form")],
        ])
        await update.message.reply_text(
            t(context, "order_title"),
            parse_mode="MarkdownV2",
            reply_markup=keyboard,
        )

    # 📋 ВИДЫ УСЛУГ
    elif text == t(context, "btn_services"):
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(t(context, "btn_aibot"), callback_data="service_aibot")],
            [InlineKeyboardButton(t(context, "btn_auto"), callback_data="service_auto")],
            [InlineKeyboardButton(t(context, "btn_ads"), callback_data="service_ads")],
        ])
        await update.message.reply_text(
            t(context, "services_intro"),
            parse_mode="MarkdownV2",
            reply_markup=keyboard,
        )

    # 🤖 ДЕМОНСТРАЦИЯ
    elif text == t(context, "btn_demo"):
        if not OPENROUTER_API_KEY:
            await update.message.reply_text(
                t(context, "demo_unavailable"),
                reply_markup=main_menu(context),
            )
            return None

        context.user_data["demo_history"] = []
        demo_kb = ReplyKeyboardMarkup(
            [[t(context, "btn_end_demo")]],
            resize_keyboard=True,
        )
        await update.message.reply_text(
            t(context, "demo_intro"),
            parse_mode="MarkdownV2",
            reply_markup=demo_kb,
        )
        return DEMO_CHAT

    # 💡 ЧЕМ МЫ ПОЛЕЗНЫ
    elif text == t(context, "btn_useful"):
        await update.message.reply_text(
            t(context, "useful"),
            parse_mode="MarkdownV2",
            reply_markup=back_menu(context),
        )

    # НЕИЗВЕСТНОЕ СООБЩЕНИЕ
    else:
        await update.message.reply_text(
            t(context, "use_buttons"),
            reply_markup=main_menu(context),
        )


# ─────────────────────────────────────────
#  ИНЛАЙН-КНОПКИ УСЛУГ
# ─────────────────────────────────────────
def services_keyboard(context) -> InlineKeyboardMarkup:
    """Клавиатура выбора услуг."""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(t(context, "btn_aibot"), callback_data="service_aibot")],
        [InlineKeyboardButton(t(context, "btn_auto"), callback_data="service_auto")],
        [InlineKeyboardButton(t(context, "btn_ads"), callback_data="service_ads")],
    ])


SERVICE_KEYS = {"service_aibot", "service_auto", "service_ads"}


async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработка всех инлайн-кнопок."""
    query = update.callback_query
    await query.answer()
    data = query.data

    if "lang" not in context.user_data:
        context.user_data["lang"] = "ru"

    # ВЫБОР ЯЗЫКА
    if data.startswith("lang_"):
        lang = data[5:]  # "lang_ru" -> "ru"
        context.user_data["lang"] = lang
        await query.message.delete()
        await query.message.chat.send_message(
            t(context, "welcome"),
            reply_markup=main_menu(context),
        )
        return

    # УСЛУГИ
    if data in SERVICE_KEYS:
        back_kb = InlineKeyboardMarkup([
            [InlineKeyboardButton(t(context, "btn_back_services"), callback_data="back_to_services")],
        ])
        await query.message.edit_text(
            t(context, data),
            parse_mode="MarkdownV2",
            reply_markup=back_kb,
        )

    elif data == "order_form":
        await query.message.edit_text(
            t(context, "order_form"),
            parse_mode="MarkdownV2",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(t(context, "btn_contact"), url="https://t.me/Foxsiiiii")],
            ]),
        )

    elif data == "back_to_services":
        await query.message.edit_text(
            t(context, "services_intro"),
            parse_mode="MarkdownV2",
            reply_markup=services_keyboard(context),
        )


# ─────────────────────────────────────────
#  ДЕМО AI-КОНСУЛЬТАНТ
# ─────────────────────────────────────────
async def handle_demo_chat(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обработка сообщений в режиме демо AI-чата."""
    text = update.message.text

    # Выход из демо
    if text == t(context, "btn_end_demo"):
        context.user_data.pop("demo_history", None)
        await update.message.reply_text(
            t(context, "demo_end"),
            reply_markup=main_menu(context),
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
        await update.message.reply_text(t(context, "demo_error"))

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
    app.add_handler(CallbackQueryHandler(handle_callback))
    app.add_handler(conv_handler)

    logger.info("✅ Бот готов!")
    logger.info("=" * 50)

    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
