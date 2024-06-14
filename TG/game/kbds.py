from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters.callback_data import CallbackData


class Game_callback_data(CallbackData, prefix = "game"):
    opponent_id:int
    field:str
    X:int
    Y:int


def game_buttons(callback_data:Game_callback_data)