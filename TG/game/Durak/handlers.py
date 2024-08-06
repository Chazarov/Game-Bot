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

from TG.game.Durak.kbds import field_buttons, deck_buttons, confirm_end_of_game_buttons, FieldCallback, CartNavigationCallback, CONFIRM_CALLBACK, ACTION_BUTTON_CALLBACK, END_GAME_CALLBACK

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
    #           Данные для фильтрации хендлеров (общие для всех мини-игр бота)
    #               game_name - название игры (константное название игры определено в блоке логики этой игры в директории Game в файлах strings.py)
    #           Данные для синхронизации с базой данных
    #               lobby_id - id объекта лобби в базе данных 
    #           Данные для отображения интерфейса и действий
    #               opponent_id - id противника,
    #               opponent_field_messages - id сообщений, которые являются игровым полем у противника
    #               player_field_messages - id сообщений, которые являются игровым полем у игрока
    #           Данные для взаимодействия с интерфейсом
    #               player_number - в игровой конфигурации игроки отличаются номером (0 или 1)(подробнее смотреть Game/Durak/game.py )
    #               field_card_idx - индекс карты на поле, которая выбрана игроком
    #               deck_cart_idx - индекс карты в колоде игрока, которая выбрана в данный момент и которой будет совершено действие (подкинуть или покрыть)
    #           А так же игровые данные, ознакомится с формированием которых можно Game/Durak/game.py (методы Durak_game.pack() / .unpack())



async def start_game(bot:Bot, message:types.Message, state:FSMContext, session:AsyncSession, start_game_parametrs:str, is_creator:bool, lobby:Lobby, message_to_display_id:int, opponent:User, chat_id:int):
    
    lobby = await orm_query.get_lobby_by_id(session = session, lobby_id = lobby.id)
    game_data = await orm_query.get_Durak_game_by_id(session = session, game_id = lobby.game_id)
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
        game_data = await orm_query.get_Durak_game_by_id(session = session, game_id = game_data.id)
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
            return await bot.edit_message_text(text = f"Соединение с игроком не состоялось(\nПопробуйте еще раз", chat_id = chat_id, message_id = message_to_display_1)

    opponent_field_messages = None
    if(is_creator):
        opponent_field_messages = [game_data.guest_display_message_1, game_data.guest_display_message_2, game_data.guest_display_message_3]
    else:
        opponent_field_messages = [game_data.creator_display_message_1, game_data.creator_display_message_2, game_data.creator_display_message_3]





    # Заполнение параметров, необходимых для игрового процесса
    player_number, opponent_number = 0, 1 if is_creator else 1, 0
    game_configuration = game.Durak()
    game_config_str = game_configuration.pack_str()
    game_config_dict = game_configuration.pack_dict()

    await game_data.set_current_game_data(session = session, game_data = game_config_str, turn = 0)

    game_config_dict["game_name"] = strings.GAME_NAME #Через это поле происходит фильтрация хендлеров игрового процесса с помощью CurrentGameFilter. Данный Фильтр определен в TG/game/filters.py
    game_config_dict["lobby_id"] = lobby.id
    game_config_dict["player_number"] = player_number
    game_config_dict["opponent_id"] = opponent.id
    game_config_dict["opponent_field_messages"] = opponent_field_messages
    game_config_dict["player_field_messages"]
    game_config_dict["field_card_idx"] = None
    game_config_dict["deck_card_idx"] = 0
    await state.update_data(game_config_dict)
    




    await bot.edit_message_text(text = f"Колода противника: {interface.draw_cards(game_configuration.players[opponent_number])}", chat_id = chat_id, message_id = message_to_display_2.message_id)
    await bot.edit_message_text(text = "поле:", chat_id = chat_id, message_id = message_to_display_3.message_id, reply_markup = field_buttons(lobby.id, game_configuration.field)) 
    await bot.edit_message_text(text = " Ваши карты:", chat_id = chat_id, message_id = message_to_display_4.message_id, reply_markup = deck_buttons()) 




@router.callback_query(FieldCallback.filter())
async def field_callback(callback:types.CallbackQuery, callback_data:FieldCallback, state:FSMContext, session:AsyncSession):

    lobby = await orm_query.get_lobby_by_id(session = session, lobby_id = callback_data.lobby_id)
    game_data = await orm_query.get_Durak_game_by_id(session = session, game_id = lobby.game_id)

    game_configuration = game.Durak()
    game_configuration.unpack(game_data.current_game_data)

    await state.update_data(choisen_card = callback_data.selected_number)
    await callback.message.edit_reply_markup(reply_markup = field_buttons(lobby_id = lobby.id, cards = game_configuration.deck, choisen = callback_data.selected_number))




