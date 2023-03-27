from telegram.ext.updater import Updater
from telegram.update import Update
from telegram.ext.callbackcontext import CallbackContext
from telegram.ext.commandhandler import CommandHandler
from telegram.ext.messagehandler import MessageHandler
from telegram.ext.filters import Filters

updater = Updater("5135025834:AAFClsqmgmeR8LvdaytZOpSvsNJpZdxW2DQ", use_context=True)


def start(update: Update, context: CallbackContext):
	update.message.reply_text(
        "Hi, maaan! In this difficult time, we must not forget what it is to communicate with your bros. Be in touch using this bot everyweekly.")

def unknown_text(update: Update, context: CallbackContext):
    update.message.reply_text(
        "Sorry I can't recognize you , you said '%s'. Bruh..." % update.message.text)
  
def send_message(update: Update, context: CallbackContext):
    update.message.sendMessage(chat_id = -1001554676415, text = 
        "Hey there! You need to talk and take a rest!")  
  
updater.dispatcher.add_handler(CommandHandler('start', start))
updater.dispatcher.add_handler(MessageHandler(Filters.text, unknown_text))
updater.dispatcher.add_handler(MessageHandler(Filters.command, unknown_text))  # Filters out unknown commands
updater.dispatcher.add_handler(MessageHandler(Filters.text, unknown_text))     # Filters out unknown messages.
  
updater.start_polling()