import logging
import telegram
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
from flask import Flask, request
from datetime import datetime, timedelta
import pytz
import openai  # OpenAI API
import config
import json
import os

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app (needed for webhooks)
app = Flask(__name__)

# OpenAI API key
openai.api_key = config.OPENAI_API_KEY

# Define daily token limit
DAILY_TOKEN_LIMIT = 25000  # Adjust as needed
USAGE_FILE = "usage.json"

# Define Kyiv timezone
kyiv_tz = pytz.timezone("Europe/Kyiv")

# Function to initialize or load usage tracking
def load_usage():
    if not os.path.exists(USAGE_FILE):
        return {"date": str(datetime.now(kyiv_tz).date()), "tokens_used": 0}
    with open(USAGE_FILE, "r") as f:
        return json.load(f)

async def save_usage(data):
    with open(USAGE_FILE, "w") as f:
        json.dump(data, f)

usage_data = load_usage()

# Reset usage counter if a new day has started
async def reset_usage_if_new_day():
    global usage_data
    current_date = str(datetime.now(kyiv_tz).date())
    if usage_data["date"] != current_date:
        usage_data = {"date": current_date, "tokens_used": 0}
        await save_usage(usage_data)

# Function for OpenAI response with token tracking
async def ai_response_async(prompt):
    await reset_usage_if_new_day()
    global usage_data

    if usage_data["tokens_used"] >= DAILY_TOKEN_LIMIT:
        return "Так, цей, ліміт використання OpenAI API на сьогодні вичерпано. Не нахабнійте"

    try:
        response = await openai.ChatCompletion.acreate(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=150,
            temperature=0.7
        )
        tokens_used = response["usage"]["total_tokens"]
        usage_data["tokens_used"] += tokens_used
        await save_usage(usage_data)
        return response["choices"][0]["message"]["content"].strip()
    except Exception as e:
        logger.error(f"OpenAI API error: {e}")
        return "Вибач, якась трабла з API OpenAI. Спробуй ще раз, мб пощастить"

# Callback for /start command
async def start(update: Update, context: CallbackContext):
    await update.message.reply_text(
        "Якщо вже так вийшло, що у тебе деменція, то можу допомогти з нагадуваннями, голосовими чатами та навіть з мисленням, мовленням і виконанням повсякденних завдань."
    )

# Callback for /help command
async def help(update: Update, context: CallbackContext):
    await update.message.reply_text(
        "Команди:\n/start - Почати\n/help - Допомога\n/setreminder - Установити нагадування\n"
        "Якщо хочеш щось сказати - кажи. Не мучай жопу, якщо срати перехтів."
    )

# Callback for handling text messages
async def handle_message(update: Update, context: CallbackContext):
    message = update.message.text
    logger.info(f"Handling message: {message}")  # Log received message
    response = await ai_response_async(message)
    logger.info(f"Total tokens used today: {usage_data['tokens_used']}/{DAILY_TOKEN_LIMIT}")  # Log token usage
    await update.message.reply_text(response)

# Set up the Telegram bot application
application = Application.builder().token(config.TOKEN).build()

# Add handlers to the app
application.add_handler(CommandHandler('start', start))
application.add_handler(CommandHandler('help', help))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

@app.route("/", methods=["POST"])
# a way to send Telegram updates
async def webhook():
    if request.method == "POST":
        update = Update.de_json(request.get_json(force=True), application.bot)
        await application.process_update(update)
    return "ok"

# Entry point for Google Cloud Function
def main():
    application.run_polling()  #Runs bot properly

# Checks if the script executed directly and not when imported as a module in another script
if __name__ == "__main__":
    main()