import re
import logging
import aiohttp
from dataclasses import dataclass
from typing import Dict, List, Optional

from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.constants import ChatAction
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
    PicklePersistence,
)

# ======== КОНФИГ ========

TELEGRAM_BOT_TOKEN = "................."
LM_STUDIO_URL = "........................."
MODEL_NAME = "............."

SYSTEM_PROMPT = (
    "Ты — дружелюбный ассистент, называющий себя CassielGPT. "
    "Отвечай коротко и понятно на русском языке. "
    "Не включай в ответ служебные или англоязычные инструкции."
)

DEFAULT_TEMPERATURE = 0.7
DEFAULT_MAX_TOKENS = 1024

# «Память»
MAX_MESSAGES_PER_CHAT = 200
MAX_CONTEXT_CHARS = 24_000

# Telegram лимиты
TG_TEXT_LIMIT = 4096

# Ограничим длину списков id сообщений
MAX_TRACKED_MSG_IDS = 700

# Тексты кнопок
BTN_NEW_CHAT   = "Начать новый чат"
BTN_LIST_CHATS = "История чатов"
BTN_DONATE     = "Пожертвовать автору"
BTN_BACK       = "Назад"

# Текст пожертвований
DONATE_MESSAGE = (
    "🙏 *Пожертвование автору*\n\n"
    "Спасибо, что хотите поддержать разработку *CassielGPT*! "
    "Это помогает оплачивать сервера, тестировать модели и выпускать обновления. "
    "Любая сумма важна. 💚\n\n"
    "Способы:\n"
    "💳 *Сбербанк (карта):* `2202 2081 0136 6822`\n"
    "📝 Комментарий к переводу: _на бота 🤖_\n\n"
    "Если отправили — напишите «поддержал», я скажу спасибо. ☕🚀"
)

logging.basicConfig(
    format="%(asctime)s — %(name)s — %(levelname)s — %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


# ======== ДАННЫЕ СЕССИЙ ========

@dataclass
class ChatSession:
    name: str
    history: List[Dict]
    bot_message_ids: List[int]
    user_message_ids: List[int]

# user_data:
# {
#   'temperature': float,
#   'max_tokens': int,
#   'chats': {'chat_1': {...}}, 'active_chat': 'chat_1', 'next_index': int
# }


# ======== ТЕКСТ-УТИЛЫ ========

def strip_english_preface(text: str) -> str:
    m = re.search(r"[А-ЯЁа-яё]", text)
    return text[m.start():] if m else text

def filter_russian_sentences(text: str) -> str:
    parts = re.split(r'(?<=[.!?])\s*', text)
    rus = [p for p in parts if re.match(r'^\s*[А-ЯЁ]', p.strip())]
    return " ".join(rus).strip() if rus else text.strip()

def chunk_plain_text(s: str, limit: int = TG_TEXT_LIMIT) -> List[str]:
    if len(s) <= limit:
        return [s]
    chunks = []
    i = 0
    while i < len(s):
        end = min(i + limit, len(s))
        cut = s.rfind("\n", i, end)
        if cut == -1:
            cut = s.rfind(" ", i, end)
        if cut == -1 or cut <= i + limit // 2:
            cut = end
        chunks.append(s[i:cut].rstrip())
        i = cut
    return chunks


# ======== UI-КЛАВЫ ========

def main_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        [
            [KeyboardButton(BTN_NEW_CHAT), KeyboardButton(BTN_LIST_CHATS)],
            [KeyboardButton(BTN_DONATE)],
        ],
        resize_keyboard=True
    )

def chats_keyboard(chats: Dict[str, dict]) -> ReplyKeyboardMarkup:
    names = [c['name'] for c in chats.values()]
    rows, row = [], []
    for i, name in enumerate(names, 1):
        row.append(KeyboardButton(name))
        if i % 2 == 0:
            rows.append(row); row = []
    if row:
        rows.append(row)
    rows.append([KeyboardButton(BTN_BACK)])
    return ReplyKeyboardMarkup(rows, resize_keyboard=True)


# ======== СЕССИИ ========

def _limit_ids(lst: List[int]) -> None:
    if len(lst) > MAX_TRACKED_MSG_IDS:
        del lst[:-MAX_TRACKED_MSG_IDS]

def ensure_user_state(context: ContextTypes.DEFAULT_TYPE) -> None:
    ud = context.user_data
    ud.setdefault("temperature", DEFAULT_TEMPERATURE)
    ud.setdefault("max_tokens", DEFAULT_MAX_TOKENS)
    if "chats" not in ud:
        ud["chats"] = {}
        ud["next_index"] = 1
        chat_id = f"chat_{ud['next_index']}"
        ud["next_index"] += 1
        ud["chats"][chat_id] = {
            "name": "чат 1",
            "history": [{"role": "system", "content": SYSTEM_PROMPT}],
            "bot_message_ids": [],
            "user_message_ids": [],
        }
        ud["active_chat"] = chat_id

