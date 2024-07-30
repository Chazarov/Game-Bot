import asyncio

from aiogram import F, types, Router, Bot
from aiogram.fsm.state import StatesGroup, State
from aiogram.filters import StateFilter
from aiogram.types import FSInputFile
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from TG import system_parametrs

from Database import orm_query
from Database.models import USER_STATES, User, Lobby

from Game.TTT import strings
from Game.TTT import game

from TG.game.filters import CurrentGameFilter

from TG.game.TicTacToe.kbds import ttt_game_buttons, finally_buttons, TTT_game_callback_data
from TG.menu.kbds import choise_TTT_buttons
from TG.pay.kbds import check_pay
from TG.pay.utils import getInv, getPayUrl

from TG.game.filters import Game_states


#Сменить инициализацию роутера и использование (убрать декораторы, инициализировать роутер после функций)
router = Router()

router.message.filter(CurrentGameFilter(strings.GAME_NAME), StateFilter(Game_states.In_game))
router.callback_query.filter(CurrentGameFilter(strings.GAME_NAME), StateFilter(Game_states.In_game))


#Фильтрация хендлеров происходит через поле game_name в хранилище state.data (фильтр описан в TG/game/filters.py)так state
# задается в меню сразу после выбора параметров игры 


#     1) В объекте комнаты (база данных):
# поле (так как в объектах, наследуемых от Callback_data, ограничение на размер данных).
#     2) В данных машины состояний (FSMcontest) (оперативная память FSM):
# id противника,
# id сообщения, которое является игровым полем у противника,
# letter - обозначает, за кого играет пользователь (SYMBOL_X или SYMBOL_Y, определенные в Game/TinTacToe/strings.py).
#     3) В объекте класса Callback_data (TTT_game_callback_data, см. в TG/game/TicTacToe/kbds.py (данные, отправляемые при нажатии кнопки, для получения и обработки ботом):
# id комнаты для обращения к ней через базу данных,
# размер ставки (для надежности он также находится в базе данных в объекте lobby),
# размеры поля,
# координаты клетки X и Y, в которую сходил пользователь,
# и win_score - количество символов в ряд, которые нужно собрать для победы.
# Эти данные также есть в объекте User в поле game_params - параметрах текущей игры пользователя (если пользователь не играет в данный момент, то оно равно None).
# Они используются там, для поиска подходящей игры 

# Точка входа в игру. В этой функции задаются основные параметры игры, выстраивается поле и меняются состояния
# пользователя как внутри базы данных так и в state (FSMContext)
async def start_game(bot:Bot, chat_id:int, state:FSMContext, session:AsyncSession, start_game_parametrs:str, is_creator:bool, lobby:Lobby, opponent:User):

    
    lobby = await orm_query.get_lobby_by_id(session = session, lobby_id = lobby.id)
    game = await orm_query.get_game_by_id(session = session, game_name = strings.GAME_NAME, game_id = lobby.game_id)
    op_tag = opponent.tag if opponent.tag == None else "@" + opponent.tag


    message_to_display = await bot.send_message(chat_id = chat_id, text = f"Ваш противник: {opponent.name}  {op_tag}")
    message_to_display_2 = await bot.send_message(chat_id = chat_id, text = "...")


    if(not is_creator):
        await game.add_creator_field_message_id(session = session, field_message_id = message_to_display_2.message_id)
    else:
        await game.add_guest_field_message_id(session = session, field_message_id = message_to_display_2.message_id)



    # Ожидание заполнения параметров лобби со стороны противника
    opponent_field_message_id = None
    try_count = 0
    while(opponent_field_message_id == None):
        await session.refresh(game) # Обновление сессии для получения актуальный на данный момент информации
        await session.refresh(lobby)
        if(is_creator):
            opponent_field_message_id = game.guest_field_message_id
            opponent_id = lobby.guest_id
        else:
            opponent_field_message_id = game.creator_field_message_id
            opponent_id = lobby.creator_id

        try_count += 1
        await asyncio.sleep(system_parametrs.WAITING_UPDATE_TIME)
        if(try_count > system_parametrs.MAXIMUM_TRY_COUNT):
            await state.clear()
            await orm_query.set_user_state(session = session, user_id = chat_id, state = USER_STATES.NOT_ACTIVE)
            await lobby.delete()
            return await bot.edit_message_text(text = f"Соединение с игроком не состоялось(\nПопробуйте еще раз", chat_id = chat_id, message_id = message_to_display.message_id)


    message_to_display_2 = await bot.send_message(chat_id = chat_id, text = "...")
    message_to_display_2_id = message_to_display_2.message_id


    game_name, n, m, win_score, bet = strings.get_start_game_parametrs(start_game_parametrs)
    field = f"{strings.SYMBOL_UNDEF}" * n * m
    letter = strings.SYMBOL_X if is_creator else strings.SYMBOL_O
    lobby_id = lobby.id
    callback_data = TTT_game_callback_data(lobby_id = lobby_id, X = 0, Y = 0, n = n, m = m, win_score = win_score)

    

    await state.update_data(letter = letter)
    await state.update_data(opponent_field_message_id = opponent_field_message_id)
    await state.update_data(opponent_id = opponent_id)
    
    await game.add_field(session = session, field = field)




    # Разделение на мини-игры происходит через поле game_name в FSMContext. Данный Фильтр определен в TG/game/filters.py
    # и используется во всех хендлерах, ответственных за непосредственный игровой процесс
    await state.update_data(game_name = strings.GAME_NAME)
    await bot.edit_message_text(text = f"Вы играете за {letter}", reply_markup = ttt_game_buttons(callback_data = callback_data, field = field), chat_id = chat_id, message_id = message_to_display_2_id)





