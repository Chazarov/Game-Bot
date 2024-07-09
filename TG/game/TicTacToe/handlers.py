from aiogram import F, types, Router
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import FSInputFile
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from Database import orm_query
from Database.models import USER_STATES

from Game.TTT import strings
from Game.TTT import game

from TG.game.filters import CurrentGameFilter

from TG.game.TicTacToe.kbds import ttt_game_buttons, finally_buttons, TTT_game_callback_data
from TG.menu.kbds import choise_TTT_buttons
from TG.pay.kbds import check_pay
from TG.pay.utils import getInv, getPayUrl


#Сменить инициализацию роутера и использование (убрать декораторы, инициализировать роутер после функций)
router = Router()

router.message.filter(CurrentGameFilter(strings.GAME_NAME))
router.callback_query.filter(CurrentGameFilter(strings.GAME_NAME))


#Фильтрация хендлеров происходит через поле game_name в хранилище state.data (фильтр описан в TG/game/filters.py)так state
# задается в меню сразу после выбора параметров игры 

class Game_states(StatesGroup):
    Find_game = State()
    In_game = State()




# Точка входа в игру. В этой функции задаются основные параметры игры, выстраивается поле и меняются состояния
# пользователя как внутри базы данных так и в state (FSMContext)
async def start_game():

    pass

async def TTT_playing_callback(callback:types.CallbackQuery, callback_data:TTT_game_callback_data, state:FSMContext, session:AsyncSession):

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

    field_line = "".join(field)

    await orm_query.set_field_in_lobbi(session = session, lobbi = lobbi, field = field_line)
    await callback.message.edit_reply_markup(reply_markup = ttt_game_buttons(callback_data = cbd, field = field_line))
    await bot.edit_message_reply_markup(chat_id = opponent_id, message_id = opponent_field_message_id, \
                                        reply_markup = ttt_game_buttons(callback_data = cbd, field = field_line))
    
    result = game.is_win(FIELD = field, win_score = cbd.win_score)

    print("\n".join(field) + "\n\n" + str(cbd.win_score) + "\n ==> " + str(result) + "\n")
    
    if(result == 'ничья'):
        await bot.edit_message_text(text =\
        f"у вас ничья", chat_id = opponent_id, message_id = opponent_field_message_id, reply_markup = finally_buttons())

        await callback.message.edit_text(text =\
        f"у вас ничья", reply_markup = finally_buttons())
        await end_game()

    elif(result == letter):
        await bot.edit_message_text(text =\
        f"Вы проиграли 😔", chat_id = opponent_id, message_id = opponent_field_message_id, reply_markup = finally_buttons())

        await orm_query.del_user_balance(session=session, user_id=opponent_id, amount=int(callback_data.bet))
        await orm_query.add_lose(session=session, user_id=opponent_id)

        await orm_query.set_user_balance(session=session, user_id=callback.from_user.id, amount=int(float(callback_data.bet)*1.7))
        await orm_query.add_win(session=session, user_id=callback.from_user.id)


        await callback.message.edit_text(text= \
                                             f"Победа!🏆\n"
                                             f"Ваш выигрыш: {str(float(callback_data.bet) * 1.7)} USDT",
                                         reply_markup=finally_buttons())

        await end_game()


@router.callback_query(F.data == "end_game", Game_states.In_game)
async def end_game(callback:types.CallbackQuery, state:FSMContext):
    await state.clear()
    await callback.message.edit_reply_markup(reply_markup = None)

#Нужно ограничить этот каллбек(чтобы кнопка никак не могла появиться во время игрового процесса)
@router.callback_query(F.data == "play_more", Game_states.In_game)
async def play_more(callback:types.CallbackQuery, state:FSMContext):
    await state.clear()
    await callback.message.edit_reply_markup(reply_markup = None)
    await callback.message.delete()

    await callback.message.answer_photo(FSInputFile('Sourses/icon/icon1.png'),f"🎮 Выберите параметры",
                               parse_mode='HTML', reply_markup=choise_TTT_buttons())

        

router.callback_query.register(TTT_playing_callback, TTT_game_callback_data.filter(), Game_states.In_game)

