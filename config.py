from os import getenv

from telebot.types import BotCommand
import dotenv

dotenv.load_dotenv()

BOT_TOKEN = getenv("BOT_TOKEN")
FORWARD_CHAT_ID = -1002686227914
spreadsheetId = "1y1fCRSKsBS_Oz1CXb51C40mDePaxbc0f6IFA1oLZVYQ"
ADMINS_LIST = [596442939,]


BOT_COMMANDS = [
    BotCommand("start", "В главное меню 📎"),
]