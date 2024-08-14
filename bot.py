import logging
import telegram
from telegram.ext import Dispatcher, CommandHandler, MessageHandler, Filters
from flask import Flask, request
from datetime import datetime, time, timedelta
import random
import config

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Set up the bot using the token provided by BotFather
bot = telegram.Bot(config.TOKEN)

# Create a dispatcher
dispatcher = Dispatcher(bot, None, workers=0)

chat_id = config.chat_id

# Define the special words and corresponding funny messages
special_words = config.special_words
default_response = config.default_response

# Define the callback function for the /start command
def start(update, context):
    context.bot.send_message(chat_id=update.message.chat_id,
                             text='Привіт! Я бот, який може надсилати вам щотижневі нагадування. Введіть /help для отримання додаткової інформації.')

# Define the callback function for the /help command
def help(update, context):
    context.bot.send_message(chat_id=update.message.chat_id,
                             text='Введіть одне з наступних спеціальних слів, і я відповім смішним повідомленням:\n' +
                                  ', '.join(special_words.keys()) + '\n\n' +
                                  'Ви також можете використовувати команду /setreminder, щоб установити щотижневе нагадування.')

# Define the callback function for the /setreminder command
def setreminder(update, context):
    now = datetime.now().time()
    reminder_time = time(hour=12)  # Set the reminder time to noon
    if now >= reminder_time:
        reminder_date = datetime.today() + timedelta(days=(7 - datetime.today().weekday()))
    else:
        reminder_date = datetime.today() + timedelta(days=(reminder_time.weekday() - datetime.today().weekday()))

    context.job_queue.run_once(sendreminder, when=reminder_date.time(), context=update.message.chat_id)

    context.bot.send_message(chat_id=update.message.chat_id,
                             text='Нагадування встановлено! Ви отримуватимете від мене повідомлення щотижня опівдні.')

# Define the callback function for the weekly reminder message
def sendreminder(context):
    context.bot.send_message(chat_id=context.job.context,
                             text='Не забудьте зробити перерву і розім\'яти кістки!')

# Define the callback function for handling special words
def specialword(update, context):
    message = update.message
    if message.reply_to_message and message.reply_to_message.from_user.id == bot.id:
        message_text = message.reply_to_message.text.lower()
    else:
        message_text = message.text.lower()

    if message_text in special_words:
        response = random.choice(special_words[message_text])
        context.bot.send_message(chat_id=update.message.chat_id, text=response)
    elif update.message.photo:
        context.bot.send_message(chat_id=update.message.chat_id, text="Гарна картинка! Де це було спізжено?")
    else:
        context.bot.send_message(chat_id=update.message.chat_id, text=random.choice(default_response))

# Add command and message handlers to the dispatcher
dispatcher.add_handler(CommandHandler('start', start))
dispatcher.add_handler(CommandHandler('help', help))
dispatcher.add_handler(CommandHandler('setreminder', setreminder))
dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, specialword))

@app.route('/', methods=['POST'])
def webhook():
    if request.method == "POST":
        update = telegram.Update.de_json(request.get_json(force=True), bot)
        dispatcher.process_update(update)
    return "ok"

# Entry point for Google Cloud Function
def main(request):
    return webhook()