def get_active_chat_id(context: ContextTypes.DEFAULT_TYPE) -> str:
    ensure_user_state(context)
    return context.user_data["active_chat"]

def get_active_chat(context: ContextTypes.DEFAULT_TYPE) -> dict:
    return context.user_data["chats"][get_active_chat_id(context)]

def create_new_chat(context: ContextTypes.DEFAULT_TYPE) -> dict:
    ensure_user_state(context)
    idx = context.user_data["next_index"]
    chat_id = f"chat_{idx}"
    context.user_data["next_index"] = idx + 1
    name = f"чат {idx}"
    context.user_data["chats"][chat_id] = {
        "name": name,
        "history": [{"role": "system", "content": SYSTEM_PROMPT}],
        "bot_message_ids": [],
        "user_message_ids": [],
    }
    context.user_data["active_chat"] = chat_id
    return context.user_data["chats"][chat_id]

def set_active_chat_by_name(context: ContextTypes.DEFAULT_TYPE, name: str) -> bool:
    ensure_user_state(context)
    for cid, chat in context.user_data["chats"].items():
        if chat["name"].strip().lower() == name.strip().lower():
            context.user_data["active_chat"] = cid
            return True
    return False

def trim_history_for_budget(history: List[Dict]) -> List[Dict]:
    if not history:
        return history
    sys = history[0] if history[0].get("role") == "system" else None
    rest = history[1:] if sys else history[:]
    if len(rest) > MAX_MESSAGES_PER_CHAT:
        rest = rest[-MAX_MESSAGES_PER_CHAT:]

    def total_chars(parts: List[Dict]) -> int:
        return sum(len(m.get("content", "")) for m in parts)

    trimmed = ([sys] if sys else []) + rest
    while total_chars(trimmed) > MAX_CONTEXT_CHARS and len(rest) > 2:
        rest = rest[2:] if len(rest) >= 2 else rest[1:]
        trimmed = ([sys] if sys else []) + rest
    return trimmed


# ======== ОПЕРАЦИИ С СООБЩЕНИЯМИ ========

async def send_long_text(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    text: str,
    reply_markup=None,
    track_session: Optional[dict] = None,
):
    chat_id = update.effective_chat.id
    chunks = chunk_plain_text(text, TG_TEXT_LIMIT)
    sent_ids: List[int] = []
    # Включим parse_mode Markdown для красивого донат-сообщения (и других)
    for idx, part in enumerate(chunks):
        if idx == 0:
            msg = await update.message.reply_text(part, reply_markup=reply_markup, parse_mode="Markdown")
        else:
            msg = await context.bot.send_message(chat_id=chat_id, text=part, parse_mode="Markdown")
        sent_ids.append(msg.message_id)
    if track_session is not None:
        track_session["bot_message_ids"].extend(sent_ids)
        _limit_ids(track_session["bot_message_ids"])

def track_user_message(update: Update, session: dict) -> None:
    if update.message:
        session["user_message_ids"].append(update.message.message_id)
        _limit_ids(session["user_message_ids"])

async def delete_session_messages(
    context: ContextTypes.DEFAULT_TYPE,
    chat_id: int,
    session: dict
):
    """Удаляем сообщения бота и пользователя этой сессии.
       В личке Telegram удалятся только сообщения бота (ограничение платформы)."""
    bot_ids = session.get("bot_message_ids", [])
    user_ids = session.get("user_message_ids", [])

    keep_bot: List[int] = []
    keep_user: List[int] = []

    for mid in bot_ids:
        try:
            await context.bot.delete_message(chat_id=chat_id, message_id=mid)
        except Exception:
            keep_bot.append(mid)

    for mid in user_ids:
        try:
            await context.bot.delete_message(chat_id=chat_id, message_id=mid)
        except Exception:
            keep_user.append(mid)

    session["bot_message_ids"] = keep_bot
    session["user_message_ids"] = keep_user

def render_session_snippet(session: dict, max_chars: int = 3500) -> str:
    msgs = session["history"]
    if not msgs:
        return "История пуста."
    tail = msgs[-12:]
    lines = []
    for m in tail:
        role = m.get("role")
        if role == "system":
            continue
        prefix = "👤" if role == "user" else "🤖"
        content = m.get("content", "").strip()
        content = re.sub(r"\n{3,}", "\n\n", content)
        lines.append(f"{prefix} {content}")
    text = "\n\n".join(lines).strip()
    if len(text) > max_chars:
        text = text[-max_chars:]
        text = "…(пропущено)\n" + text
    return text or "История пуста."


