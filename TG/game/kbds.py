from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters.callback_data import CallbackData


class Game_callback_data(CallbackData, prefix = "game"):
    field:str
    lobbi_id:int
    X:int
    Y:int
    n:int
    m:int


def game_buttons(lobbi_id:int, field:str, n:int, m:int):
    kbd = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text = field[y*m + x],\
 callback_data = Game_callback_data(lobbi_id = lobbi_id, field = field, Y = y, X = x, n = n, m = m).pack())\
          for x in range(m)] for y in range(n)
    ])

    return kbd

def finally_buttons():
    kbd = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text = "Завершить игру", callback_data = "end_game")
            ]
        ]
    )

    return kbd