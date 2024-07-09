from aiogram import F, types, Router, Dispatcher
from aiogram.filters import Command, StateFilter
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import FSInputFile, InputMediaPhoto
from aiogram.fsm.context import FSMContext

from Game.Durak import strings

from TG.game.filters import CurrentGameFilter


router = Router()

router.message.filter(CurrentGameFilter(game_name = strings.GAME_NAME))
router.callback_query.filter(CurrentGameFilter(game_name = strings.GAME_NAME))