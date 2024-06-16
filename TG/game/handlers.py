import asyncio
import time

from aiogram import F, types, Router, Dispatcher
from aiogram.filters import Command, StateFilter
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import FSInputFile, InputMediaPhoto
from aiogram.fsm.context import FSMContext

from sqlalchemy.ext.asyncio import AsyncSession

from Database import orm_query
from Database.models import USER_STATES
from TG import system_parametrs

from Game import strings
from Game import game

from TG.game.kbds import game_buttons, finally_buttons, Game_callback_data



router = Router()


class Game_states(StatesGroup):
    Find_game = State()
    In_game = State()


@router.message(Command("start_game"), StateFilter(None))
async def start_game(message: types.Message, state:FSMContext, session:AsyncSession):
    
    is_creator:bool

    message_id = message.message_id + 1
    bot = message.bot
    chat_id = message.from_user.id

    await state.set_state(Game_states.Find_game)
    await orm_query.set_user_state(session = session, user_id = chat_id, state = USER_STATES.WAITING_FOR_A_GAME)
    await message.answer("...")

    timer_start = time.time()
    waiting_time = 0
    bar_count = 0
    opponent = None
    lobbi = None
    bar = "⚫️"



    while(1):
        bar_count+=1
        waiting_time = int(time.time() - timer_start)
        
        if(bar_count > 3): bar_count = 0
        
        await bot.edit_message_text(text = \
            f"Идет поиск противника\n"+\
            f"Время ожидания: {waiting_time}\n"
            f"|    {bar*bar_count}              \n", chat_id = chat_id, message_id = message_id)
        
        if(waiting_time%system_parametrs.WAITING_UPDATE_TIME == 0):
            lobbi = await orm_query.get_lobbi_by_invitation(session = session, guest_id = chat_id)
            if(lobbi != None): break
            opponent = await orm_query.get_user_who_want_to_play(session = session, ignore_user_id = chat_id)
            if(opponent != None): break

        if(time.time() - timer_start > system_parametrs.MAXIMUM_WAITING_TIME): break
        await asyncio.sleep(1)

    await orm_query.set_user_state(session = session, user_id = chat_id, state = USER_STATES.IN_GAME)
    await state.set_state(Game_states.In_game)


    # Проверка для профилактики ошибки создания двух комнат(lobbi) с одним и тем же пользователем
    # (пользователь был приглашен в комнату другого игрока, пока для него создавалась собственная комната)
    another_lobbi = await orm_query.get_lobbi_by_invitation(session = session, guest_id = chat_id)
    if(another_lobbi != None):
        letter = strings.SYMBOL_O
        lobbi = another_lobbi
    
    letter = ""#❌ или ⭕ в зависимости от того , за кого будет играть пользователь
    if(lobbi != None):
        is_creator = False

        letter = strings.SYMBOL_O

        opponent_id = lobbi.creator_id
        opponent = await orm_query.get_user_by_id(session = session, user_id = opponent_id)

    elif(opponent != None):
        is_creator = True

        lobbi = await orm_query.create_lobbi(session = session, X_user_id = message.from_user.id, O_user_id = opponent.id)
        letter = strings.SYMBOL_X
            
    else:
        await orm_query.set_user_state(session = session, user_id = chat_id, state = USER_STATES.NOT_ACTIVE)
        return await bot.edit_message_text(text = f"К сожалению в лобби сейчас нет игроков 😢\nпопробуйте еще раз позже", chat_id = chat_id, message_id = message_id)
    

    op_tag = opponent.tag
    if(op_tag == None): op_tag = ""
    else: op_tag = "@" + op_tag

    await bot.edit_message_text(text = f"Ваш противник: {opponent.name}  {op_tag}", chat_id = chat_id, message_id = message_id)

    send_message = await message.answer("...")
    if(not is_creator):
        await orm_query.add_in_lobbi_guest_field_message_id(session = session, lobbi_id = lobbi.id, field_message_id = send_message.message_id)
    else:
        await orm_query.add_in_lobbi_creator_field_message_id(session = session, lobbi_id = lobbi.id, field_message_id = send_message.message_id)

    opponent_field_message_id = None
    try_count = 0
    while(opponent_field_message_id == None):
        lobbi = await orm_query.get_lobbi_by_id(session = session, lobbi_id = lobbi.id)
        await session.refresh(lobbi)
        if(is_creator):
            opponent_field_message_id = lobbi.guest_field_message_id
            opponent_id = lobbi.guest_id
        else:
            opponent_field_message_id = lobbi.creator_field_message_id
            opponent_id = lobbi.creator_id

        try_count += 1
        await asyncio.sleep(system_parametrs.WAITING_UPDATE_TIME)
        if(try_count > system_parametrs.MAXIMUM_TRY_COUNT):
            return await bot.edit_message_text(text = f"Соединение с игроком не состоялось(\nПопробуйте еще раз", chat_id = chat_id, message_id = send_message.message_id)


    await state.update_data(letter = letter)
    await state.update_data(opponent_field_message_id = opponent_field_message_id)
    await state.update_data(opponent_id = opponent_id)
    field = f"{strings.SYMBOL_UNDEF}" * 9
    await bot.edit_message_text(text = f"Вы играете за {letter}", reply_markup = game_buttons(lobbi_id = lobbi.id, field = field, n = 3, m = 3), chat_id = chat_id, message_id = send_message.message_id)
    


