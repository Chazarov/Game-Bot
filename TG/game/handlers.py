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

from Game.TTT import strings as TTTStrings
from Game.TTT import game as TTTgame

from Game.Durak import strings as DurakStrings
from Game.Durak import game as DurakGame

from TG.game.filters import CurrentGameFilter


from TG.game.TicTacToe.kbds import ttt_game_buttons, TTT_game_callback_data
from TG.game.TicTacToe.handlers import start_game as TTT_Start_Game#Вынести в эту функцию инициализацию игры
from TG.pay.kbds import check_pay
from TG.pay.utils import getInv, getPayUrl

from TG.game.TicTacToe.handlers import router as TTT_router
from TG.game.Durak.handlers import router as Durak_router

from TG.game.kbds  import GameStartParametrsCallback

# 1 выбор начальных параметров для игры
# 2 поиск лобби со схожими параметрами
# 3 Создание игровых полей и настройка лобби


# Главные состояния бота
class Game_states(StatesGroup):
    Find_game = State()
    In_game = State()




    
router = Router()
router.include_router(TTT_router)
router.include_router(Durak_router)

Crypto = cryptopay.Crypto(token=os.getenv("CRYPTO_TOKEN"), testnet=False)




async def delete_menu(callback:types.CallbackQuery):
    await callback.message.delete()



# Это оплата при условии что не достаточно средств? Как тогда проверяется что оплата прошла в дальнейшем в коде?
# Недостаточно средств для оплаты
async def insufficient_funds_for_the_bet(callback:types.CallbackQuery, callback_data:TTT_game_callback_data):
    delete_menu(callback = callback)
    await callback.answer("Недостаточно средств для игры, пополните баланс")
    pay = Crypto.createInvoice("USDT", str(callback_data.bet), params={"description": "Оплата игры", "expires_in": 60})

    invoiceID = getInv(str(pay))
    URL = getPayUrl(str(pay))

    # await message.answer(f"Ссылка на оплату: {URL}",parse_mode='HTML', reply_markup=check_pay(invoiceID))

    await callback.message.answer_photo(FSInputFile('Sourses/icon/icon1.png'), caption=f"💳 Оплата игры\n\n"
                                                                                f"Ваш айди: <code>{str(callback.message.from_user.id)}</code>\n"
                                                                                f"ID заказа: <b>{invoiceID}</b>\n"
                                                                                f"Сумма: <b>{callback_data.bet} USDT</b>",
                                parse_mode='HTML', reply_markup=check_pay(invoiceID, URL))
    


# 1 Найти противника 
# 2 Создать лобби и игровое поле


# Соединение игроков происходит следующим образом:  
#
#    №1 - Поиск противника 
# Игроку (объект User в Database.models) в базе данных сначала присваивается состояние WAITING_FOR_A_GAME и полю find_game_parametrs - параметры выбранной им игры.
# Далее происходит поиск пользователя с состоянием WAITING_FOR_A_GAME и идентичными параметрами игры.
# Если такой пользователь найден - создается "Лобби" (далее будет упоминаться как Комната) (объект TTT_lobby в Database.models), где находятся параметры для синхронизации
# (id обоих противников, id сообщений - которые будут являться полем для игры у обоих пользователей).
#
# При этом одновременно с поиском пользователя с состоянием WAITING_FOR_A_GAME происходит поиск комнаты, в которую приглашен пользователь (Если в какой-то комнате указан id пользователя как guest_id),
# значит пользователь уже сам был приглашен в лобби и поиск противника заканчивается.
#
# Далее происходит синхронизация параметров игры (смотреть далее в этом коде №2). 
async def start_game(callback:types.CallbackQuery, callback_data:GameStartParametrsCallback, state:FSMContext, session:AsyncSession):

    message = callback.message
    chat_id = callback.from_user.id
    bot = message.bot
    is_creator:bool
    user = await orm_query.get_user_by_id(session=session, user_id=callback.from_user.id)


    # Формирование данных игры для поиска 
    game_start_parametrs = ""
    if(callback_data.game_name == TTTStrings.GAME_NAME):
        game_start_parametrs = TTTStrings.get_start_game_parametrs(callback_data.game_parametrs)
    elif(callback_data.game_name == DurakStrings.GAME_NAME):
        game_start_parametrs = DurakStrings.get_start_game_parametrs(callback_data.game_parametrs)



    if user.balance < callback_data.bet:
        await insufficient_funds_for_the_bet(callback, callback_data)
    else:
        await state.set_state(Game_states.Find_game)
        
        
        # Устанавливаем состояние пользователя на ожидание игры с заданными параметрами
        await orm_query.set_user_state(session = session, user_id = chat_id, state = USER_STATES.WAITING_FOR_A_GAME, find_game_parametrs = game_start_parametrs)

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
        lobby = None
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
                lobby = await orm_query.get_lobby_by_invitation(session = session, guest_id = chat_id)
                if(lobby != None): break
                opponent = await orm_query.get_user_who_want_to_play(session = session, ignore_user_id = chat_id, game_params = game_start_parametrs)
                if(opponent != None): break

            if(time.time() - timer_start > system_parametrs.MAXIMUM_WAITING_TIME): break

            await asyncio.sleep(1)

        await orm_query.set_user_state(session = session, user_id = chat_id, state = USER_STATES.IN_GAME)
        await state.set_state(Game_states.In_game)

        try:
            # Проверка для профилактики ошибки создания двух комнат(lobby) с одним и тем же пользователем
            # (пользователь был приглашен в комнату другого игрока, пока для него создавалась собственная комната)
            another_lobby = await orm_query.get_lobby_by_invitation(session = session, guest_id = chat_id)
            #Вынести определение символа в начало игры!!!!!
            if(another_lobby != None):
                lobby = another_lobby

            if(lobby != None):
                is_creator = False
                opponent_id = lobby.creator_id
                opponent = await orm_query.get_user_by_id(session = session, user_id = opponent_id)

            elif(opponent != None):
                is_creator = True
                lobby = await orm_query.create_lobby(session = session, creator_id = chat_id, guest_id = opponent.id)

            else:
                await orm_query.set_user_state(session = session, user_id = chat_id, state = USER_STATES.NOT_ACTIVE)
                return await bot.edit_message_text(text = f"К сожалению в лобби сейчас нет игроков 😢\nпопробуйте еще раз позже", chat_id = chat_id, message_id = message_id)






            #№2 - Синхронизация параметров игры
            # В нутри функций TTT_Start_Game и др Происходит ожидание заполнения всех данных в комнате: 
            # Ветвление на отдельные игры
            if(callback_data.game_name == TTTStrings.GAME_NAME):
                TTT_Start_Game(bot, message, state, session, game_start_parametrs, is_creator, lobby, send_message, opponent, chat_id)
            elif(callback_data.game_name == DurakStrings.GAME_NAME):
                pass

            

        except Exception as e:
            print(e)
            if(lobby != None):
                await lobby.delete(session = session)
            await state.clear()
            await orm_query.set_user_state(session = session, user_id = chat_id, state = USER_STATES.NOT_ACTIVE)
            return await bot.edit_message_text(text = f"Ошибка подключения (\nПопробуйте еще раз позже", chat_id = chat_id, message_id = send_message.message_id)




router.callback_query.register(start_game, GameStartParametrsCallback.filter(), StateFilter(None))