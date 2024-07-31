import asyncio
import os
import time

from aiogram import F, types, Router, Bot
from aiogram.filters import StateFilter
from aiogram.types import FSInputFile
from aiogram.fsm.context import FSMContext

from TG.crypto_pay_api_sdk import cryptopay

from sqlalchemy.ext.asyncio import AsyncSession

from Database import orm_query
from Database.models import USER_STATES
from TG import system_parametrs

from Game.TTT import strings as TTTStrings
from Game.TTT import game as TTTgame

from Game.Durak import strings as DurakStrings
from Game.Durak import game as DurakGame

from TG.game.filters import CurrentGameFilter
from TG.game.filters import Game_states


from TG.game.TicTacToe.kbds import ttt_game_buttons, TTT_game_callback_data
from TG.game.TicTacToe.handlers import start_game as TTT_Start_Game
from TG.pay.kbds import check_pay
from TG.pay.utils import getInv, getPayUrl

from TG.game.TicTacToe.handlers import router as TTT_router
from TG.game.Durak.handlers import router as Durak_router

from TG.game.kbds  import GameStartParametrsCallback

# 1 выбор начальных параметров для игры
# 2 поиск лобби со схожими параметрами
# 3 Создание игровых полей и настройка лобби





    
router = Router()
router.include_router(TTT_router)
router.include_router(Durak_router)

Crypto = cryptopay.Crypto(token=os.getenv("CRYPTO_TOKEN"), testnet=False)





# Это оплата при условии что не достаточно средств? Как тогда проверяется что оплата прошла в дальнейшем в коде?
# Недостаточно средств для оплаты
async def insufficient_funds_for_the_bet(callback:types.CallbackQuery, callback_data:TTT_game_callback_data):
    await callback.message.delete()
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

    async def broke_connection():
        print(">>>>> Some went wrong + " + str(e))

        if(lobby != None):
            await lobby.delete(session = session)
        await state.clear()
        await orm_query.set_user_state(session = session, user_id = chat_id, state = USER_STATES.NOT_ACTIVE)
        await bot.send_message(text = f"Подключение сорвалось 😢. Попробуйте начать игру еще раз", chat_id = chat_id)


    message = callback.message
    chat_id = callback.from_user.id
    bot = message.bot
    is_creator:bool
    user = await orm_query.get_user_by_id(session=session, user_id=callback.from_user.id)


    # Формирование данных игры для поиска 


    # Проверка баланса
    # if user.balance < callback_data.bet:
    #    return await insufficient_funds_for_the_bet(callback, callback_data)
    


    # Устанавливаем состояние пользователя на ожидание игры с заданными параметрами
    await state.set_state(Game_states.Find_game)
    await orm_query.set_user_state(session = session, user_id = chat_id, state = USER_STATES.WAITING_FOR_A_GAME, find_game_parametrs = callback_data.game_parametrs)

    callback.message.delete()

    # Поиск противника или лобби, в которое система уже добавила пользователя
    opponent, lobby = await find_opponent_or_invitation(message.bot, session = session, chat_id = message.chat.id, game_start_parametrs = callback_data.game_parametrs)
    
    await orm_query.set_user_state(session = session, user_id = chat_id, state = USER_STATES.IN_GAME)
    await state.set_state(Game_states.In_game)

# try:


    # Проверка для профилактики ошибки создания двух комнат(lobby) с одним и тем же пользователем
    # (пользователь был приглашен в комнату другого игрока, пока для него создавалась собственная комната)
    another_lobby = await orm_query.get_lobby_by_invitation(session = session, guest_id = chat_id)

    if(another_lobby != None):
        lobby = another_lobby

    if(lobby != None):
        is_creator = False
        opponent_id = lobby.creator_id
        opponent = await orm_query.get_user_by_id(session = session, user_id = opponent_id)

    elif(opponent != None):
        is_creator = True

        #Почему то ошибки связанные с базой данных не всегда корректно обрабатываются try except. Придумать что - нибудь на замену      <<<<<<<<<<<<<<<<<
        lobby = await orm_query.create_lobby(session = session, creator_id = chat_id, guest_id = opponent.id, bet = callback_data.bet, game_name = callback_data.game_name, game_start_parametrs = callback_data.game_parametrs)
        
    else:
        await orm_query.set_user_state(session = session, user_id = chat_id, state = USER_STATES.NOT_ACTIVE)
        return await bot.send_message(text = f"К сожалению в лобби сейчас нет игроков 😢\nпопробуйте еще раз позже", chat_id = chat_id)





    #№2 - Синхронизация параметров игры
    # В нутри функций TTT_Start_Game и др Происходит ожидание заполнения всех данных в комнате: 
    # Ветвление на отдельные игры
    await session.refresh(lobby)
    if(lobby == None):
        return await broke_connection()

    if(callback_data.game_name == TTTStrings.GAME_NAME):
        await TTT_Start_Game(bot = bot, chat_id = chat_id, state = state, session = session, start_game_parametrs = callback_data.game_parametrs, is_creator = is_creator, lobby = lobby, opponent = opponent)
    elif(callback_data.game_name == DurakStrings.GAME_NAME):
        pass 

        



    # except Exception as e:
    #     print(">>>>>>>>>>>> Make game exception: " + str(e))
    #     return await broke_connection()




async def find_opponent_or_invitation(bot:Bot, session:AsyncSession, chat_id:str, game_start_parametrs:str):
    
    
    message_to_display = await bot.send_message(text = \
            f"Идет поиск противника\n"+\
            f"Время ожидания: {0}\n"
            f"|                 \n", chat_id = chat_id)
    message_to_display_id = message_to_display.message_id
    


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
            f"|    {bar*bar_count}              \n", chat_id = chat_id, message_id = message_to_display_id)

        #Чтобы избежать многократного обращения к базе данных за одну секунду проверка приглашения в комнату и поиск игрока для 
        # приглашения производятся не постоянно а каждые WAITING_UPDATE_TIME (смотреть эту величину в system_parametrs)
        if(waiting_time%system_parametrs.WAITING_UPDATE_TIME == 0):
            lobby = await orm_query.get_lobby_by_invitation(session = session, guest_id = chat_id)
            if(lobby != None): break
            opponent = await orm_query.get_user_who_want_to_play(session = session, ignore_user_id = chat_id, game_params = game_start_parametrs)
            if(opponent != None): break

        if(time.time() - timer_start > system_parametrs.MAXIMUM_WAITING_TIME): break

        await asyncio.sleep(1)

    await message_to_display.delete()
    return opponent, lobby


router.callback_query.register(start_game, GameStartParametrsCallback.filter(), StateFilter(None))#❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