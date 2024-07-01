from aiogram import F, types, Router, Dispatcher
from aiogram.filters import Command, StateFilter
from aiogram.types import FSInputFile, InputMediaPhoto, CallbackQuery
from aiogram.fsm.context import FSMContext

from sqlalchemy.ext.asyncio import AsyncSession

from Database import orm_query
from TG.menu.kbds import menu_buttons, choise_game_buttons, choise_TTT_buttons

router = Router()
router.message.filter(StateFilter(None))



@router.message(Command("start"))
async def command_start(message: types.Message, session:AsyncSession):
    user_id = message.from_user.id
    user = await orm_query.get_user_by_id(session = session, user_id = user_id)
    if(user == None):
        tag = message.from_user.username
        user = await orm_query.add_user(session = session, user_id = user_id, name = message.from_user.first_name, tag = tag)

    await message.answer_photo(FSInputFile('Sourses/icon/icon1.png'), caption=f"🖥 Личный кабинет\n\n" + 
                                                                        f"Ваш айди: <code>{message.from_user.id}</code>\n" +
                                                                        f"Баланс: <b>  {user.balance} $</b>\n" + 
                                                                        f"Дата регистрации: <b>{user.created}</b>", parse_mode='HTML', reply_markup=menu_buttons())


@router.callback_query(F.data == "profile")
async def command_profile(callback: CallbackQuery, session:AsyncSession):
    await callback.message.edit_caption(caption=f"🖥 Личный кабинет\n\n"
                                                                              f"Ваш айди: <code>---callback.message.from_user.id---</code>\n"
                                                                              f"Баланс: <b>---0.00 RUB---</b>\n"
                                                                              f"Дата регистрации: <b>19/06/2024</b>",
                               parse_mode='HTML', reply_markup=menu_buttons())
    
@router.callback_query(F.data == "back_to_gameslist")
@router.callback_query(F.data == "games")
async def command_profile(callback: CallbackQuery, session:AsyncSession):
    await callback.message.edit_caption(caption=f"🎮 Выберите игру",
                               parse_mode='HTML', reply_markup=choise_game_buttons())

@router.callback_query(F.data == "ttt_game")
async def command_profile(callback: CallbackQuery, session:AsyncSession):
    await callback.message.edit_caption(caption=f"🎮 Выберите параметры",
                               parse_mode='HTML', reply_markup=choise_TTT_buttons())