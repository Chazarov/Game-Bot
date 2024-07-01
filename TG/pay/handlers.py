import asyncio
import os
import random
import string
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
from .kbds import check_pay, add_bal_buttons
from .utils import is_number, getPayUrl, getInv, checkInvoice, is_int_num
from ..crypto_pay_api_sdk import cryptopay
from ..menu.handlers import id_generator
from ..menu.kbds import menu_buttons

router = Router()
Crypto = cryptopay.Crypto(token=os.getenv("CRYPTO_TOKEN"), testnet=False)

class pay_amount(StatesGroup):
    pay_summ = State()

class pay_vivod(StatesGroup):
    pay_summ = State()

class promo_state2(StatesGroup):
    code = State()

class rassilka(StatesGroup):
    text = State()




@router.callback_query(F.data == "del_balance")
async def start_command(callback: CallbackQuery, state: FSMContext, session:AsyncSession):
    user = await orm_query.get_user_by_id(session=session, user_id=callback.from_user.id)
    await callback.message.answer(f"<b>🏦 Введите сумму в USDT, которую вы хотите вывести</b>\n"
                                  f"💸 <b>Ваш баланс: {user.balance} USDT</b>", parse_mode='HTML')
    await state.set_state(pay_vivod.pay_summ)


@router.message(pay_vivod.pay_summ)
async def checkPay(message: types.Message, state: FSMContext, session:AsyncSession):
    summ = message.text
    await state.update_data(pay_summ=message.text)
    user = await orm_query.get_user_by_id(session=session, user_id=message.from_user.id)
    if is_int_num(summ):
        if user.balance>=int(summ):
            await orm_query.del_user_balance(session=session, user_id=message.from_user.id, amount=int(summ))
            uniq_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=15))
            print(Crypto.transfer(message.from_user.id, 'USDT', str(int(summ)), uniq_id))
            await message.answer(f"✅ <b>Успешный вывод на сумму {int(summ)}</b>", parse_mode='HTML')
            await state.clear()
        else:
            await message.answer("<b>❌ Недостаточно средств</b>", parse_mode='HTML')
            await state.clear()
    else:
        await message.answer("<b>❌ Неккоректный ввод</b>", parse_mode='HTML')
        await state.clear()


@router.callback_query(F.data == "balance")
async def start_command(callback: CallbackQuery, state: FSMContext):
    #await callback.message.answer("Введите сумму в USDT, на которую хотите пополнить баланс [MIN: 1.0]", parse_mode='HTML')
    await callback.message.edit_caption(f"<b>♻️ Выберите сумму для пополения</b>", parse_mode='HTML', reply_markup=add_bal_buttons())
    #await state.set_state(pay_amount.pay_summ)


@router.callback_query(F.data == "enter_promo")
async def start_command(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("🎁 <b>Введите промокод</b>", parse_mode='HTML')
    await state.set_state(pay_amount.pay_summ)

@router.message(pay_amount.pay_summ)
async def checkPay(message: types.Message, state: FSMContext, session:AsyncSession):
    promo = message.text
    await state.update_data(pay_summ=message.text)
    isValid = orm_query.get_promo_by_id(session=session, promo=promo)
    if isValid != None:
         promocode = await orm_query.get_promo_by_id(session=session, promo=promo)
         await message.answer(f"✅ Промкокод на сумму {promocode.amount} активирован")
         await orm_query.set_user_balance(session=session, user_id=message.from_user.id, amount=promocode.amount)
         await orm_query.delete_promo(session=session, promo=promo)
         await state.clear()
    else:
        await message.answer(f"❌ Неккоректный ввод", parse_mode='HTML')
        await state.clear()


@router.callback_query(lambda c: c.data and c.data.startswith('invoice#'))
async def balance(callback: CallbackQuery, state: FSMContext, session:AsyncSession):
    summ = callback.data.split('#')[1]
    await callback.message.delete()
    pay = Crypto.createInvoice("USDT", summ, params={"description": "Оплата игры", "expires_in": 60})

    invoiceID = getInv(str(pay))
    URL = getPayUrl(str(pay))

    # await message.answer(f"Ссылка на оплату: {URL}",parse_mode='HTML', reply_markup=check_pay(invoiceID))

    await callback.message.answer_photo(FSInputFile('Sourses/icon/icon1.png'), caption=f"💳 Оплата игры\n\n"
                                                                              f"Ваш айди: <code>{str(callback.from_user.id)}</code>\n"
                                                                              f"ID заказа: <b>{invoiceID}</b>\n"
                                                                              f"Сумма: <b>{summ} USDT</b>",
                               parse_mode='HTML', reply_markup=check_pay(invoiceID, URL))

@router.callback_query(lambda c: c.data and c.data.startswith('checkpay#'))
async def balance(callback: CallbackQuery, state: FSMContext, session:AsyncSession):
    minvoice = callback.data.split('#')[1]

    stats = checkInvoice(str(minvoice))

    if stats[0]=="True":
        await callback.answer(f"Оплата прошла, сумма {stats[1]}")
        await orm_query.set_user_balance(session=session, user_id=callback.from_user.id, amount=int(stats[1]))
        #await callback.message.delete()
        user = await orm_query.get_user_by_id(session=session, user_id=callback.from_user.id)
        await callback.message.edit_caption(caption=f"🖥 Личный кабинет\n\n"
                                                    f"Ваш айди: <code>{callback.from_user.id}</code>\n" +
                                                    f"Баланс: <b>{user.balance} USDT</b>\n" +
                                                    f"Дата регистрации: <b>{user.created}</b>", parse_mode='HTML',
                                            reply_markup=menu_buttons())
    else:
        await callback.answer("Оплата не прошла")

@router.callback_query(F.data == "create_promo")
async def start_command(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("💲 <b>Введите сумму промокода в USDT</b>", parse_mode='HTML')
    await state.set_state(promo_state2.code)


@router.message(promo_state2.code)
async def checkPay(message: types.Message, state: FSMContext, session:AsyncSession):
    await state.update_data(code=message.text)
    summ = message.text
    if is_int_num(summ) and int(summ)>0:
        promocode2 = id_generator()
        promo = await orm_query.add_promo(session=session, promo=promocode2, summa=int(summ))
        await message.answer(f"<b>Промокод </b> <code>{promocode2}</code> <b>на сумму {summ} USDT успешно создан</b>", parse_mode='HTML')
        await state.clear()
    else:
        await message.answer("❌ <b>Неккоректный ввод</b>", parse_mode='HTML')
        await state.clear()


@router.callback_query(F.data == "message_to_all")
async def start_command(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("<b>Введите сообщение для рассылки</b>", parse_mode='HTML')
    await state.set_state(rassilka.text)

@router.message(rassilka.text)
async def checkPay(message: types.Message, state: FSMContext, session:AsyncSession):
    await state.update_data(text=message.text)
    message_id = message.message_id
    text = message.text
    user_ids = await orm_query.get_ative_users(session=session)
    print(user_ids)
    bot = message.bot
    for i in range(len(user_ids)):
        user = await orm_query.get_user_by_id(session=session, user_id=user_ids[i])
        print(user.name, user.wins)

    for user_id in user_ids:
        try:
            await bot.send_message(user_id, text, parse_mode='HTML')
            print(f"Сообщение успешно отправлено пользователю {user_id}")
        except Exception as e:
            print(f"Ошибка при отправке сообщения пользователю {user_id}: {e}")
