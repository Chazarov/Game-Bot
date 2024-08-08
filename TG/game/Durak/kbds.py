from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters.callback_data import CallbackData

from Game.Durak.interface import draw_choisen_card, draw_card

from TG.my_scripts_lib import organaizer





CONFIRM_CALLBACK = "confirm_callback"
ACTION_BUTTON_CALLBACK = "action_button_callback"
END_GAME_CALLBACK = "end_game_callback"
NEXT_CARD_CALLBACK = "next_card_callback"
PREV_CARD_CALLBACK = "prev_card_callback"

class FieldCallback(CallbackData, prefix = "field_callback"):
    selected_number:int

class CartNavigationCallback(CallbackData, prefix = ""):
    next_card:int
    






def deck_buttons(is_attak:bool = None):

    middle_button_text = ""
    if(is_attak == None):
        middle_button_text = " "
    elif(is_attak == True):
        middle_button_text = "Подкинуть"
    elif(is_attak == False):
        middle_button_text = "Покрыть"

    kbd = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text = "<<", callback_data = NEXT_CARD_CALLBACK),
            InlineKeyboardButton(text = middle_button_text, callback_data = ACTION_BUTTON_CALLBACK),
            InlineKeyboardButton(text = ">>", callback_data = PREV_CARD_CALLBACK)
        ],
        [
            InlineKeyboardButton(text = "Подтвердить ход", callback_data = CONFIRM_CALLBACK)
        ]
    ])

    return kbd



def field_buttons(lobby_id:int, cards:list[list[int, str]], choisen:int = None):
    buttons = [InlineKeyboardButton(text = draw_card(cards[i], True) if i != choisen else draw_choisen_card(cards[i]), callback_data = FieldCallback(selected_number = i, lobby_id = lobby_id).pack()) for i in range(len(cards))]
    kbd = InlineKeyboardMarkup(
        inline_keyboard=organaizer(buttons, page = 0, page_size = 2, line_size = 3)
    )

    return kbd

def confirm_end_of_game_buttons():
    kbd = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text = "Завершить игру", callback_data = END_GAME_CALLBACK)
            ],
        ]
    )
