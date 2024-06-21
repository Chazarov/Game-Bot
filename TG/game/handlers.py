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

async def delete_menu(callback:types.CallbackQuery):
    await callback.message.delete()

async def start_game(callback:types.CallbackQuery, callback_data:Game_callback_data, state:FSMContext, session:AsyncSession):

    
    
    message = callback.message
    chat_id = callback.from_user.id
    bot = message.bot
    is_creator:bool
    game_parametrs = game.make_game_parametrs(n = callback_data.n, m = callback_data.m, win_score = callback_data.win_score, bet = callback_data.bet)

    
    await state.set_state(Game_states.Find_game)
    await orm_query.set_user_state(session = session, user_id = chat_id, state = USER_STATES.WAITING_FOR_A_GAME, find_game_parametrs = game_parametrs)
    send_message = await message.answer(text = \
            f"Идет поиск противника\n"+\
            f"Время ожидания: {0}\n"
            f"|                 \n")
    message_id = send_message.message_id
    await delete_menu(callback = callback)

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
            opponent = await orm_query.get_user_who_want_to_play(session = session, ignore_user_id = chat_id, game_params = game_parametrs)
            if(opponent != None): break

        if(time.time() - timer_start > system_parametrs.MAXIMUM_WAITING_TIME): break
        await asyncio.sleep(1)

    await orm_query.set_user_state(session = session, user_id = chat_id, state = USER_STATES.IN_GAME)
    await state.set_state(Game_states.In_game)

    try:
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
            letter = strings.SYMBOL_X

            lobbi = await orm_query.create_lobbi(session = session, creator_id = chat_id, guest_id = opponent.id)
            
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
                await state.clear()
                await orm_query.set_user_state(session = session, user_id = chat_id, state = USER_STATES.NOT_ACTIVE)
                await orm_query.close_lobbi(session = session, lobbi_id = lobbi.id)
                return await bot.edit_message_text(text = f"Соединение с игроком не состоялось(\nПопробуйте еще раз", chat_id = chat_id, message_id = send_message.message_id)

        field = f"{strings.SYMBOL_UNDEF}" * callback_data.n*callback_data.m

        await state.update_data(letter = letter)
        await state.update_data(opponent_field_message_id = opponent_field_message_id)
        await state.update_data(opponent_id = opponent_id)
        await orm_query.set_field_in_lobbi(session = session, lobbi = lobbi, field = field)
        callback_data.lobbi_id = lobbi.id
        await bot.edit_message_text(text = f"Вы играете за {letter}", reply_markup = game_buttons(callback_data = callback_data, field = field), chat_id = chat_id, message_id = send_message.message_id)
    
    except Exception as e: 
        print(e)
        if(lobbi != None):
            await orm_query.close_lobbi(session = session, lobbi_id = lobbi.id)
        await state.clear()
        await orm_query.set_user_state(session = session, user_id = chat_id, state = USER_STATES.NOT_ACTIVE)
        return await bot.edit_message_text(text = f"Ошибка подключения (\nПопробуйте еще раз позже", chat_id = chat_id, message_id = send_message.message_id)


async def game_playing_callback(callback:types.CallbackQuery, callback_data:Game_callback_data, state:FSMContext, session:AsyncSession):

    async def end_game():
        await orm_query.set_user_state(session = session, user_id = callback.from_user.id, state = USER_STATES.NOT_ACTIVE)
        await orm_query.set_user_state(session = session, user_id = opponent_id, state = USER_STATES.NOT_ACTIVE)
        await orm_query.close_lobbi(session = session, lobbi_id = cbd.lobbi_id)

    state_data = await state.get_data()
    cbd = callback_data
    bot = callback.bot

    lobbi = await orm_query.get_lobbi_by_id(session = session, lobbi_id = cbd.lobbi_id)
    field = [lobbi.field[cbd.n*i:][:cbd.m] for i in range(cbd.n)]
    letter = state_data["letter"]
    opponent_field_message_id = state_data["opponent_field_message_id"]
    opponent_id = state_data["opponent_id"]

    if(not game.can_walk(symbol = letter, field = lobbi.field)):
        return await callback.answer("Сейчас не ваш ход🚫")
    
    if(field[cbd.Y][cbd.X] != strings.SYMBOL_UNDEF):
        return await callback.answer("Вы не можете так сходить!")
    
    field[cbd.Y] = field[cbd.Y][:cbd.X] + letter + field[cbd.Y][cbd.X + 1:]

    field = "".join(field)

    await orm_query.set_field_in_lobbi(session = session, lobbi = lobbi, field = field)
    await callback.message.edit_reply_markup(reply_markup = game_buttons(callback_data = cbd, field = field))
    await bot.edit_message_reply_markup(chat_id = opponent_id, message_id = opponent_field_message_id, \
                                        reply_markup = game_buttons(callback_data = cbd, field = field))
    
    result = game.is_win(FIELD = field, win_score = cbd.win_score)
    
    if(result == 'ничья'):
        await bot.edit_message_text(text =\
        f"у вас ничья", chat_id = opponent_id, message_id = opponent_field_message_id, reply_markup = finally_buttons())

        await callback.message.edit_text(text =\
        f"у вас ничья", reply_markup = finally_buttons())
        await end_game()
    elif(result == letter):
        await bot.edit_message_text(text =\
        f"Вы проиграли 😔", chat_id = opponent_id, message_id = opponent_field_message_id, reply_markup = finally_buttons())

        await callback.message.edit_text(text =\
        f"Победа!🏆\n", reply_markup = finally_buttons())

        await end_game()


@router.callback_query(F.data == "end_game", Game_states.In_game)
async def end_game(callback:types.CallbackQuery, state:FSMContext):
    await state.clear()
    await callback.message.edit_reply_markup(reply_markup = None)

        

router.callback_query.register(start_game, Game_callback_data.filter(), StateFilter(None))
router.callback_query.register(game_playing_callback, Game_callback_data.filter(), Game_states.In_game)

