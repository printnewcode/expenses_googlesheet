from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

def create_keyboard_type(list_: list, type_: int = 0) -> list:
    list_ = []
    if type_ == 0:
        prefix = "type"

        with open('data_types.txt', 'r', encoding="utf-8") as file:
            list_ = [line.strip() for line in file.readlines()]
    elif type_ == 1:
        prefix = "subtype"
        with open('data_subtypes.txt', 'r', encoding="utf-8") as file:
            list_ = [line.strip() for line in file.readlines()]
    
    
    keyboard_types = InlineKeyboardMarkup()
    for index, item in enumerate(list_):
        button = InlineKeyboardButton(item, callback_data=f"{prefix}_{list_.index(item)}")
        keyboard_types.add(button)

        # Добавляем новую строку после каждых трех кнопок
        if (index + 1) % 3 == 0:
            keyboard_types.add(InlineKeyboardButton(" ", callback_data="dummy"))  # Пустая кнопка для новой строки
    keyboard_types.add(InlineKeyboardButton(text="Другое", callback_data=f"{prefix}_other"))
    return keyboard_types