# ======== ХЕНДЛЕРЫ ========

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ensure_user_state(context)
    session = get_active_chat(context)
    track_user_message(update, session)
    await send_long_text(
        update, context,
        "Привет! Я CassielGPT на базе LM Studio.\n"
        "Кнопками ниже можно начинать новый чат и переключаться между чатами.\n\n"
        "Команды:\n"
        "/renamechat <новое имя> — переименовать текущий чат\n"
        "/deletechat yes — удалить текущий чат\n"
        "/donate — реквизиты для поддержки автора 🙏",
        reply_markup=main_keyboard(),
        track_session=session
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    session = get_active_chat(context)
    track_user_message(update, session)
    await send_long_text(
        update, context,
        "/start — показать меню\n"
        "/reset — очистить текущий чат\n"
        "/settemp <0.0–1.0> — температура\n"
        "/setmax <1–2048> — max_tokens\n"
        "/renamechat <новое имя> — переименовать текущий чат\n"
        "/deletechat yes — удалить текущий чат\n"
        "/donate — реквизиты для поддержки автора 🙏\n\n"
        f"Кнопки: {BTN_NEW_CHAT} / {BTN_LIST_CHATS} / {BTN_DONATE}.",
        reply_markup=main_keyboard(),
        track_session=session
    )

async def donate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    session = get_active_chat(context)
    track_user_message(update, session)
    await send_long_text(update, context, DONATE_MESSAGE, reply_markup=main_keyboard(), track_session=session)

async def set_temperature(update: Update, context: ContextTypes.DEFAULT_TYPE):
    session = get_active_chat(context)
    track_user_message(update, session)
    if len(context.args) != 1:
        return await send_long_text(update, context, "Использование: /settemp <0.0–1.0>", track_session=session)
    try:
        t = float(context.args[0])
        if not 0.0 <= t <= 1.0:
            raise ValueError
    except ValueError:
        return await send_long_text(update, context, "Введите число от 0.0 до 1.0.", track_session=session)
    context.user_data["temperature"] = t
    await send_long_text(update, context, f"Температура установлена: {t}", reply_markup=main_keyboard(), track_session=session)

async def set_max_tokens(update: Update, context: ContextTypes.DEFAULT_TYPE):
    session = get_active_chat(context)
    track_user_message(update, session)
    if len(context.args) != 1:
        return await send_long_text(update, context, "Использование: /setmax <1–2048>", track_session=session)
    try:
        m = int(context.args[0])
        if not 1 <= m <= 2048:
            raise ValueError
    except ValueError:
        return await send_long_text(update, context, "Введите целое от 1 до 2048.", track_session=session)
    context.user_data["max_tokens"] = m
    await send_long_text(update, context, f"max_tokens установлено: {m}", reply_markup=main_keyboard(), track_session=session)

async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ensure_user_state(context)
    chat_id = update.effective_chat.id
    session = get_active_chat(context)
    track_user_message(update, session)
    await delete_session_messages(context, chat_id, session)
    session["history"] = [{"role": "system", "content": SYSTEM_PROMPT}]
    await send_long_text(update, context, "Текущий чат очищен!", reply_markup=main_keyboard(), track_session=session)

async def show_chats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ensure_user_state(context)
    session = get_active_chat(context)
    track_user_message(update, session)
    chats = context.user_data["chats"]
    names = [c['name'] for c in chats.values()]
    msg = "Выбери чат:\n" + ("\n".join(f"• {n}" for n in names) if names else "Пока нет чатов.")
    await send_long_text(update, context, msg, reply_markup=chats_keyboard(chats), track_session=session)

async def rename_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ensure_user_state(context)
    session = get_active_chat(context)
    track_user_message(update, session)
    if not context.args:
        return await send_long_text(update, context, "Использование: /renamechat <новое имя>", track_session=session)

    new_name = " ".join(context.args).strip()
    if not new_name:
        return await send_long_text(update, context, "Имя не должно быть пустым.", track_session=session)
    for c in context.user_data["chats"].values():
        if c is not session and c["name"].strip().lower() == new_name.lower():
            return await send_long_text(update, context, "Такое имя уже используется.", track_session=session)

    old_name = session["name"]
    session["name"] = new_name[:64]
    await send_long_text(update, context, f"Чат «{old_name}» переименован в «{session['name']}».", reply_markup=main_keyboard(), track_session=session)

async def delete_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ensure_user_state(context)
    ud = context.user_data
    chat_id_tg = update.effective_chat.id
    active_id = get_active_chat_id(context)
    session = ud["chats"][active_id]
    track_user_message(update, session)

    if not context.args or context.args[0].lower() != "yes":
        return await send_long_text(
            update, context,
            "Подтверждение: чтобы удалить текущий чат, отправь: /deletechat yes",
            track_session=session
        )

    await delete_session_messages(context, chat_id_tg, session)
    del ud["chats"][active_id]

    if not ud["chats"]:
        create_new_chat(context)
    else:
        new_active = next(iter(ud["chats"].keys()))
        ud["active_chat"] = new_active

    new_session = get_active_chat(context)
    await send_long_text(
        update, context,
        f"Чат удалён. Активен «{new_session['name']}».",
        reply_markup=main_keyboard(),
        track_session=new_session
    )
    snippet = render_session_snippet(new_session)
    if snippet:
        await send_long_text(update, context, f"Последние сообщения:\n\n{snippet}", track_session=new_session)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    txt = update.message.text.strip()
    ensure_user_state(context)
    chat_id_tg = update.effective_chat.id

    current_session = get_active_chat(context)
    track_user_message(update, current_session)

    # кнопки
    if txt == BTN_NEW_CHAT:
        session = create_new_chat(context)
        await send_long_text(update, context, f"Создан {session['name']}. Начинай писать 👇", reply_markup=main_keyboard(), track_session=session)
        return

    if txt == BTN_LIST_CHATS:
        return await show_chats(update, context)

    if txt == BTN_DONATE:
        return await donate(update, context)

    if txt == BTN_BACK:
        return await send_long_text(update, context, "Готово.", reply_markup=main_keyboard(), track_session=get_active_chat(context))

    # переключение по имени
    if set_active_chat_by_name(context, txt):
        await delete_session_messages(context, chat_id_tg, current_session)
        new_session = get_active_chat(context)
        await send_long_text(update, context, f"Переключился на «{new_session['name']}».", reply_markup=main_keyboard(), track_session=new_session)
        snippet = render_session_snippet(new_session)
        if snippet:
            await send_long_text(update, context, f"Последние сообщения:\n\n{snippet}", track_session=new_session)
        return

    # обычный текст — диалог с моделью
    user_text = txt
    session = get_active_chat(context)
    logger.info(f"Пользователь: {user_text}")

    session["history"].append({"role": "user", "content": user_text})
    trimmed = trim_history_for_budget(session["history"])

    await update.message.chat.send_action(ChatAction.TYPING)

    payload = {
        "model": MODEL_NAME,
        "messages": trimmed,
        "temperature": context.user_data["temperature"],
        "max_tokens": context.user_data["max_tokens"],
    }

    session_http: aiohttp.ClientSession = context.application.bot_data.get("lm_session")
    if session_http is None or session_http.closed:
        session_http = aiohttp.ClientSession()
        context.application.bot_data["lm_session"] = session_http

    try:
        async with session_http.post(LM_STUDIO_URL, json=payload, timeout=120) as resp:
            if resp.status != 200:
                text = await resp.text()
                logger.error("LM Studio вернул %s: %s", resp.status, text)
                return await send_long_text(update, context, f"Ошибка LM Studio: {resp.status}", reply_markup=main_keyboard(), track_session=session)

            data = await resp.json()

        choices = data.get("choices")
        if not choices:
            err = data.get("error", {}).get("message", "Неизвестная ошибка")
            return await send_long_text(update, context, f"Ошибка: {err}", reply_markup=main_keyboard(), track_session=session)

        raw = choices[0]["message"]["content"]
        reply = filter_russian_sentences(strip_english_preface(raw))

        logger.info(f"Бот: {reply}")
        session["history"].append({"role": "assistant", "content": reply})
        session["history"] = trim_history_for_budget(session["history"])

        await send_long_text(update, context, reply, reply_markup=main_keyboard(), track_session=session)

    except Exception:
        logger.exception("Ошибка при запросе к LM Studio")
        await send_long_text(update, context, "Упс! Что-то пошло не так. Попробуйте позже.", reply_markup=main_keyboard(), track_session=session)

async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    session = get_active_chat(context)
    track_user_message(update, session)
    await send_long_text(update, context, "Извини, я понимаю только текст.", reply_markup=main_keyboard(), track_session=session)


# ======== LIFECYCLE ========

async def on_shutdown(app):
    session_http: aiohttp.ClientSession = app.bot_data.get("lm_session")
    if session_http and not session_http.closed:
        await session_http.close()


# ======== ЗАПУСК ========

if __name__ == "__main__":
    persistence = PicklePersistence(filepath="bot_state.pickle")

    app = ApplicationBuilder() \
        .token(TELEGRAM_BOT_TOKEN) \
        .persistence(persistence) \
        .build()

    app.bot_data["lm_session"] = None
    app.post_shutdown = on_shutdown

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("donate", donate))
    app.add_handler(CommandHandler("settemp", set_temperature))
    app.add_handler(CommandHandler("setmax", set_max_tokens))
    app.add_handler(CommandHandler("reset", reset))
    app.add_handler(CommandHandler("renamechat", rename_chat))
    app.add_handler(CommandHandler("deletechat", delete_chat))

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(MessageHandler(~filters.TEXT, unknown))

    logger.info("Бот запущен и готов к работе!")
    app.run_polling()
