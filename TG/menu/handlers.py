from aiogram import F, types, Router, Dispatcher
from aiogram.filters import Command, StateFilter
from aiogram.types import FSInputFile, InputMediaPhoto
from aiogram.fsm.context import FSMContext

from sqlalchemy.ext.asyncio import AsyncSession

from Database import orm_query



router = Router()



@router.message(Command("start"))
async def command_start(message: types.Message, state:FSMContext):
    print(message.message_id)
    await message.answer("Приветствую!")


@router.message(Command("profile"))
async def command_profile(message: types.Message, session:AsyncSession):
    pass