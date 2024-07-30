import asyncio

from aiogram import F, types, Router, Dispatcher, Bot
from aiogram.filters import Command, StateFilter
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import FSInputFile, InputMediaPhoto
from aiogram.fsm.context import FSMContext

from sqlalchemy.ext.asyncio import AsyncSession

from Database.models import USER_STATES, User, Lobby
from Database import orm_query

from TG import system_parametrs
from TG.game.filters import CurrentGameFilter

from Game.Durak import strings

router = Router()

router.message.filter(CurrentGameFilter(game_name = strings.GAME_NAME))
router.callback_query.filter(CurrentGameFilter(game_name = strings.GAME_NAME))


async def start_game(bot:Bot, message:types.Message, state:FSMContext, session:AsyncSession, start_game_parametrs:str, is_creator:bool, lobby:Lobby, message_to_display_id:int, opponent:User, chat_id:int):
    
    lobby = await orm_query.get_lobby_by_id(session = session, lobby_id = lobby.id)
    game = await orm_query.get_game_by_id(session = session, game_name = strings.GAME_NAME, game_id = lobby.game_id)
    op_tag = opponent.tag if opponent.tag == None else "@" + opponent.tag


    message_to_display_1 = await bot.send_message(text = f"Ваш противник: {opponent.name}  {op_tag}", chat_id = chat_id)
    
    

    if(not is_creator):
        await game.set_display_messages_creator(session = session, message1 = message_to_display_1, message2 = message_to_display_2, message3 = message_to_display_3)
    else:
        await game.set_display_messages_guest(session = session, message1 = message_to_display_1, message2 = message_to_display_2, message3 = message_to_display_3)

    # Ожидание заполнения параметров лобби со стороны противника
    fields_are_filled_in = False
    try_count = 0
    while(not filleds_are_filled_in):
        await session.refresh(game) # Обновление сессии для получения актуальный на данный момент информации
        await session.refresh(lobby)
        if(is_creator):
            filleds_are_filled_in = game.guest_fields_are_filled_in
        else:
            filleds_are_filled_in = game.creator_fields_are_filled_in

        try_count += 1
        await asyncio.sleep(system_parametrs.WAITING_UPDATE_TIME)
        if(try_count > system_parametrs.MAXIMUM_TRY_COUNT):
            await state.clear()
            await orm_query.set_user_state(session = session, user_id = chat_id, state = USER_STATES.NOT_ACTIVE)
            await lobby.delete()
            return await bot.edit_message_text(text = f"Соединение с игроком не состоялось(\nПопробуйте еще раз", chat_id = chat_id, message_id = message_to_display_1)



    # Разделение на мини-игры происходит через поле game_name в FSMContext. Данный Фильтр определен в TG/game/filters.py
    # и используется во всех хендлерах, ответственных за непосредственный игровой процесс
    await state.update_data(game_name = strings.GAME_NAME)

    

    message_to_display_2 = await bot.send_message(text = "...", chat_id = chat_id)
    message_to_display_3 = await bot.send_message(text = "...", chat_id = chat_id)
    message_to_display_4 = await bot.send_message(text = "...", chat_id = chat_id)







