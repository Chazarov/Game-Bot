from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters.callback_data import CallbackData

from Game.Durak.game import Card, get_card_visual

from TG.my_scripts_lib import organaizer


class FieldCallback(CallbackData, prefix = "field_callback"):
    selected_number:int




def deck_buttons(carts_quality:int, attak:bool = None):

    middle_button_text = ""
    if(attak == None):
        middle_button_text = " "
    elif(attak == True):
        middle_button_text = "Подкинуть"
    elif(attak == False):
        middle_button_text = "Покрыть"


    kbd = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text = "<<", callback_data = "next_card"),
            InlineKeyboardButton(text = middle_button_text, callback_data = "action"),
            InlineKeyboardButton(text = ">>", callback_data = "prev_card")
        ],
        [
            InlineKeyboardButton(text = "Подтвердить ход", callback_data = "a")
        ]
    ])

    return kbd

def field_buttons(cards:list[Card]):
    buttons = [InlineKeyboardButton(text = get_card_visual(cards[i], True), callback_data = FieldCallback(selected_number = i).pack()) for i in range(len(cards))]
    kbd = InlineKeyboardMarkup(
        inline_keyboard=organaizer(buttons, page = 0, page_size = 2, line_size = 3)
    )

    return kbd