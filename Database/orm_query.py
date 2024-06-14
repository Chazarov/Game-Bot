from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from Database.models import User, USER_STATES, TTTlobbi

from random import randint



async def get_user_by_id(session:AsyncSession, user_id:int):
    q = select(User).where(User.id == user_id)
    r = await session.execute(q)
    return r.scalar()

async def get_user_who_want_to_play(session:AsyncSession):
    q = select(User).where(User.state == USER_STATES.WAITING_FOR_A_GAME)
    r = await session.execute(q)
    users = r.scalar()
    if(users == None): return None
    random_user_id = randint(0, len(users) - 1)
    return users[random_user_id]

async def get_lobbi_by_user_id(session:AsyncSession, user_id:int):
    q = select(TTTlobbi).where(TTTlobbi.O_user_id == user_id)
    r = await session.execute(q)
    obj = r.scalar()

    if(obj != None): return obj
    else:
        q = select(TTTlobbi).where(TTTlobbi.X_user_id == user_id)
        r = await session.execute(q)
        obj = r.scalar()
        if(obj != None): return obj
        else: return None

async def get_lobbi_by_id(session:AsyncSession, lobbi_id:int):
    q = select(TTTlobbi).where(TTTlobbi.id == lobbi_id)
    r = await session.execute(q)
    return r.scalar()



async def set_user_state(session:AsyncSession, user_id:int, state:str):
    user = await get_user_by_id(session = session, user_id = user_id)
    if(user != None):
        user.state = state
        await session.commit()
        return user
    else: raise ValueError(f"User with id {user_id} not found")



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

async def create_lobbi(session:AsyncSession, X_user_id:int, O_user_id:int):
    obj = TTTlobbi(
        X_user_id = X_user_id,
        O_user_id = O_user_id
    )
    session.add(obj)
    await session.commit()
    return obj






async def close_lobbi(session:AsyncSession, lobbi_id:int):

    obj = get_lobbi_by_id(session = session, lobbi_id = lobbi_id)

    if(obj == None): return None
    else:
        session.delete(obj)
        await session.commit()
        return True









