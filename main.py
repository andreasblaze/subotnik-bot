import logging
import telegram
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
from flask import Flask, request
from datetime import datetime, timedelta
import pytz
import random
import openai  # OpenAI API
import config
import json
import os

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Set up the bot using the token provided by BotFather
bot = telegram.Bot(config.TOKEN)

# OpenAI API key
openai.api_key = config.OPENAI_API_KEY

# Define daily token limit
DAILY_TOKEN_LIMIT = 25000  # Adjust as needed
USAGE_FILE = "usage.json"

# Define Kyiv timezone
kyiv_tz = pytz.timezone("Europe/Kyiv")

# Create a app
app = Application.builder().token(config.TOKEN).build()

# Function to initialize or load usage tracking
def load_usage():
    if not os.path.exists(USAGE_FILE):
        return {"date": str(datetime.now(kyiv_tz).date()), "tokens_used": 0}
    with open(USAGE_FILE, "r") as f:
        return json.load(f)

def save_usage(data):
    with open(USAGE_FILE, "w") as f:
        json.dump(data, f)

usage_data = load_usage()

# Reset usage counter if a new day has started
def reset_usage_if_new_day():
    global usage_data
    current_date = str(datetime.now(kyiv_tz).date())
    if usage_data["date"] != current_date:
        usage_data = {"date": current_date, "tokens_used": 0}
        save_usage(usage_data)

# Function for OpenAI response with token tracking
def ai_response(prompt):
    reset_usage_if_new_day()
    global usage_data

    if usage_data["tokens_used"] >= DAILY_TOKEN_LIMIT:
        return "Так, цей, ліміт використання OpenAI API на сьогодні вичерпано. Не нахабнійте"

    try:
        response = openai.Completion.create(
            engine="gpt-3.5-turbo",
            prompt=prompt,
            max_tokens=150,
            temperature=0.7
        )
        tokens_used = response.usage["total_tokens"]
        usage_data["tokens_used"] += tokens_used
        save_usage(usage_data)
        return response.choices[0].text.strip()
    except Exception as e:
        logger.error(f"OpenAI API error: {e}")
        return "Вибач, якась трабла з токеном OpenAI. Спробуй ще раз, мб пощастить"

# Callback for /start command
def start(update, context):
    context.bot.send_message(
        chat_id=update.message.chat_id,
        text="Якщо вже так вийшло, що у тебе деменція, то можу допомогти з нагадуваннями, голосовими чатами та навіть з мисленням, мовленням і виконанням повсякденних завдань."
    )

# Callback for /help command
def help(update, context):
    context.bot.send_message(
        chat_id=update.message.chat_id,
        text="Команди:\n/start - Почати\n/help - Допомога\n/setreminder - Установити нагадування\n"
             "Якщо хочеш щось сказати - кажи. Не мучай жопу, якщо срати перехтів."
    )

# Callback for handling text messages
def handle_message(update, context):
    message = update.message.text
    response = ai_response(message)
    context.bot.send_message(chat_id=update.message.chat_id, text=response)

# Add handlers to the app
app.add_handler(CommandHandler('start', start))
app.add_handler(CommandHandler('help', help))
app.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

@app.route('/', methods=['POST'])
def webhook():
    if request.method == "POST":
        update = telegram.Update.de_json(request.get_json(force=True), bot)
        app.process_update(update)
    return "ok"

# Entry point for Google Cloud Function
def main(request):
    return webhook()