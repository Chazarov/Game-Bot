from aiogram import F, types, Router, Dispatcher
from aiogram.filters import Command, StateFilter
from aiogram.types import FSInputFile, InputMediaPhoto
from aiogram.fsm.context import FSMContext

from sqlalchemy.ext.asyncio import AsyncSession

from Database import orm_query



router = Router()



@router.message(Command("start"))
async def command_start(message: types.Message, session:AsyncSession):
    user_id = message.from_user.id
    user = await orm_query.get_user_by_id(session = session, user_id = user_id)
    if(user == None):
        tag = message.from_user.username
        await orm_query.add_user(session = session, user_id = user_id, name = message.from_user.first_name, tag = tag)

    await message.answer("Приветствую!")


@router.message(Command("profile"))
async def command_profile(message: types.Message, session:AsyncSession):
    pass