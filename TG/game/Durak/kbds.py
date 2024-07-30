from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters.callback_data import CallbackData





def deck_buttons(carts_quality:int, attak:bool = None):

    middle_button_text = ""
    if(attak == None):
        middle_button_text = "."
    elif(attak == True):
        middle_button_text = "Подкинуть"
    elif(attak == False):
        middle_button_text = "Покрыть"


    kbd = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text = "<<", callback_data = ""),
            InlineKeyboardButton(text = middle_button_text, callback_data = ""),
            InlineKeyboardButton(text = ">>", callback_data = "")
        ],
        [
            InlineKeyboardButton(text = "Подтвердить ход")
        ]
    ])

    return kbd