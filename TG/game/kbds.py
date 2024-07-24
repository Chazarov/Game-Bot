from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters.callback_data import CallbackData


# в game_configuration - конфигурацция параметров необходимая для определения выбранной игры
# их формирование описано в Game/Название_игры/strings.py
class GameStartParametrsCallback(CallbackData, prefix = "game"):
    game_name:str
    bet:int
    game_parametrs:str