@router.callback_query(CartNavigationCallback.filter())
async def card_navigation_callback(callback:types.CallbackQuery, callback_data:CartNavigationCallback, state:FSMContext, session:AsyncSession):
    fsm_data = await state.get_data()
    player_deck = fsm_data["player_deck"]

    if((len(player_deck) > callback_data.next_card) and (callback_data >= 0)):

        deck_card = fsm_data["player_decks"][fsm_data["player_number"]][callback_data.next_card]
        
        await state.update_data(choisen_card = callback_data.next_card)
        await callback.message.edit_text(text = interface.draw_card(deck_card), reply_markup = deck_buttons())





@router.callback_query(F.data == ACTION_BUTTON_CALLBACK)
async def action_button_callback(callback:types.CallbackQuery, state:FSMContext, session:AsyncSession):

    async def you_cant_move_like_that():
        await callback.answer("Вы не можете так сходить!") 
    




    # Распаковка данных
    fsm_data = await state.get_data()
    if((fsm_data["field_card_idx"] == None) and (fsm_data["player_number" != fsm_data["attacking_player"]])):
        return # Если не выбрана карта на поле и игрок кроется<<<<<<<<<<<<<<<<<<<<<<<<<<<<
    game_config = game.Durak()
    game_config.unpack_dict(fsm_data)





    # Совершение игровой логики
    if(game_config.turn == game_config.attacking_player):
        if(game_config.can_throw_in(fsm_data["deck_card_idx"])):
            game_config.to_throw_in(fsm_data["deck_card_idx"])
        else:
            return await you_cant_move_like_that()
    else:
        if(game_config.can_cover(fsm_data["deck_card_idx"], fsm_data["field_card_idx"])):
            game_config.to_cover(fsm_data["deck_card_idx"], fsm_data["field_card_idx"])
        else:
            return await you_cant_move_like_that()





    # Сохранение данных 
    updated_data_dict = game_config.pack_dict(fsm_data)
    await state.update_data(updated_data_dict)



# При подтверждении хода происходит перенос данных из машины состояний в объект базы данных
@router.callback_query(F.data == CONFIRM_CALLBACK)
async def confirm_button_callback(callback:types.CallbackQuery, state:FSMContext, session:AsyncSession):

    async def you_are_win():
        await bot.delete_message(fsm_data["player_field_messages"][0])
        await bot.delete_message(fsm_data["player_field_messages"][1])
        await bot.delete_message(fsm_data["player_field_messages"][2])
        await bot.delete_message(fsm_data["opponent_field_messages"][0])
        await bot.delete_message(fsm_data["opponent_field_messages"][1])
        await bot.delete_message(fsm_data["opponent_field_messages"][2])

        await callback.message.answer(text = "Победа", reply_markup = confirm_end_of_game_buttons())
        await callback.message.answer(text = "Поражение", reply_markup = confirm_end_of_game_buttons())





    # Распаковка данных
    bot = callback.bot
    chat_id = callback.message.chat.id
    lobby = await orm_query.get_lobby_by_id(session = session, lobby_id = fsm_data["lobby_id"])
    game_data = await orm_query.get_Durak_game_by_id(session = session, game_id = lobby.game_id)

    fsm_data = await state.get_data()
    game_configuration = game.Durak()
    game_configuration.unpack_dict(fsm_data)


    # Совершение игровой логики
    turn_result = game_configuration.confirm()

    if(turn_result == strings.WIN):
        return await you_are_win()




    # Сохранение данных 
    game_config_str = game_configuration.pack_str()
    game_config_dict = game_configuration.pack_dict(fsm_data = fsm_data)
    await game_data.set_current_game_data(session = session, game_data = game_config_str, turn = game_configuration.turn)
    await state.update_data(game_config_dict)



@router.callback_query(F.data == END_GAME_CALLBACK)
async def end_game(callback:types.CallbackQuery, state:FSMContext, session:AsyncSession):

    await state.clear()
    await callback.message.edit_reply_markup(reply_markup = None)