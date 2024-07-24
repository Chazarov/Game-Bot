from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from Database.models import User, USER_STATES, Lobby, promo_codes, TTT_game, Durak_game

from Game.TTT import strings as TTTStrings
from Game.Durak import strings as DurakStrings

from random import randint


#  User
async def get_user_by_id(session:AsyncSession, user_id:int):
    q = select(User).where(User.id == user_id)
    r = await session.execute(q)
    return r.scalar()

async def get_user_who_want_to_play(session:AsyncSession, ignore_user_id:int, game_params:str):
    q = select(User).where(User.state == USER_STATES.WAITING_FOR_A_GAME, User.id != ignore_user_id, User.game_params == game_params)
    r = await session.execute(q)
    return r.scalars().first()

async def set_user_balance(session:AsyncSession, user_id:int, amount:int)->bool:
    user = await get_user_by_id(session = session, user_id = user_id)
    if(user != None):

        if(user.balance + amount >= 0):
            user.balance += amount
            await session.commit()
            return True
        else: return False
    else: raise ValueError(f"User with id {user_id} not found")

async def del_user_balance(session:AsyncSession, user_id:int, amount:float)->bool:
    user = await get_user_by_id(session = session, user_id = user_id)
    if(user != None):
        user.balance = user.balance - amount
        await session.commit()
        return True
    else: raise ValueError(f"User with id {user_id} not found")

async def add_lose(session:AsyncSession, user_id:int)->bool:
    user = await get_user_by_id(session = session, user_id = user_id)
    if(user != None):
        user.loses = user.loses + 1
        await session.commit()
        return True
    else: raise ValueError(f"User with id {user_id} not found")
async def set_user_state(session:AsyncSession, user_id:int, state:str, find_game_parametrs:str = None):
    user = await get_user_by_id(session = session, user_id = user_id)
    if(user != None):
        if(state == USER_STATES.WAITING_FOR_A_GAME):
            if (find_game_parametrs == None):
                raise ValueError(f"value of find_game_parametrs must not be empty")
            user.game_params = find_game_parametrs

        if(state == USER_STATES.NOT_ACTIVE):
            user.game_params = None

        user.state = state
        await session.commit()
        return user
    else: raise ValueError(f"User with id {user_id} not found")

async def get_active_users(session:AsyncSession):
    users = await session.execute(
        select(User.id).filter(User.is_active)
    )
    return users.scalars().all()

async def add_win(session:AsyncSession, user_id:int)->bool:
    user = await get_user_by_id(session = session, user_id = user_id)
    if(user != None):
        user.wins = user.wins + 1
        await session.commit()
        return True
    else: raise ValueError(f"User with id {user_id} not found")

async def change_active(session:AsyncSession, user_id:int, is_active:bool) -> bool:
    user = await get_user_by_id(session=session, user_id=user_id)
    if (user != None):
        user.is_active = is_active
        await session.commit()
        return True
    else:
        raise ValueError(f"User with id {user_id} not found")





# Lobby
async def get_lobby_by_id(session:AsyncSession, lobby_id:int):
    q = select(Lobby).where(Lobby.id == lobby_id)
    r = await session.execute(q)
    return r.scalar()

async def get_lobby_by_invitation(session:AsyncSession, guest_id:int):
    q = select(Lobby).where(Lobby.guest_id == guest_id)
    r = await session.execute(q)
    obj = r.scalar()

    return obj

async def create_lobby(session:AsyncSession, creator_id:int, guest_id:int, bet:int, game_name:str, game_start_parametrs:str):
    game_obj = await create_game(session = session, game_name = game_name, game_parametrs = game_start_parametrs)


    obj = Lobby(
        game_name = game_name,
        creator_id = creator_id,
        guest_id = guest_id,
        game_id = game_obj.id,
        bet = bet
    )

    session.add(obj)
    await session.commit()
    return obj





# Game
async def get_game_by_id(session:AsyncSession, game_name:str, game_id:int):
    if(game_name == TTTStrings.GAME_NAME):
        q = select(TTT_game).where(TTT_game.id == game_id)
    elif(game_name == DurakStrings.GAME_NAME):
        q = select(Durak_game).where(Durak_game.id == game_id)
    r = await session.execute(q)
    obj = r.scalar()

    return obj

async def create_game(session:AsyncSession, game_name:str, game_parametrs:str):
    if(game_name == TTTStrings.GAME_NAME):
        obj = TTT_game(
            #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        )
    elif(game_name == DurakStrings.GAME_NAME):
        obj = Durak_game(
            #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        )

    session.add(obj)
    await session.commit()
    return obj





# Admin
async def add_promo(session:AsyncSession, promo:str, summa:int):
    obj = promo_codes(
        promoname = promo,
        amount = summa,
    )
    session.add(obj)
    await session.commit()
    return obj

async def get_promo_by_id(session:AsyncSession, promo:str):
    q = select(promo_codes).where(promo_codes.promoname == promo)
    r = await session.execute(q)
    return r.scalar()

async def delete_promo(session:AsyncSession, promo:str):
    promo = await get_promo_by_id(session = session, promo = promo)
    await session.delete(promo)
    await session.commit()
async def add_user(session:AsyncSession, user_id:int, tag:str, name:str):
    obj = User(
        id = user_id,
        tag = tag,
        name = name,
        state = USER_STATES.NOT_ACTIVE
    )
    session.add(obj)
    await session.commit()
    return obj













