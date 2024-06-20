from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from Database.models import User, USER_STATES, TTTlobbi

from random import randint



async def get_user_by_id(session:AsyncSession, user_id:int):
    q = select(User).where(User.id == user_id)
    r = await session.execute(q)
    return r.scalar()

async def get_user_who_want_to_play(session:AsyncSession, ignore_user_id:int, game_params:str):
    q = select(User).where(User.state == USER_STATES.WAITING_FOR_A_GAME, User.id != ignore_user_id, User.game_params == game_params)
    r = await session.execute(q)
    return r.scalars().first()

async def get_lobbi_by_invitation(session:AsyncSession, guest_id:int):
    q = select(TTTlobbi).where(TTTlobbi.guest_id == guest_id)
    r = await session.execute(q)
    obj = r.scalar()

    return obj

async def get_lobbi_by_id(session:AsyncSession, lobbi_id:int):
    q = select(TTTlobbi).where(TTTlobbi.id == lobbi_id)
    r = await session.execute(q)
    return r.scalar()



async def set_user_balance(session:AsyncSession, user_id:int, amount:int)->bool:
    user = await get_user_by_id(session = session, user_id = user_id)
    if(user != None):

        if(user.balance + amount >= 0):
            user.balance += amount
            await session.commit()
            return True
        else: return False
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

async def add_in_lobbi_guest_field_message_id(session:AsyncSession, lobbi_id:int, field_message_id):
    lobbi = await get_lobbi_by_id(session = session, lobbi_id = lobbi_id)
    if(lobbi != None):
        lobbi.guest_field_message_id = field_message_id
        await session.commit()
    else: raise ValueError(f"Lobbi with id {lobbi_id} not found")

async def add_in_lobbi_creator_field_message_id(session:AsyncSession, lobbi_id:int, field_message_id):
    lobbi = await get_lobbi_by_id(session = session, lobbi_id = lobbi_id)
    if(lobbi != None):
        lobbi.creator_field_message_id = field_message_id
        await session.commit()
    else: raise ValueError(f"Lobbi with id {lobbi_id} not found")





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

async def create_lobbi(session:AsyncSession, creator_id:int, guest_id:int):
    obj = TTTlobbi(
        creator_id = creator_id,
        guest_id = guest_id,
    )
    session.add(obj)
    await session.commit()
    return obj





async def close_lobbi(session:AsyncSession, lobbi_id:int):

    obj = await get_lobbi_by_id(session = session, lobbi_id = lobbi_id)

    if(obj == None): return None
    else:
        await session.delete(obj)
        await session.commit()
        return True









