from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters.callback_data import CallbackData


class Game_callback_data(CallbackData, prefix = "game"):
    lobbi_id:int
    bet:int
    X:int
    Y:int
    n:int
    m:int
    win_score:int


def game_buttons(callback_data:Game_callback_data, field:str):
    cbd = callback_data
    kbd = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text = field[y*cbd.m + x],\
 callback_data = Game_callback_data(lobbi_id = cbd.lobbi_id, Y = y, X = x, n = cbd.n, m = cbd.m, win_score = cbd.win_score, bet = cbd.bet).pack())\
          for x in range(cbd.m)] for y in range(cbd.n)
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