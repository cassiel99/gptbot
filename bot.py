from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
import requests

# ======== НАСТРОЙКИ ========

TELEGRAM_BOT_TOKEN = "///////"

LM_STUDIO_URL = "........."

SYSTEM_PROMPT = "Ты дружелюбный ассистент. Отвечай кратко и понятно."

MODEL_NAME = "local-model"  # LM Studio игнорирует название, но поле нужно

TEMPERATURE = 0.7
MAX_TOKENS = 1024


# ======== ОБРАБОТЧИКИ ========

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # при /start создаём новую историю диалога
    context.user_data["history"] = [
        {"role": "system", "content": SYSTEM_PROMPT}
    ]
    await update.message.reply_text(
        "Привет! Я бот, работающий на LM Studio.\nНапиши мне что-нибудь!"
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text

    # если истории нет — создаём новую
    if "history" not in context.user_data:
        context.user_data["history"] = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ]

    # добавляем пользовательское сообщение в историю
    context.user_data["history"].append(
        {"role": "user", "content": user_message}
    )

    # готовим payload для LM Studio
    payload = {
        "model": MODEL_NAME,
        "messages": context.user_data["history"],
        "temperature": TEMPERATURE,
        "max_tokens": MAX_TOKENS,
    }

    try:
        response = requests.post(
            LM_STUDIO_URL,
            json=payload,
            timeout=60
        )

        # проверим код ответа HTTP
        if response.status_code != 200:
            await update.message.reply_text(
                f"LM Studio вернул код {response.status_code}: {response.text}"
            )
            return

        data = response.json()

        # проверим наличие ключа 'choices'
        if "choices" not in data:
            error_message = data.get("error", {}).get("message", "Неизвестная ошибка")
            await update.message.reply_text(
                f"LM Studio вернул ошибку: {error_message}"
            )
            return

        assistant_reply = data["choices"][0]["message"]["content"]

        # добавляем ответ ассистента в историю
        context.user_data["history"].append(
            {"role": "assistant", "content": assistant_reply}
        )

        await update.message.reply_text(assistant_reply)

    except Exception as e:
        await update.message.reply_text("Ошибка при обращении к LM Studio:\n" + str(e))


async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["history"] = [
        {"role": "system", "content": SYSTEM_PROMPT}
    ]
    await update.message.reply_text("Контекст чата сброшен!")


# ======== ЗАПУСК БОТА ========

if __name__ == "__main__":
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("reset", reset))
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)
    )

    print("Бот запущен!")
    app.run_polling()
