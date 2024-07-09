from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters.callback_data import CallbackData

def check_pay(invoice,URL):
    kbd = InlineKeyboardMarkup(inline_keyboard = [
            [
                InlineKeyboardButton(text = "Оплатить", url=f"{URL}"),
                InlineKeyboardButton(text="Проверить оплату", callback_data=f"checkpay#{invoice}"),
            ],
            [
                InlineKeyboardButton(text="Отмена", callback_data=f"profile"),
            ],
        ]
    )

    return kbd

def add_main_bal(URL):
    kbd = InlineKeyboardMarkup(inline_keyboard = [
            [
                InlineKeyboardButton(text = "Оплатить", url=f"{URL}"),
            ],
        ]
    )

    return kbd

def add_bal_buttons():
    kbd = InlineKeyboardMarkup(inline_keyboard = [
            [
                InlineKeyboardButton(text="💸 25 USDT", callback_data=f"invoice#25"),
            ],
            [
                InlineKeyboardButton(text="💸 50 USDT", callback_data=f"invoice#50"),
            ],
            [
                InlineKeyboardButton(text="💸 100 USDT", callback_data=f"invoice#100"),
            ],
            [
                InlineKeyboardButton(text="🎁 Ввести промокод", callback_data=f"enter_promo"),
            ],
        ]
    )

    return kbd