from os import getenv

from telebot.types import BotCommand
import dotenv

dotenv.load_dotenv()

BOT_TOKEN = getenv("BOT_TOKEN")
FORWARD_CHAT_ID = -1002686227914
spreadsheetId = "1zpBzjVnqLL8gyCP74mXWqTlQNOrbQ-sjs7vL8ulUdH0"

BOT_COMMANDS = [
    BotCommand("start", "В главное меню 📎"),
]