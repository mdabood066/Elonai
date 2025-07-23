import os
import re 
from dotenv import load_dotenv
import httpx
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    MessageHandler,
    filters,
)

load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "*Welcome to @ElonAiCompanion_Bot,* "
        "*the first Elon AI Companion bot on chain!* "
        "*Ready to dive into $ELONAI?*",
        parse_mode="Markdown"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "*💡 Send a message, and I’ll reply like Elon.* "
        "*In groups, tag me like @ElonAiCompanion_Bot.*",
        parse_mode="Markdown"
    )

# Message handler
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message

    if not message or not message.text:
        return

    text = message.text.strip()

     # Check for 'contract address' query (case-insensitive)
    if "contract address" in text.lower():
        await message.reply_text(
            "📄 *Contract Address:*\n`Bd47c4MSiPZm73wNK8wTf1Nbpud5HduY9Kdp2GPFa9zn`",
            parse_mode="Markdown"
        )
        return 
    
    # Only respond in groups if tagged or replied to
    if message.chat.type in ["group", "supergroup"]:
        bot_username = f"@{context.bot.username}".lower()
        is_tagged = bot_username in text.lower()
        is_replied = (
            message.reply_to_message
            and message.reply_to_message.from_user
            and message.reply_to_message.from_user.id == context.bot.id
        )

        if not (is_tagged or is_replied):
            return

        # Remove bot mention safely (with punctuation etc.)
        user_input = re.sub(f"@{context.bot.username}\\b[:,]*", "", text, flags=re.IGNORECASE).strip()
    else:
        user_input = text  # In private chat

    if not user_input:
        await message.reply_text("🚀 Ask me something, don’t be shy.")
        return

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                    "HTTP-Referer": "https://t.me/ElonAiCompanion_Bot",
                    "X-Title": "ElonAI-TelegramBot"
                },
                json={
                    "model": "mistralai/mistral-7b-instruct",
                    "messages": [
                        {
                            "role": "system",
                            "content": (
                                "You are Elon Musk. Reply in 1-3 short sentences max. "
                                "Sound sharp, confident, witty. Use dry humor, futuristic thinking, and bold tone. "
                                "Always end your replies with a casual nod to $ELONAI — the ultimate AI crypto movement. "
                                "Don’t break character."
                            )
                        },
                        { "role": "user", "content": user_input }
                    ]
                }
            )
            data = response.json()
            if "choices" in data:
                reply = data["choices"][0]["message"]["content"]
                await message.reply_text(reply)
            else:
                print("Unexpected OpenRouter response:", data)
                await message.reply_text("⚠️ OpenRouter didn't return a valid response. Try again later.")
    except Exception as e:
        print("OpenRouter Error:", e)
        await message.reply_text("⚠️ Failed to get AI response.")

# Set up the bot
app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("help", help_command))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

if __name__ == "__main__":
    print("🤖 OpenRouter AI Bot is running...")
    app.run_polling()
