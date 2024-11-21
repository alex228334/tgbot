from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_support_keyboard():
    support_contacts = [
        ("🆘Тех. Поддержка", "https://t.me/xxnett_tss"),
    ]
    keyboard_buttons = [
        [InlineKeyboardButton(text=name, url=link)] for name, link in support_contacts
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
    return keyboard


def get_change_card_keyboard():
    change_button = InlineKeyboardButton(text="Изменить номер карты", callback_data="change_card")
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[change_button]])
    return keyboard
