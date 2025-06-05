import os

import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime, timezone, timedelta
from functools import wraps

import config
from keyboards import START_BUTTON, PAYMENT_TYPES, ADMIN_BUTTONS
from static.types import types, subtypes
from work import google_sheets
from create_keyboard import create_keyboard_type
import httplib2
from googleapiclient import discovery
from oauth2client.service_account import ServiceAccountCredentials
from gspread import Client, Spreadsheet, Worksheet, service_account
from oauth2client.service_account import ServiceAccountCredentials

timezone_offset = +3.0
tzinfo = timezone(timedelta(hours=timezone_offset))

info = {}

commands = config.BOT_COMMANDS

bot = telebot.TeleBot(
    config.BOT_TOKEN,
    threaded=False,
    skip_pending=True,
)

bot.set_my_commands(commands)

# Устанавливаем доступ к Google Таблицам
credentials = ServiceAccountCredentials.from_json_keyfile_name(os.path.join(os.path.dirname(__file__), "static", "google_cred.json"), ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive'])

httpAuth = credentials.authorize(httplib2.Http()) # Авторизуемся в системе
service = discovery.build('sheets', 'v4', http = httpAuth) # Выбираем работу с таблицами и 4 версию API 

print('https://docs.google.com/spreadsheets/d/' + config.spreadsheetId)

driveService = discovery.build('drive', 'v3', http = httpAuth) # Выбираем работу с Google Drive и 3 версию API

def client_init_json() -> Client:
    """Создание клиента для работы с Google Sheets."""
    return service_account(filename=os.path.join(os.path.dirname(__file__), "static", "google_cred.json"))

def get_table_by_id(client: Client, table_url):
    """Получение таблицы из Google Sheets по ID таблицы."""
    
    return client.open_by_key(table_url)
    """except:
        spreadsheet = service.spreadsheets().create(body = {
    'properties': {'title': 'Затраты', 'locale': 'ru_RU'},
    'sheets': [{'properties': {'sheetType': 'GRID',
                               'sheetId': 0,
                               'title': 'Лист 1',
                               'gridProperties': {'rowCount': 100, 'columnCount': 15}}}]
}).execute()
        access = driveService.permissions().create(
    fileId = spreadsheetId,
    body = {'type': 'user', 'role': 'writer', 'emailAddress': 'artemplotnikov0303@gmail.com'},  # Открываем доступ на редактирование
    fields = 'id'
).execute()
        return client.open_by_key(spreadsheet.id)"""

def get_worksheet_info(table: Spreadsheet) -> dict:
    """Возвращает количество листов в таблице и их названия."""
    worksheets = table.worksheets()
    worksheet_info = {
        "count": len(worksheets),
        "names": [worksheet.title for worksheet in worksheets]
    }
    return worksheet_info

def last_filled_row(worksheet):
    str_list = list(filter(None, worksheet.col_values(1)))
    return len(str_list)

def insert_one(table: Spreadsheet, title: str, data: list):
    """Вставка данных в лист."""
    worksheet = table.worksheet(title)
    worksheet.insert_row(data, index=last_filled_row(worksheet)+1)


client = client_init_json()
table = get_table_by_id(client, config.spreadsheetId)
info = get_worksheet_info(table)


"""Admin"""

def admin_permission(func):
    """
    Checking user for admin permission to access the function.
    """

    @wraps(func)
    def wrapped(message) -> None:
        user_id = message.from_user.id
        if not user_id in config.ADMINS_LIST:
            bot.send_message(user_id, "У вас нет доступа к админ-панели")
            return
        return func(message)

    return wrapped


@admin_permission
@bot.message_handler(commands=["admin"])
def admin_panel(message):
    """Админ-панель"""
    bot.send_message(chat_id=message.chat.id, text="Выберите, что хотите изменить", reply_markup=ADMIN_BUTTONS)


"""User"""


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

    elif call.data.split("_")[1] == "type" or call.data.split("_")[1] == "subtype":
        text = ""
        if call.data.split("_")[1] == "type":
            with open('data_types.txt', 'r', encoding="utf-8") as file:
                for line in file.readlines():
                    text += f"{line.strip()}\n"
            markup = InlineKeyboardMarkup()
            delete_types = InlineKeyboardButton(text="Удалить", callback_data="delete_types")
            add_types = InlineKeyboardButton(text="Добавить", callback_data="add_types")
            markup.add(delete_types).add(add_types)
            
            bot.send_message(chat_id=call.message.chat.id, text=f"Вот список доступных!\n\n{text}", reply_markup=markup)
        else:
            with open('data_subtypes.txt', 'r', encoding="utf-8") as file:
                for line in file.readlines():
                    text += f"{line.strip()}\n"

            markup = InlineKeyboardMarkup()
            delete_subtypes = InlineKeyboardButton(text="Удалить", callback_data="delete_subtypes")
            add_subtypes = InlineKeyboardButton(text="Добавить", callback_data="add_subtypes")
            markup.add(delete_subtypes).add(add_subtypes)
            bot.send_message(chat_id=call.message.chat.id, text=f"Вот список доступных!\n\n{text}", reply_markup=markup)

    elif call.data.split("_")[1] == "types" or call.data.split("_")[1] == "subtypes":
        if call.data.split("_")[0] == "delete":
            msg = bot.send_message(chat_id=user_id, text="Введите наименование, которое нужно удалить")
            bot.register_next_step_handler(msg, register_delete, type_=0 if call.data.split("_")[1] == "types" else 1)
        elif call.data.split("_")[0] == "add":
            msg = bot.send_message(chat_id=user_id, text="Введите новое наименование")
            bot.register_next_step_handler(msg, register_add, type_=0 if call.data.split("_")[1] == "types" else 1)

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


def register_delete(message, type_):
    if type_ == 0:
        with open('data_types.txt', 'r', encoding="utf-8") as file:
            lines = file.readlines()
        new_lines = [line.strip() for line in lines if message.text not in line]

        with open('data_types.txt', 'w', encoding="utf-8") as file:
            for line in new_lines:
                if line:
                    file.write(line + '\n')
    else:
        with open('data_subtypes.txt', 'r', encoding="utf-8") as file:
            lines = file.readlines()
        new_lines = [line.strip() for line in lines if message.text not in line]

        with open('data_subtypes.txt', 'w', encoding="utf-8") as file:
            for line in new_lines:
                if line:
                    file.write(line + '\n')
    bot.send_message(chat_id=message.chat.id, text="Наименование успешно удалено!")

def register_add(message, type_):
    if type_ == 0:
        with open('data_types.txt', 'a', encoding="utf-8") as file:
            file.write('\n' + message.text + '\n')
    else:
        with open('data_subtypes.txt', 'a', encoding="utf-8") as file:
            file.write('\n' + message.text + '\n')
    bot.send_message(chat_id=message.chat.id, text="Наименование успешно добавлено!")

@bot.message_handler(func=lambda message: True)
def get_message(message):
    try:
        if message.chat.id == config.FORWARD_CHAT_ID:
            data_ = message.text.split("|")
            data_.append(datetime.now(tzinfo).strftime("%Y-%m-%d"))
            data_.append(datetime.now(tzinfo).strftime("%H:%M"))
            insert_one(
                table=table,
                title=info['names'][0],
                data=data_
            )
            print("Данные добавлены!")
        elif message.text == "/start":
            try:
                del info[message.chat.id]
                bot.clear_step_handler_by_chat_id(message.chat.id)
                start(message)
            except:
                pass
    except Exception as e:
        print(e)


bot.polling(none_stop=True)