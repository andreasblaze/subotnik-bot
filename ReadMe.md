# Telegram Reminder Bot

This is a Telegram bot that sends weekly reminders and responds to special keywords with funny messages or images.

## Setup

To use this bot, you'll need to:

1. Create a Telegram bot using [BotFather](https://core.telegram.org/bots#6-botfather).
2. Clone this repository and install the required dependencies (`python-telegram-bot` and `config`).
3. Create a `config.py` file with the following variables:

TOKEN = 'YOUR_BOT_TOKEN'
chat_id = 'YOUR_CHAT_ID'
special_words = {
'word1': ['response1', 'response2', ...],
'word2': ['response3', 'response4', ...],
...
}
default_response = ['default response1', 'default response2', ...]

Replace `YOUR_BOT_TOKEN` with the token provided by BotFather, and `YOUR_CHAT_ID` with the chat ID of the chat where you want to receive the reminders.
4. Run the bot using `python bot.py`.

## Usage

The bot supports the following commands:

- `/start`: Sends a greeting message.
- `/help`: Displays a list of special words that the bot responds to, and instructions for setting up the weekly reminder.
- `/setreminder`: Sets up a weekly reminder to take a break and stretch your muscles.
- Special words: When you send a message containing a special word (e.g. "word1"), the bot will respond with a funny message or image associated with that word. If there is no associated message or image, the bot will send a default response.

## Contributing

Contributions are welcome! If you find a bug or have a feature request, please open an issue or submit a pull request.

## License

This bot is licensed under the [MIT License](https://github.com/andreasblaze/weekly-subotnik-bot/blob/main/LICENSE).
