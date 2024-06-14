import time

from aiogram import F, types, Router, Dispatcher
from aiogram.filters import Command, StateFilter
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import FSInputFile, InputMediaPhoto
from aiogram.fsm.context import FSMContext

from sqlalchemy.ext.asyncio import AsyncSession

from Database import orm_query
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
    bar = "⚫️"
    while(1):
        bar_count+=1
        if(bar_count > 3): bar_count = 0
        bot.edit_message_text(text = \
            f"Идет поиск противника\n"+\
            f"Время ожидания: {int(time.time() - timer_start)}"
            f"    {bar*bar_count}              \n", chat_id = chat_id, message_id = message_id)
        
        opponent = await orm_query.get_user_who_want_to_play(session = session)
        if(opponent != None): break

        if(time.time() - timer_start > system_parametrs.MAXIMUM_WAITING_TIME): break

    if(opponent != None):
        bot.edit_message_text(text = \
            f"Ваш противник: {opponent.name}  {opponent.tag}", chat_id = chat_id, message_id = message_id)
    else:
        bot.edit_message_text(text = \
            f"К сожалению в лобби сейчас нет игроков 😢\nпопробуйте в следующий раз", chat_id = chat_id, message_id = message_id)
    
    
    if(opponent): 
        field = f"{strings.SYMBOL_O}" * 9
        callback = Game_callback_data(opponent_id = opponent.id, field = field, X = 0, Y = 0)
        message.answer("", reply_markup=game_buttons())