@router.callback_query(Game_callback_data.filter(), Game_states.In_game)
async def game_playing_callback(callback:types.CallbackQuery, callback_data:Game_callback_data, state:FSMContext, session:AsyncSession):

    state_data = await state.get_data()
    field = [callback_data.field[3*i:][:3] for i in range(3)]
    cbd = callback_data
    bot = callback.bot

    letter = state_data["letter"]
    opponent_field_message_id = state_data["opponent_field_message_id"]
    opponent_id = state_data["opponent_id"]

    if(not game.can_walk(symbol = letter, field = callback_data.field)):
        return await callback.answer("Сейчас не ваш ход🚫")
    
    if(field[cbd.Y][cbd.X] != strings.SYMBOL_UNDEF):
        return await callback.answer("Вы не можете так сходить!")
    
    field[cbd.Y] = field[cbd.Y][:cbd.X] + letter + field[cbd.Y][cbd.X + 1:]

    await callback.message.edit_reply_markup(reply_markup = game_buttons(lobbi_id = cbd.lobbi_id, field = "".join(field), n = 3, m = 3))
    await bot.edit_message_reply_markup(chat_id = opponent_id, message_id = opponent_field_message_id, \
                                        reply_markup = game_buttons(lobbi_id = cbd.lobbi_id, field = "".join(field), n = 3, m = 3))
    
    result = game.is_win(FIELD = field, win_score = 3)
    
    if(result == 'ничья'):
        await orm_query.set_user_state(session = session, user_id = callback.from_user.id, state = USER_STATES.NOT_ACTIVE)
        await orm_query.close_lobbi(session = session, lobbi_id = cbd.lobbi_id)

        await bot.edit_message_text(text =\
        f"у вас ничья", chat_id = opponent_id, message_id = opponent_field_message_id, reply_markup = finally_buttons())

        return await callback.message.edit_text(text =\
        f"у вас ничья", reply_markup = finally_buttons())
    elif(result == letter):
        await orm_query.set_user_state(session = session, user_id = callback.from_user.id, state = USER_STATES.NOT_ACTIVE)
        await orm_query.close_lobbi(session = session, lobbi_id = cbd.lobbi_id)

        await bot.edit_message_text(text =\
        f"Вы проиграли 😔", chat_id = opponent_id, message_id = opponent_field_message_id, reply_markup = finally_buttons())

        return await callback.message.edit_text(text =\
        f"Победа!🏆\n", reply_markup = finally_buttons())
    


@router.callback_query(F.data == "end_game", Game_states.In_game)
async def end_game(callback:types.CallbackQuery, state:FSMContext):
    await state.clear()
    await callback.message.edit_reply_markup(reply_markup = None)

        


