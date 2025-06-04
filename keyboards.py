from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

START_BUTTON = InlineKeyboardMarkup()
start_button = InlineKeyboardButton(text="Добавить расход", callback_data="new-expenses")
START_BUTTON.add(start_button)

PAYMENT_TYPES = InlineKeyboardMarkup()
money = InlineKeyboardButton(text="Наличные", callback_data="payment_money")
card = InlineKeyboardButton(text="Безналичные", callback_data="payment_card")
PAYMENT_TYPES.add(money).add(card)

ADMIN_BUTTONS = InlineKeyboardMarkup()
admin_type = InlineKeyboardButton(text="Направления затрат", callback_data="admin_type")
admin_subtype = InlineKeyboardButton(text="Статьи затрат", callback_data="admin_subtype")
ADMIN_BUTTONS.add(admin_type).add(admin_subtype)