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

from TG.game.kbds import game_buttons, Game_callback_data



router = Router()


class Game_states(StatesGroup):
    Find_game = State()
    In_game = State()


@router.message(Command("start_game"))
async def start_game(message: types.Message, state:FSMContext, session:AsyncSession):
    
    message_id = message.message_id + 1
    bot = message.bot
    chat_id = message.from_user.id

    await state.set_state(Game_states.Find_game)

    timer_start = time.time()
    bar_count = 0
    opponent = None
    lobbi = None
    bar = "⚫️"
    while(1):
        bar_count+=1
        if(bar_count > 3): bar_count = 0
        bot.edit_message_text(text = \
            f"Идет поиск противника\n"+\
            f"Время ожидания: {int(time.time() - timer_start)}"
            f"    {bar*bar_count}              \n", chat_id = chat_id, message_id = message_id)
        
        lobbi = await orm_query.get_lobbi_by_user_id(session = session, user_id = chat_id)
        if(lobbi != None): break
        opponent = await orm_query.get_user_who_want_to_play(session = session)
        if(opponent != None): break

        if(time.time() - timer_start > system_parametrs.MAXIMUM_WAITING_TIME): break

    await orm_query.set_user_state(session = session, state = USER_STATES.IN_GAME)
    
    letter = ""#❌ или ⭕ в зависимости от того , за кого будет играть пользователь
    if(lobbi != None):
        opponent = await orm_query.get_user_by_id(session = session, user_id = opponent_id)

    elif(opponent != None):
        lobbi = await orm_query.create_lobbi(session = session, X_user_id = message.from_user.id, O_user_id = opponent.id)

        # Проверка для профилактики ошибки создания двух комнат(lobbi) с одним и тем же пользователем
        # (пользователь был приглашен в комнату другого игрока, пока для него создавалась собственная комната)
        another_lobbi = await orm_query.get_lobbi_by_user_id(session = session, user_id = chat_id)
        if(another_lobbi != None):
            await orm_query.close_lobbi(session = session, lobbi_id = lobbi.id)
            lobbi = another_lobbi
    else:
        return await bot.edit_message_text(text = f"К сожалению в лобби сейчас нет игроков 😢\nпопробуйте в следующий раз", chat_id = chat_id, message_id = message_id)
    
    if lobbi.X_user_id != chat_id:
        opponent_id = lobbi.X_user_id  
        letter = strings.SYMBOL_O
    else:
        opponent_id = lobbi.O_user_id
        letter = strings.SYMBOL_X

    field = f"{strings.SYMBOL_UNDEF}" * 9
    my_callback = Game_callback_data(lobbi_id = lobbi.id, opponent_id = opponent.id, field = field, X = 0, Y = 0, letter = letter)
    await bot.edit_message_text(text = f"Ваш противник: {opponent.name}  {opponent.tag}", chat_id = chat_id, message_id = message_id)
    await message.answer(text = f"Вы играете за {letter}", reply_markup = game_buttons(my_callback))