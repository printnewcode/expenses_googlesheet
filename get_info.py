import telebot

import config
from keyboards import START_BUTTON, PAYMENT_TYPES
from static.types import types, subtypes
from work import google_sheets
from work.google_sheets import main, client_init_json, get_table_by_id, get_worksheet_info
from create_keyboard import create_keyboard_type

info = {}

commands = config.BOT_COMMANDS

bot = telebot.TeleBot(
    config.BOT_TOKEN,
    threaded=False,
    skip_pending=True,
)

bot.set_my_commands(commands)

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(chat_id=message.chat.id, text="Добро пожаловать!\n\nДля добавления нового расхода нажмите кнопку ниже", reply_markup=START_BUTTON)


@bot.callback_query_handler(lambda c: c.data=="new-expenses")
def choose_type(call):
    info[call.message.chat.id] = {}
    bot.send_message(chat_id=call.message.chat.id, text="Выберите направление расхода", reply_markup=create_keyboard_type(types, 0))


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    user_id = call.message.chat.id

    if call.data.startswith('type'):
        info[user_id]['type'] = types[int(call.data.split("_")[1])]
        bot.send_message(user_id, "Выберите статью затрат:", reply_markup=create_keyboard_type(subtypes, 1))

    elif call.data.startswith('subtype'):
        info[user_id]['subtype'] = subtypes[int(call.data.split("_")[1])]
        bot.send_message(user_id, "Выберите способ оплаты:", reply_markup=PAYMENT_TYPES)

    elif call.data.startswith('payment'):
        info[user_id]['payment'] = "Наличные" if call.data.split("_")[1] == "money" else "Безналичные"
        bot.send_message(user_id, "Введите сумму:")
        bot.register_next_step_handler(call.message, process_amount)

    elif call.data.endswith("other"):
        msg = bot.send_message(chat_id=call.message.chat.id, text="Введите свое значение")
        bot.register_next_step_handler(msg, register_other, call.data.split("_")[0])


def register_other(message, type_):
    user_id = message.chat.id
    info[user_id][f"{type_}"] = message.text

    if type_ == "type":
        bot.send_message(user_id, "Выберите статью затрат:", reply_markup=create_keyboard_type(subtypes, 1))
    else:
        bot.send_message(user_id, "Выберите способ оплаты:", reply_markup=PAYMENT_TYPES)


def process_amount(message):
    user_id = message.chat.id
    info[user_id]['amount'] = message.text

    # Формируем сообщение для переадресации
    result_message = f"{info[user_id]['type']} | {info[user_id]['subtype']} | {info[user_id]['payment']} | {info[user_id]['amount']}"
    
    
    bot.send_message(config.FORWARD_CHAT_ID, result_message)
    bot.send_message(user_id, "Данные отправлены!")
    # Очищаем данные после отправки (опционально)
    del info[user_id]

try:
    bot.remove_webhook()
except Exception as e:
    print(f"Ошибка при удалении вебхука: {e}")

@bot.message_handler(func=lambda message: True)
def get_message(message):
    try:
        if message.chat.id == config.FORWARD_CHAT_ID:
            data_ = message.text.split("|")

            google_sheets.insert_one(
                table=table,
                title=info['names'][0],
                data=data_
            )
            print("Данные добавлены!")
    except Exception as e:
        print(e)

client = client_init_json()
table = get_table_by_id(client, config.spreadsheetId)
info = get_worksheet_info(table)


bot.polling(none_stop=True)