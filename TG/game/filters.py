from aiogram import Router
from aiogram.filters import Filter
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from sqlalchemy.ext.asyncio import AsyncSession

class CurrentGameFilter(Filter):

    game_name:str

    def __init__(self, game_name:str) -> None:
        self.game_name = game_name
        return

    async def __call__(self, message:Message, state:FSMContext) -> bool:
        data = await state.get_data()
        if("game_name" in data.keys):
            if(self.game_name == data["game_name"]):
                return True
        return False