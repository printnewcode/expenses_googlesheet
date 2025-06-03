from functools import wraps

from get_info import bot, table, info
from config import FORWARD_CHAT_ID
from work import google_sheets

def is_forwarded_chat(func):
    """
    Checking for needed chat.
    """

    @wraps(func)
    def wrapped(message) -> None:
        if not message.chat.id == FORWARD_CHAT_ID:
            return
        return func(message)

    return wrapped

