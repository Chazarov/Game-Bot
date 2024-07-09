import asyncio
import os

from aiogram import Bot, Dispatcher, types
from aiogram.types import BotCommand

from dotenv import find_dotenv, load_dotenv
load_dotenv(find_dotenv())

from Database.engine import as_create_db, session_maker
from Database.middleweares import DataBaseSession

from TG.game.TicTacToe.handlers import router as game_router
from TG.menu.handlers import router as menu_router
from TG.pay.handlers import router as pay_router




bot = Bot(token = os.getenv("TOKEN"))
dp = Dispatcher()


dp.include_router(game_router)
dp.include_router(menu_router)
dp.include_router(pay_router)


async def on_startup(bot):
    await as_create_db()

async def on_shutdown(bot):
    print("бот лег")


user_commands = [
    BotCommand(command='start', description='начать работу с ботом'),
    
]

async def main()->None:
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    dp.update.middleware(DataBaseSession(session_pool = session_maker))


    await bot.delete_webhook(drop_pending_updates = True)
    await bot.set_my_description("/start - начать работу")
    await bot.set_my_commands(commands = user_commands,scope = types.BotCommandScopeAllPrivateChats())
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())