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