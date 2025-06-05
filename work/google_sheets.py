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


"""
# Устанавливаем доступ к Google Таблицам
credentials = ServiceAccountCredentials.from_json_keyfile_name(os.path.join(os.path.dirname(__file__), "..", "static", "google_cred.json"), ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive'])

httpAuth = credentials.authorize(httplib2.Http()) # Авторизуемся в системе
service = discovery.build('sheets', 'v4', http = httpAuth) # Выбираем работу с таблицами и 4 версию API 

driveService = discovery.build('drive', 'v3', http = httpAuth) # Выбираем работу с Google Drive и 3 версию API"""


