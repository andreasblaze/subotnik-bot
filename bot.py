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
special_words = {'привіт': ['Хай', 'Привіт', 'Шо ти', 'Здоровеньки були!'],
                 'анекдот': [
    'Є люди, які несуть в собі щастя. Коли ці люди поруч, все ніби стає яскравим і барвистим. Але моя дружина їх називає алкашами!',
    'З одного боку, в гості без пляшки не підеш. А з іншого – якщо в тебе є пляшка, та на холєру в гості пертись?',
    '– Кохана, давай миритися. Вибач мене, я був не правий.\n – Стоп! Не їж! Я приготую щось інше!',
    'Купив курс, по якому англійську мові вивчають уві сні. Але дружина вигнала викладачку із нашого ліжка.',
    'Кажуть, що у геніїв в будинку має бути безлад. Дивлюсь на свою дитину і гордість розпирає! Енштейна виховую!..',
    '– Тату, а правда, що в Індії чоловік до шлюбу не знає хто його дружина?\nТато зітхаючи:\n – Та виходить, що у нас теж так…',
    '– Куме, ваш пес з′їв мою курку!\n – Добре, куме, що сказали! Не буду вже їсти йому давати…',
    '– Куме, ваш пес з′їв мою курку!\n – Добре, куме, що сказали! Не буду вже їсти йому давати…',
    '– Алло, це лінія допомоги алкоголікам?\n – Так.\n – Підкажіть як зробити мохіто!',
    'Невістка свекрусі:\n\n – Мамо, чому ви стоїте біля відкритого вікна?\n – Та ось думаю: стрибнути чи закрити…\n – Стрибайте, я закрию!',
    'Допоможіть знайти чоловіка! Дуже заляканий і збентежений… Волосся сиве, одягнений в сині труси, сірий пуховик і чорну шкарпетку… Коротше, в чому встиг, курvа, в тому і втік!',
    '– Кума, а ти знаєш, що я коханка твого чоловіка?\n – А мій брехун сказав, що вона молода і красива!',
    'Галька зрозуміла, що шуба не норкова, коли пішов мокрий сніг і засмерділо цапом.',
    'pics/atls.jpg\n Атланти)))'
    ],
                  'кіт': 'Мяф', 'пес': 'Woof!'}
default_response = "шо за нах"

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
    message = update.message.lower()
    if message.reply_to_message and message.reply_to_message.from_user.id == bot.id:
        # If the message is a reply to the bot, get the original message text
        message_text = message.reply_to_message.text.lower()
    else:
        # Otherwise, get the current message text
        message_text = message.text.lower()

    # Send the response message or image
    if response.endswith('.jpg', '.jpeg', '.png', '.gif'):
        # Send the image
        with open(response, 'rb') as photo_file:
            context.bot.send_photo(chat_id=update.message.chat_id, photo=photo_file)
    else:
        # Send the text message
        context.bot.send_message(chat_id=update.message.chat_id, text=response)


    #response = special_words.get(message_text, default_response)

    if message_text in special_words:
        response = special_words[message_text]
        context.bot.send_message(chat_id=update.message.chat_id, text=response)
    elif update.message.photo:
        context.bot.send_message(chat_id=update.message.chat_id, text="Гарна картинка! Де це було спізжено?")
    else:
        context.bot.send_message(chat_id=update.message.chat_id, text=default_response)

    # Send the response message
    #context.bot.send_message(chat_id=update.message.chat_id,
    #                        text=response)

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