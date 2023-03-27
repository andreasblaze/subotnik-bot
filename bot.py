import logging
import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from datetime import datetime, time, timedelta

TOKEN     = "5135025834:AAFClsqmgmeR8LvdaytZOpSvsNJpZdxW2DQ"
chat_id   = "-1001554676415"

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# Define the special words and corresponding funny messages
special_words = {'hello': 'Hi there!', 'cat': 'Meow!', 'dog': 'Woof!'}
default_response = "I don't know what to say to that."

# Define the callback function for the /start command
def start(update, context):
    context.bot.send_message(chat_id=update.message.chat_id,
                             text='Hello! I am a bot that can send you weekly reminders. Type /help for more information.')

# Define the callback function for the /help command
def help(update, context):
    context.bot.send_message(chat_id=update.message.chat_id,
                             text='Type one of the following special words and I will respond with a funny message:\n' +
                                  ', '.join(special_words.keys()) + '\n\n' +
                                  'You can also use the /setreminder command to set a weekly reminder.')

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
                             text='Reminder set! You will receive a message from me every week at noon.')

# Define the callback function for the weekly reminder message
def sendreminder(context):
    context.bot.send_message(chat_id=context.job.context,
                             text='Don\'t forget to take a break and stretch your legs!')

# Define the callback function for handling special words
def specialword(update, context):
    # Get the user's message text and check if it contains a special word
    message_text = update.message.text.lower()
    response = special_words.get(message_text, default_response)

    # Send the response message
    context.bot.send_message(chat_id=update.message.chat_id,
                             text=response)

# Set up the bot using the token provided by BotFather
bot = telegram.Bot(TOKEN)

# Create an Updater object and attach the relevant handlers
updater = Updater(TOKEN, use_context=True)
updater.dispatcher.add_handler(CommandHandler('start', start))
updater.dispatcher.add_handler(CommandHandler('help', help))
updater.dispatcher.add_handler(CommandHandler('setreminder', setreminder))
updater.dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, specialword))

# Start the bot and schedule the weekly reminder message
updater.start_polling()
updater.idle()