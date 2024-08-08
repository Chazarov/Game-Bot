import os
import random
import string

from aiogram import F, types, Router, Dispatcher
from aiogram.filters import Command, StateFilter
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import FSInputFile, InputMediaPhoto, CallbackQuery
from aiogram.fsm.context import FSMContext

from sqlalchemy.ext.asyncio import AsyncSession

from Database import orm_query
from TG.menu.kbds import menu_buttons, choise_game_buttons, choise_TTT_buttons, main_reply_buttoms, work_btn, backprof, start_game_buttons
from TG.pay.utils import is_int_num, Crypto

ADMINID = os.getenv("ADMIN_ID")



router = Router()
router.message.filter(StateFilter(None))

def id_generator(size=10, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


@router.message(F.text == "👤 Профиль")
@router.message(Command("start"))
async def command_start(message: types.Message, session:AsyncSession):
    user_id = message.from_user.id
    user = await orm_query.get_user_by_id(session = session, user_id = user_id)
    if(user == None):
        tag = message.from_user.username
        user = await orm_query.add_user(session = session, user_id = user_id, name = message.from_user.first_name, tag = tag)
    if message.from_user.id==ADMINID:
        isWorker = True
    else:
        isWorker = False
    await message.answer("<b>Главное меню</b>",parse_mode='HTML', reply_markup=main_reply_buttoms(isWorker=isWorker))
    await message.answer_photo(FSInputFile('Sourses/icon/icon1.png'), caption=f"🖥 Личный кабинет\n\n" + 
                                                                        f"Ваш айди: <code>{message.from_user.id}</code>\n" +
                                                                        f"Баланс: <b>{user.balance} USDT</b>\n" +
                                                                        f"Дата регистрации: <b>{user.created}</b>", parse_mode='HTML', reply_markup=menu_buttons())


@router.callback_query(F.data == "profile")
async def command_profile(callback: CallbackQuery, session:AsyncSession):
    user = await orm_query.get_user_by_id(session=session, user_id=callback.from_user.id)
    await callback.message.edit_caption(caption=f"🖥 Личный кабинет\n\n"
                                                                        f"Ваш айди: <code>{callback.from_user.id}</code>\n" +
                                                                        f"Баланс: <b>{user.balance} USDT</b>\n" +
                                                                        f"Дата регистрации: <b>{user.created}</b>", parse_mode='HTML', reply_markup=menu_buttons())

@router.callback_query(F.data == "stats")
async def command_statistic(callback: CallbackQuery, session:AsyncSession):
    user = await orm_query.get_user_by_id(session=session, user_id=callback.from_user.id)
    await callback.message.edit_caption(caption=f"👤 <b>Статистика</b>\n\n"
                                                    f"📊 <b>Всего игр: {user.wins+user.loses}</b>\n"
                                                    f"🎉 <b>Побед: {user.wins}\n</b>"
                                                    f"💢 <b>Поражений: {user.loses}</b>", parse_mode='HTML', reply_markup=backprof())

@router.callback_query(F.data == "rating")
async def command_rating(callback: CallbackQuery, session:AsyncSession):
    user = await orm_query.get_user_by_id(session=session, user_id=callback.from_user.id)
    text = f"<b>🔝 Рейтинг\n\n</b>"

    user_ids = await orm_query.get_ative_users(session=session)
    for i in range(len(user_ids)):
        user = await orm_query.get_user_by_id(session=session, user_id=user_ids[i])
        text = text + f"<b>{i+1}) {user.name} | Побед: <code>{user.wins}</code> | Поражений: <code>{user.loses}</code>\n</b>"
        if i==10:
            break
    await callback.message.edit_caption(caption=text, parse_mode='HTML', reply_markup=backprof())

@router.callback_query(F.data == "back_to_gameslist")
@router.callback_query(F.data == "games")
async def command_profile(callback: CallbackQuery, session:AsyncSession):
    await callback.message.edit_caption(caption=f"🎮 Выберите игру",
                               parse_mode='HTML', reply_markup=choise_game_buttons())





#Здесь меняется состояние и в данные FSMContext добавляется название игры , по которому далее будет происходить фильтрация 
# и разделение хендлеров на придожения различных игр (фильтр смотреть в TG/Gm)
@router.callback_query(F.data == "ttt_game")
async def choise_TTT_game(callback: CallbackQuery, session:AsyncSession, state:FSMContext):
    await callback.message.edit_caption(caption=f"🎮 Выберите параметры",
                               parse_mode='HTML', reply_markup = choise_TTT_buttons())

@router.callback_query(F.data == "durak_game")
async def choise_Durak_game(callback: CallbackQuery, session:AsyncSession):
   await callback.message.edit_caption(caption = "Дурак", reply_markup = start_game_buttons())
  




@router.message(F.text == "⚡️ Воркер панель")
async def start_command(message: types.Message, session:AsyncSession, command:Command = None):
    if message.from_user.id == ADMINID:
        user_ids = await orm_query.get_ative_users(session=session)
        amount = Crypto.getBalance()
        usdt_available = next(item['available'] for item in amount['result'] if item['currency_code'] == 'USDT')
        await message.answer_photo(FSInputFile('Sourses/icon/icon1.png'),f"<b>⚙️ Настройки</b>\n"
                                                                         f"<b>📊 Всего пользователей:</b> <code>{len(user_ids)}\n</code>"
                                                                         f"<b>💰 Баланс основного кошелька:</b> <code>{usdt_available} USDT</code>", parse_mode='HTML', reply_markup=work_btn())


router.callback_query.register(choise_TTT_game, F.data == "ttt_game")