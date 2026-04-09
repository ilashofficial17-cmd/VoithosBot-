import logging
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler

from config import OPENROUTER_API_KEY, ai_client, AI_MODEL, SYSTEM_PROMPT, DEMO_MESSAGE_LIMIT
from locales import detect_lang, t

logger = logging.getLogger(__name__)

DEMO_CHAT = 1


# ─────────────────────────────────────────
#  КЛАВИАТУРЫ
# ─────────────────────────────────────────
def main_menu(context) -> ReplyKeyboardMarkup:
    keyboard = [
        [t(context, "btn_order"), t(context, "btn_services")],
        [t(context, "btn_demo"), t(context, "btn_useful")],
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def back_menu(context) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup([[t(context, "btn_back")]], resize_keyboard=True)


def lang_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Русский", callback_data="lang_ru")],
        [InlineKeyboardButton("English", callback_data="lang_en")],
        [InlineKeyboardButton("Deutsch", callback_data="lang_de")],
    ])


def services_keyboard(context) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(t(context, "btn_aibot"), callback_data="service_aibot")],
        [InlineKeyboardButton(t(context, "btn_auto"), callback_data="service_auto")],
        [InlineKeyboardButton(t(context, "btn_ads"), callback_data="service_ads")],
    ])


def _ensure_lang(update, context):
    if "lang" not in context.user_data:
        context.user_data["lang"] = detect_lang(update.effective_user)


# ─────────────────────────────────────────
#  /START & /MENU
# ─────────────────────────────────────────
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.info(f"👤 /start от {update.effective_user.first_name}")
    context.user_data["lang"] = detect_lang(update.effective_user)

    await update.message.reply_text(
        t(context, "welcome"),
        reply_markup=main_menu(context),
    )
    await update.message.reply_text(
        "🌐 Change language / Сменить язык:",
        reply_markup=lang_keyboard(),
    )


async def menu_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.info(f"📋 /menu от {update.effective_user.first_name}")
    _ensure_lang(update, context)

    await update.message.reply_text(
        t(context, "choose_option"),
        reply_markup=main_menu(context),
    )


# ─────────────────────────────────────────
#  ОБРАБОТКА КНОПОК МЕНЮ
# ─────────────────────────────────────────
async def handle_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = update.message.text
    _ensure_lang(update, context)
    logger.info(f"📨 {text} от {update.effective_user.first_name}")

    if text == t(context, "btn_back"):
        await update.message.reply_text(
            t(context, "choose_option"),
            reply_markup=main_menu(context),
        )

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

    elif text == t(context, "btn_services"):
        await update.message.reply_text(
            t(context, "services_intro"),
            parse_mode="MarkdownV2",
            reply_markup=services_keyboard(context),
        )

    elif text == t(context, "btn_demo"):
        if not OPENROUTER_API_KEY:
            await update.message.reply_text(
                t(context, "demo_unavailable"),
                reply_markup=main_menu(context),
            )
            return None

        context.user_data["demo_history"] = []
        context.user_data["demo_count"] = 0

        demo_kb = ReplyKeyboardMarkup(
            [[t(context, "btn_end_demo")]],
            resize_keyboard=True,
        )
        await update.message.reply_text(
            t(context, "demo_intro"),
            parse_mode="MarkdownV2",
            reply_markup=demo_kb,
        )
        # AI начинает первым
        first_msg = t(context, "demo_first_msg")
        context.user_data["demo_history"].append(
            {"role": "assistant", "content": first_msg}
        )
        await update.message.reply_text(first_msg)
        return DEMO_CHAT

    elif text == t(context, "btn_useful"):
        await update.message.reply_text(
            t(context, "useful"),
            parse_mode="MarkdownV2",
            reply_markup=back_menu(context),
        )

    else:
        await update.message.reply_text(
            t(context, "use_buttons"),
            reply_markup=main_menu(context),
        )


# ─────────────────────────────────────────
#  ИНЛАЙН-КНОПКИ (услуги, язык, форма)
# ─────────────────────────────────────────
SERVICE_KEYS = {"service_aibot", "service_auto", "service_ads"}


async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    data = query.data

    if "lang" not in context.user_data:
        context.user_data["lang"] = "ru"

    # ВЫБОР ЯЗЫКА
    if data.startswith("lang_"):
        context.user_data["lang"] = data[5:]
        await query.message.delete()
        await query.message.chat.send_message(
            t(context, "welcome"),
            reply_markup=main_menu(context),
        )
        return

    # УСЛУГИ — с кнопкой "Заказать"
    if data in SERVICE_KEYS:
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton(t(context, "btn_order_service"), callback_data="order_from_service")],
            [InlineKeyboardButton(t(context, "btn_back_services"), callback_data="back_to_services")],
        ])
        await query.message.edit_text(
            t(context, data),
            parse_mode="MarkdownV2",
            reply_markup=kb,
        )

    elif data in ("order_form", "order_from_service"):
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
    text = update.message.text

    # Выход
    if text == t(context, "btn_end_demo"):
        context.user_data.pop("demo_history", None)
        context.user_data.pop("demo_count", None)
        await update.message.reply_text(
            t(context, "demo_end"),
            reply_markup=main_menu(context),
        )
        return ConversationHandler.END

    # Лимит сообщений
    count = context.user_data.get("demo_count", 0) + 1
    context.user_data["demo_count"] = count

    if count > DEMO_MESSAGE_LIMIT:
        context.user_data.pop("demo_history", None)
        context.user_data.pop("demo_count", None)
        await update.message.reply_text(
            t(context, "demo_limit"),
            reply_markup=main_menu(context),
        )
        return ConversationHandler.END

    # Собираем историю
    history = context.user_data.get("demo_history", [])
    history.append({"role": "user", "content": text})

    await update.message.chat.send_action("typing")

    try:
        response = await ai_client.chat.completions.create(
            model=AI_MODEL,
            messages=[{"role": "system", "content": SYSTEM_PROMPT}] + history,
            max_tokens=500,
        )
        reply = response.choices[0].message.content
        history.append({"role": "assistant", "content": reply})

        if len(history) > 20:
            history = history[-20:]
        context.user_data["demo_history"] = history

        await update.message.reply_text(reply)

    except Exception as e:
        logger.error(f"OpenRouter ошибка: {e}")
        await update.message.reply_text(t(context, "demo_error"))

    return DEMO_CHAT
