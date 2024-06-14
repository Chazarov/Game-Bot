from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from Database.models import User, USER_STATES

from random import randint

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



