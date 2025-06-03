# Настройка бота

1. ```python -m venv venv```
2. ```venv\Scripts\activate```
3. ```pip install -r requirements.txt```
4. Создать в корневой директории файл .env

.env:
```BOT_TOKEN=```

5. Ввести в config.py свои значения spreadsheetId (id Google таблицы) и FORWARD_CHAT_ID (id чата, из которого берется информация для заполнения таблицы)


# Запуск бота

```python get_info.py```