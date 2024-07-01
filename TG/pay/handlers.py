import asyncio
import os
import time

from aiogram import F, types, Router, Dispatcher
from aiogram.filters import Command, StateFilter
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import FSInputFile, InputMediaPhoto, CallbackQuery
from aiogram.fsm.context import FSMContext

from sqlalchemy.ext.asyncio import AsyncSession

from Database import orm_query
from Database.models import USER_STATES
from TG import system_parametrs
from .kbds import check_pay
from .utils import is_number, getPayUrl, getInv, checkInvoice
from ..crypto_pay_api_sdk import cryptopay

router = Router()
Crypto = cryptopay.Crypto(token=os.getenv("CRYPTO_TOKEN"), testnet=False)

class pay_amount(StatesGroup):
    pay_summ = State()


@router.callback_query(F.data == "balance")
async def start_command(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Введите сумму в USDT, на которую хотите пополнить баланс [MIN: 1.0]", parse_mode='HTML')
    await state.set_state(pay_amount.pay_summ)

@router.message(pay_amount.pay_summ)
async def checkPay(message: types.Message, state: FSMContext):
    summ = message.text
    if is_number(summ) and float(summ)>0.9:
        await state.update_data(pay_summ=message.text)

        pay = Crypto.createInvoice("USDT", summ, params={"description": "Оплата игры","expires_in": 60})

        invoiceID = getInv(str(pay))
        URL = getPayUrl(str(pay))


        #await message.answer(f"Ссылка на оплату: {URL}",parse_mode='HTML', reply_markup=check_pay(invoiceID))

        await message.answer_photo(FSInputFile('Sourses/icon/icon1.png'),caption=f"💳 Оплата игры\n\n"
                                f"Ваш айди: <code>{str(message.from_user.id)}</code>\n"
                                f"ID заказа: <b>{invoiceID}</b>\n"
                                f"Сумма: <b>{summ} USDT</b>",
                                parse_mode='HTML', reply_markup=check_pay(invoiceID, URL))
        await state.clear()
    else:
        await message.answer(f"Неккоректная сумма", parse_mode='HTML')

@router.callback_query(lambda c: c.data and c.data.startswith('checkpay#'))
async def balance(callback: CallbackQuery, state: FSMContext):
    minvoice = callback.data.split('#')[1]

    stats = checkInvoice(str(minvoice))

    if stats[0]=="True":
        await callback.answer(f"Оплата прошла, сумма {stats[1]}")
    else:
        await callback.answer("Оплата не прошла")
