import logging
import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from datetime import datetime, time, timedelta
import random
import config

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

chat_id   = config.chat_id

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
    # Get the current time and calculate the time of the next reminder
    now = datetime.now().time()
    reminder_time = time(hour=12) # Set the reminder time to noon
    if now >= reminder_time:
        # If it's already past noon today, schedule the next reminder for next week
        reminder_date = datetime.today() + timedelta(days=(7 - datetime.today().weekday()))
    else:
        # Otherwise, schedule the next reminder for this week
        reminder_date = datetime.today() + timedelta(days=(reminder_time.weekday() - datetime.today().weekday()))

    # Schedule the reminder message using the job queue
    context.job_queue.run_once(sendreminder, when=reminder_date.time(), context=update.message.chat_id)

    context.bot.send_message(chat_id=update.message.chat_id,
                             text='Нагадування встановлено! Ви отримуватимете від мене повідомлення щотижня опівдні.')

# Define the callback function for the weekly reminder message
def sendreminder(context):
    context.bot.send_message(chat_id=context.job.context,
                             text='Не забудьте зробити перерву і розім\'яти кістки!')

# Define the callback function for handling special words
def specialword(update, context):
    # Get the user's message text and check if it contains a special word
    message = update.message
    if message.reply_to_message and message.reply_to_message.from_user.id == bot.id:
        # If the message is a reply to the bot, get the original message text
        message_text = message.reply_to_message.text.lower()
    else:
        # Otherwise, get the current message text
        message_text = message.text.lower()

    # Send the response message or image
    if message_text in special_words:
        response         = random.choice(special_words[message_text])
        default_response = random.choice(default_response)
        context.bot.send_message(chat_id=update.message.chat_id, text=response)
        
    elif update.message.photo:
        context.bot.send_message(chat_id=update.message.chat_id, text="Гарна картинка! Де це було спізжено?")
    else:
        context.bot.send_message(chat_id=update.message.chat_id, text=default_response)



# Set up the bot using the token provided by BotFather
bot = telegram.Bot(config.TOKEN)

# Create an Updater object and attach the relevant handlers
updater = Updater(config.TOKEN, use_context=True)
updater.dispatcher.add_handler(CommandHandler('start', start))
updater.dispatcher.add_handler(CommandHandler('help', help))
updater.dispatcher.add_handler(CommandHandler('setreminder', setreminder))
updater.dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, specialword))

# Start the bot and schedule the weekly reminder message
updater.start_polling()
updater.idle()