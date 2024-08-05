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
from Game.Durak import game
from Game.Durak import interface

from TG.game.Durak.kbds import field_buttons, deck_buttons, FieldCallback, CartNavigationCallback

router = Router()

router.message.filter(CurrentGameFilter(game_name = strings.GAME_NAME))
router.callback_query.filter(CurrentGameFilter(game_name = strings.GAME_NAME))


# Ход игрока:
    # Игрок делает допустимые изменения на поле , которые сохраняются в Машине состояний FSMcontext. А при подтверждении хода эти данные добавляются в лобби 
    # Посредничество машины состояний нужно для того , чтобы избежать черезмерно частого обращения к базе данных
# Распределение данных:
    #     1) В объекте комнаты (база данных):
    #           вся конфигурация игры (игровая логика описана в Game/Durak/game.py) в виде строки(формирование строки происходит в функции Durak.pack())
    #     2) В данных машины состояний (FSMcontest) (оперативная память FSM):
    #           Данные для синхронизации с базой данных
    #               lobby_id - id объекта лобби в базе данных 
    #           Данные для отображения интерфейса и действий
    #               opponent_id - id противника,
    #               opponent_field_messages - id сообщений, которые являются игровым полем у противника
    #           А так же игровые данные:
    #               player_number - номер игрока 0 или 1 
    #               choisen_card - Текущая выбранная карта на поле(карта, которая будет бита)
    #               player_deck - колода игрока в виде списка list[list[int ,str]] - сила и масть карты
    #               current_deck_cart - индекс карты в колоде игрока, которая выбрана(отображается) в данный момент


async def start_game(bot:Bot, message:types.Message, state:FSMContext, session:AsyncSession, start_game_parametrs:str, is_creator:bool, lobby:Lobby, message_to_display_id:int, opponent:User, chat_id:int):


    lobby = await orm_query.get_lobby_by_id(session = session, lobby_id = lobby.id)
    game_data = await orm_query.get_game_by_id(session = session, game_name = strings.GAME_NAME, game_id = lobby.game_id)
    op_tag = opponent.tag if opponent.tag == None else "@" + opponent.tag


    message_to_display_1 = await bot.send_message(text = f"Ваш противник: {opponent.name}  {op_tag}", chat_id = chat_id)
    
    message_to_display_2 = await bot.send_message(text = "...", chat_id = chat_id)
    message_to_display_3 = await bot.send_message(text = "...", chat_id = chat_id)
    message_to_display_4 = await bot.send_message(text = "...", chat_id = chat_id)

    if(not is_creator):
        await game_data.set_display_messages_creator(session = session, message1 = message_to_display_2, message2 = message_to_display_3, message3 = message_to_display_4)
    else:
        await game_data.set_display_messages_guest(session = session, message1 = message_to_display_2, message2 = message_to_display_3, message3 = message_to_display_4)

    # Ожидание заполнения параметров лобби со стороны противника
    fields_are_filled_in = False
    try_count = 0
    while(not fields_are_filled_in):
        lobby = await orm_query.get_lobby_by_id(session = session, lobby_id = lobby.id)
        game_data = await orm_query.get_game_by_id(session = session, game_name = strings.GAME_NAME, game_id = game_data.id)
        await session.refresh(game_data) # Обновление сессии для получения актуальный на данный момент информации
        await session.refresh(lobby)
        if(is_creator):
            fields_are_filled_in = game_data.guest_fields_are_filled_in
        else:
            fields_are_filled_in = game_data.creator_fields_are_filled_in

        try_count += 1
        await asyncio.sleep(system_parametrs.WAITING_UPDATE_TIME)
        if(try_count > system_parametrs.MAXIMUM_TRY_COUNT):
            await state.clear()
            await orm_query.set_user_state(session = session, user_id = chat_id, state = USER_STATES.NOT_ACTIVE)
            await lobby.delete(session = session)
            await bot.edit_message_text(text = f"Соединение с игроком не состоялось(\nПопробуйте еще раз", chat_id = chat_id, message_id = message_to_display_1)



    # Заполнение параметров, необходимых для игрового процесса
    player_number, opponent_number = 0, 1 if is_creator else 1, 0
    game_configuration = game.Durak()
    game_config_pack = game_configuration.pack()
    await game_data.set_current_game_data(session = session, game_data = game_config_pack, turn = 0)

    await state.update_data(game_name = strings.GAME_NAME) #Через это поле происходит фильтрация хендлеров игрового процесса с помощью CurrentGameFilter. Данный Фильтр определен в TG/game/filters.py
    await state.update_data(player_number = player_number)
    await state.update_data(opponent_id = opponent.id)
    await state.update_data(opponent_field_messages = [message_to_display_2.message_id, message_to_display_3.message_id, message_to_display_4.message_id])
    await state.update_data(choisen_card = None)
    await state.update_data(player_deck = interface.make_cards_parametrs_list(game_configuration.players[player_number].cards))
    await state.update_data(current_deck_cart = 0)

    

    

    await bot.edit_message_text(text = f"Колода противника: {interface.draw_cards(game_configuration.players[opponent_number])}", chat_id = chat_id, message_id = message_to_display_2.message_id)
    await bot.edit_message_text(text = "поле:", chat_id = chat_id, message_id = message_to_display_3.message_id, reply_markup = field_buttons(lobby.id, game_configuration.field)) 
    await bot.edit_message_text(text = " Ваши карты:", chat_id = chat_id, message_id = message_to_display_4.message_id, reply_markup = deck_buttons()) 




@router.callback_query(FieldCallback.filter())
async def field_callback(callback:types.CallbackQuery, callback_data:FieldCallback, state:FSMContext, session:AsyncSession):

    lobby = await orm_query.get_lobby_by_id(session = session, lobby_id = callback_data.lobby_id)
    game_data = await orm_query.get_game_by_id(session = session, game_name = strings.GAME_NAME, game_id = lobby.game_id)

    game_configuration = game.Durak()
    game_configuration.unpack(game_data.current_game_data)

    await state.update_data(choisen_card = callback_data.selected_number)
    await callback.message.edit_reply_markup(reply_markup = field_buttons(lobby_id = lobby.id, cards = game_configuration.deck, choisen = callback_data.selected_number))




@router.callback_query(CartNavigationCallback.filter())
async def card_navigation_callback(callback:types.CallbackQuery, callback_data:CartNavigationCallback, state:FSMContext, session:AsyncSession):
    fsm_data = await state.get_data()
    player_deck = fsm_data["player_deck"]

    if((len(player_deck) > callback_data.next_card) and (callback_data >= 0)):
        await state.update_data(choisen_card = callback_data.next_card)





