from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters.callback_data import CallbackData

from Game.TTT import strings as TTTstrings
from Game.Durak import strings as DURAKstrings



# Теперь все парамеиры игры будут находится в базе данных в объекте лобби.
class GameBase(CallbackData, prefix = "game"):
    game_name:str
    lobby_id:int
    bet:int
class TTT_game_callback_data(CallbackData, prefix = "Tic tac toe game"):
    lobby_id:int
    X:int
    Y:int
    n:int
    m:int
    win_score:int

class Durak_game_callback_data(CallbackData, prefix = "Durak game"):
    pass


def ttt_game_buttons(cbd:TTT_game_callback_data, field:str):
    kbd = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text = field[y*cbd.m + x],  callback_data = TTT_game_callback_data(lobby_id = cbd.lobby_id, X = x, Y = y, n = cbd.n, m = cbd.m, win_score = cbd.win_score).pack())\
          for x in range(cbd.m)] for y in range(cbd.n)
    ])

    return kbd

def finally_buttons():
    kbd = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text = "Завершить игру", callback_data = "end_game")
            ],
            [
                InlineKeyboardButton(text="Сыграть еще раз", callback_data="play_more")
            ]
        ]
    )

    return kbd