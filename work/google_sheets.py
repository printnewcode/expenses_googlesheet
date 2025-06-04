import os

import logging
from datetime import datetime
from traceback import format_exc
from typing import List

import httplib2
from googleapiclient import discovery
from oauth2client.service_account import ServiceAccountCredentials
from gspread import Client, Spreadsheet, Worksheet, service_account
from oauth2client.service_account import ServiceAccountCredentials

# Устанавливаем доступ к Google Таблицам
credentials = ServiceAccountCredentials.from_json_keyfile_name(os.path.join(os.path.dirname(__file__), "..", "static", "google_cred.json"), ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive'])

httpAuth = credentials.authorize(httplib2.Http()) # Авторизуемся в системе
service = discovery.build('sheets', 'v4', http = httpAuth) # Выбираем работу с таблицами и 4 версию API 

spreadsheetId = "1zpBzjVnqLL8gyCP74mXWqTlQNOrbQ-sjs7vL8ulUdH0" # сохраняем идентификатор файла
print('https://docs.google.com/spreadsheets/d/' + spreadsheetId)

driveService = discovery.build('drive', 'v3', http = httpAuth) # Выбираем работу с Google Drive и 3 версию API

def client_init_json() -> Client:
    """Создание клиента для работы с Google Sheets."""
    return service_account(filename=os.path.join(os.path.dirname(__file__), "..", "static", "google_cred.json"))

def get_table_by_id(client: Client, table_url):
    """Получение таблицы из Google Sheets по ID таблицы."""
    try:
        return client.open_by_key(table_url)
    except:
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
        return client.open_by_key(spreadsheet.id)

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

"""insert_one(table=table,
               title=worksheet_info['names'][0],
               data=["Загрузка", "Расходы на доставку", "Безналичные", "2000"])"""
client = client_init_json()
table = get_table_by_id(client, spreadsheetId)
info = get_worksheet_info(table)

def main():
    # Создаем клиента и открываем таблицу
    
    # Получаем информацию о листах
    
    print(f"Количество листов: {info['count']}")
    print("Названия листов:")
    for name in info['names']:

        print(name)



if __name__ == '__main__':
    main()

