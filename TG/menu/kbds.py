from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters.callback_data import CallbackData

from TG.game.TicTacToe.kbds import TTT_game_callback_data



def menu_buttons():
    kbd = InlineKeyboardMarkup(inline_keyboard = [
            [
                InlineKeyboardButton(text = "Играть 🎮", callback_data="games"),

            ],
            [
                InlineKeyboardButton(text="Пополнить баланс 💳", callback_data="balance"),
                InlineKeyboardButton(text="Вывести деньги 💳", callback_data="del_balance"),
            ],
            [
                InlineKeyboardButton(text="Cтатистика 👤", callback_data="stats"),
                InlineKeyboardButton(text="Рейтинг 🔝", callback_data="rating"),
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
                InlineKeyboardButton(text="Дурак онлайн (один на один) ♣️", callback_data="durak_game"),
            ],
            [
                InlineKeyboardButton(text = "Назад", callback_data="profile"),
            ],
        ]
    )
    return kbd

def backprof():
    kbd = InlineKeyboardMarkup(inline_keyboard = [
            [
                InlineKeyboardButton(text = "Назад", callback_data="profile"),
            ],
        ]
    )
    return kbd

def work_btn():
    kbd = InlineKeyboardMarkup(inline_keyboard = [
            [
                InlineKeyboardButton(text = "🎁 Создать промокод", callback_data="create_promo"),
            ],
            [
                InlineKeyboardButton(text="💰 Пополнить кошелёк", callback_data="create_bal"),
            ],
            [
                InlineKeyboardButton(text = "📥 Рассылка", callback_data="message_to_all"),
            ],
        ]
    )
    return kbd

def main_reply_buttoms(isWorker):
    if (isWorker):
        kbd = ReplyKeyboardMarkup(keyboard=[
                [
                    KeyboardButton(text="👤 Профиль"),
                ],
                [
                    KeyboardButton(text="⚡️ Воркер панель"),
                ],
            ], resize_keyboard=True)
    else:
        kbd = ReplyKeyboardMarkup(keyboard=[
                [
                    KeyboardButton(text="👤 Профиль"),
                ],
            ], resize_keyboard=True)
    return kbd

def choise_TTT_buttons():
    kbd = InlineKeyboardMarkup(inline_keyboard = [
            [
                InlineKeyboardButton(text = "Поля - 3x3 | Ставка - $25", callback_data = TTT_game_callback_data(field = "-", lobbi_id = 0, X = 0, Y = 0, n = 3, m = 3, win_score = 3, bet = 25).pack()),
            ],
            [
                InlineKeyboardButton(text = "Поля - 5x5 | Ставка - $50", callback_data = TTT_game_callback_data(field = "-", lobbi_id = 0, X = 0, Y = 0, n = 5, m = 5, win_score = 4, bet = 50).pack()),
            ],
            [
                InlineKeyboardButton(text="Поля - 10x10 | Ставка - $100", callback_data = TTT_game_callback_data(field = "-", lobbi_id = 0, X = 0, Y = 0, n = 10, m = 10, win_score = 5, bet = 100).pack()),
            ],
            [
                InlineKeyboardButton(text="Назад", callback_data="back_to_gameslist"),
            ],
        ]
    )
    return kbd