import asyncio
import os
import time

from aiogram import F, types, Router, Dispatcher
from aiogram.filters import Command, StateFilter
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import FSInputFile, InputMediaPhoto
from aiogram.fsm.context import FSMContext

from crypto_pay_api_sdk import cryptopay

from sqlalchemy.ext.asyncio import AsyncSession

from Database import orm_query
from Database.models import USER_STATES
from TG import system_parametrs

from Game.TTT import strings
from Game.TTT import game

from TG.game.filters import CurrentGameFilter


from TG.game.TicTacToe.kbds import ttt_game_buttons, TTT_game_callback_data
from TG.game.TicTacToe.handlers import start_game #Вынести в эту функцию инициализацию игры
from TG.pay.kbds import check_pay
from TG.pay.utils import getInv, getPayUrl

from TG.game.TicTacToe.handlers import router as TTT_router
from TG.game.Durak.handlers import router as Durak_router




class Game_states(StatesGroup):
    Find_game = State()
    In_game = State()




    
router = Router()
router.include_router(TTT_router)
router.include_router(Durak_router)

Crypto = cryptopay.Crypto(token=os.getenv("CRYPTO_TOKEN"), testnet=False)




async def delete_menu(callback:types.CallbackQuery):
    await callback.message.delete()

# Соединение игроков происходит следующим образом:  
#
#    №1 - Поиск противника 
# Игроку (объект User в Database.models) в базе данных сначала присваивается состояние WAITING_FOR_A_GAME и полю find_game_parametrs - параметры выбранной им игры.
# Далее происходит поиск пользователя с состоянием WAITING_FOR_A_GAME и идентичными параметрами игры.
# Если такой пользователь найден - создается "Лобби" (далее будет упоминаться как Комната) (объект TTT_lobbi в Database.models), где находятся параметры для синхронизации
# (id обоих противников, id сообщений - которые будут являться полем для игры у обоих пользователей).
#
# При этом одновременно с поиском пользователя с состоянием WAITING_FOR_A_GAME происходит поиск комнаты, в которую приглашен пользователь (Если в какой-то комнате указан id пользователя как guest_id),
# значит пользователь уже сам был приглашен в лобби и поиск противника заканчивается.
#
# Далее происходит синхронизация параметров игры (смотреть далее в этом коде №2). 
async def start_game(callback:types.CallbackQuery, callback_data:TTT_game_callback_data, state:FSMContext, session:AsyncSession):

    
    
    message = callback.message
    chat_id = callback.from_user.id
    bot = message.bot
    is_creator:bool
    game_parametrs = game.make_game_parametrs(n = callback_data.n, m = callback_data.m, win_score = callback_data.win_score, bet = callback_data.bet)

    user = await orm_query.get_user_by_id(session=session, user_id=callback.from_user.id)
    if user.balance < callback_data.bet:
        await callback.message.delete()
        await callback.answer("Недостаточно средств для игры, пополните баланс")
        pay = Crypto.createInvoice("USDT", str(callback_data.bet), params={"description": "Оплата игры", "expires_in": 60})

        invoiceID = getInv(str(pay))
        URL = getPayUrl(str(pay))

        # await message.answer(f"Ссылка на оплату: {URL}",parse_mode='HTML', reply_markup=check_pay(invoiceID))

        await message.answer_photo(FSInputFile('Sourses/icon/icon1.png'), caption=f"💳 Оплата игры\n\n"
                                                                                  f"Ваш айди: <code>{str(message.from_user.id)}</code>\n"
                                                                                  f"ID заказа: <b>{invoiceID}</b>\n"
                                                                                  f"Сумма: <b>{callback_data.bet} USDT</b>",
                                   parse_mode='HTML', reply_markup=check_pay(invoiceID, URL))
    else:

        await state.set_state(Game_states.Find_game)
        
        
        # Устанавливаем состояние пользователя на ожидание игры с заданными параметрами
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

            #Чтобы избежать многократного обращения к базе данных за одну секунду проверка приглашения в комнату и поиск игрока для 
            # приглашения производятся не постоянно а каждые WAITING_UPDATE_TIME (смотреть эту величину в system_parametrs)
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
            #    №2 - Синхронизация параметров игры
            # Происходит ожидание заполнения всех данных в комнате:
            # creator_field_message_id и guest_field_message_id - id сообщений, которые будут служить полем для игры.
            # Данные, необходимые для игрового процесса, распределены следующим образом:
            #
            #     1) В объекте комнаты (база данных):
            # поле (так как в объектах, наследуемых от Callback_data, остановлено ограничение).
            #     2) В данных машины состояний (FSMcontest) (оперативная память FSM):
            # id противника,
            # id сообщения, которое является игровым полем у противника,
            # letter - обозначает, за кого играет пользователь (❌ или ⭕).
            #     3) В объекте класса Callback_data (TTT_game_callback_data, см. в TG/game/kbds) (данные, отправляемые при нажатии кнопки, для получения и обработки ботом):
            # id комнаты для обращения к ней через базу данных,
            # размер ставки (для надежности он также находится в базе данных в объекте lobbi),
            # размеры поля,
            # координаты клетки X и Y, в которую сходил пользователь,
            # и win_score - количество символов в ряд, которые нужно собрать для победы.
            # Эти данные также есть в объекте User в поле game_params - параметрах текущей игры пользователя (если пользователь не играет в данный момент, то оно равно None).
            # Они используются там, для поиска подходящей игры 

            while(opponent_field_message_id == None):
                lobbi = await orm_query.get_lobbi_by_id(session = session, lobbi_id = lobbi.id)
                await session.refresh(lobbi) # Обновление сессии для получения актуальный на данный момент информации
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
            await bot.edit_message_text(text = f"Вы играете за {letter}", reply_markup = ttt_game_buttons(callback_data = callback_data, field = field), chat_id = chat_id, message_id = send_message.message_id)

        except Exception as e:
            print(e)
            if(lobbi != None):
                await orm_query.close_lobbi(session = session, lobbi_id = lobbi.id)
            await state.clear()
            await orm_query.set_user_state(session = session, user_id = chat_id, state = USER_STATES.NOT_ACTIVE)
            return await bot.edit_message_text(text = f"Ошибка подключения (\nПопробуйте еще раз позже", chat_id = chat_id, message_id = send_message.message_id)




router.callback_query.register(start_game, TTT_game_callback_data.filter(), StateFilter(None))