async def TTT_playing_callback(callback:types.CallbackQuery, callback_data:TTT_game_callback_data, state:FSMContext, session:AsyncSession):

    async def end_game():
        await orm_query.set_user_state(session = session, user_id = callback.from_user.id, state = USER_STATES.NOT_ACTIVE)
        await orm_query.set_user_state(session = session, user_id = opponent_id, state = USER_STATES.NOT_ACTIVE)
        await state.update_data(game_name = "")
        await lobby.delete()

    state_data = await state.get_data()
    cbd = callback_data
    bot = callback.bot

    lobby = await orm_query.get_lobby_by_id(session = session, lobby_id = cbd.lobby_id)
    game = await orm_query.get_game_by_id(session = session, game_name = strings.GAME_NAME, game_id = lobby.game_id)
    field = [game.field[cbd.n*i:][:cbd.m] for i in range(cbd.n)]
    letter = state_data["letter"]
    opponent_field_message_id = state_data["opponent_field_message_id"]
    opponent_id = state_data["opponent_id"]

    if(not game.can_walk(symbol = letter, field = game.field)):
        return await callback.answer("Сейчас не ваш ход🚫")
    
    if(field[cbd.Y][cbd.X] != strings.SYMBOL_UNDEF):
        return await callback.answer("Вы не можете так сходить!")
    
    field[cbd.Y] = field[cbd.Y][:cbd.X] + letter + field[cbd.Y][cbd.X + 1:]
    field_line = "".join(field)

    await game.set_field(session = session, field = field_line)
    await callback.message.edit_reply_markup(reply_markup = ttt_game_buttons(callback_data = cbd, field = field_line))
    await bot.edit_message_reply_markup(chat_id = opponent_id, message_id = opponent_field_message_id, \
                                        reply_markup = ttt_game_buttons(callback_data = cbd, field = field_line))
    
    result = game.is_win(FIELD = field, win_score = cbd.win_score)
    
    if(result == 'ничья'):
        await bot.edit_message_text(text =\
        f"у вас ничья", chat_id = opponent_id, message_id = opponent_field_message_id, reply_markup = finally_buttons())
        await end_game()

    elif(result == letter):
        await bot.edit_message_text(text =\
        f"Вы проиграли 😔", chat_id = opponent_id, message_id = opponent_field_message_id, reply_markup = finally_buttons())

        # Оплата <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<,
        # await orm_query.del_user_balance(session=session, user_id=opponent_id, amount=int(callback_data.bet))
        # await orm_query.set_user_balance(session=session, user_id=callback.from_user.id, amount=int(float(callback_data.bet)))

        await orm_query.add_lose(session=session, user_id=opponent_id)
        await orm_query.add_win(session=session, user_id=callback.from_user.id)


        await callback.message.edit_text(text =\
                f"Победа!🏆\n"
                f"Ваш выигрыш: {str(float(callback_data.bet))} USDT",
            reply_markup=finally_buttons())

        await end_game()


@router.callback_query(F.data == "end_game")
async def end_game(callback:types.CallbackQuery, state:FSMContext):
    await state.clear()
    await callback.message.edit_reply_markup(reply_markup = None)


@router.callback_query(F.data == "play_more")
async def play_more(callback:types.CallbackQuery, state:FSMContext):
    await state.clear()
    await callback.message.edit_reply_markup(reply_markup = None)
    await callback.message.delete()

    await callback.message.answer_photo(FSInputFile('Sourses/icon/icon1.png'),f"🎮 Выберите параметры",
                               parse_mode='HTML', reply_markup=choise_TTT_buttons())

        

router.callback_query.register(TTT_playing_callback, TTT_game_callback_data.filter())

