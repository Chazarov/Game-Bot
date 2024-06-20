from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters.callback_data import CallbackData

from TG.game.kbds import Game_callback_data


def menu_buttons():
    kbd = InlineKeyboardMarkup(inline_keyboard = [
            [
                InlineKeyboardButton(text = "Играть🎮", callback_data="games"),
                InlineKeyboardButton(text="Пополнить баланс💳", callback_data="balance"),
            ],
            [
                InlineKeyboardButton(text = "Профиль👤", callback_data="chk"),
            ],
        ]
    )
    return kbd

def choise_game_buttons():
    kbd = InlineKeyboardMarkup(inline_keyboard = [
            [
                InlineKeyboardButton(text = "Крестики нолики ❌", callback_data="ttt_game"),
            ],
            [
                InlineKeyboardButton(text = "Назад", callback_data="profile"),
            ],
        ]
    )
    return kbd

def choise_TTT_buttons():
    kbd = InlineKeyboardMarkup(inline_keyboard = [
            [
                InlineKeyboardButton(text = "Поля - 3x3 | Ставка - $25", callback_data = Game_callback_data(field = "-", lobbi_id = 0, X = 0, Y = 0, n = 3, m = 3, bet = 25).pack()),
            ],
            [
                InlineKeyboardButton(text = "Поля - 5x5 | Ставка - $50", callback_data = Game_callback_data(field = "-", lobbi_id = 0, X = 0, Y = 0, n = 5, m = 5, bet = 50).pack()),
            ],
            [
                InlineKeyboardButton(text="Поля - 10x10 | Ставка - $100", callback_data = Game_callback_data(field = "-", lobbi_id = 0, X = 0, Y = 0, n = 10, m = 10, bet = 100).pack()),
            ],
            [
                InlineKeyboardButton(text="Назад", callback_data="back_to_gameslist"),
            ],
        ]
    )
    return kbd