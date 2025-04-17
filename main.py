import asyncio
from aiogram import Bot, Dispatcher, types, Router, F
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command, CommandStart

from aiogram.filters import StateFilter

from userStates import UserStates
from configure.env import config
import algorithms as algos
import texts as tx

bot = Bot(token=config['token'])
dp = Dispatcher(storage=MemoryStorage())

router = Router()

main_keyboard1 = ReplyKeyboardMarkup(
    keyboard= [[KeyboardButton(text="Составить портфель"),]],
    resize_keyboard=True
)


@router.message(CommandStart())
async def cmd_start(message: types.Message):
    await message.answer(
        tx.start_command(),
        reply_markup=main_keyboard1)


@router.message(F.text =="Главное меню")
async def contacts(message: types.Message):
    await message.answer(tx.return_main(), reply_markup=main_keyboard1)


@router.message(F.text =="Составить портфель")
async def contacts(message: types.Message, state: FSMContext):
    await message.answer(tx.request_money())
    await state.set_state(UserStates.Money)


@router.message(StateFilter(UserStates.Money))
async def answer(message: types.Message, state: FSMContext):
    if message.text.lower() == 'отмена':
        await message.answer(tx.start_make_portfolio())
        await state.clear()
    else:
        if '/' not in message.text:
            if message.text.isdigit():
                amount = int(message.text)
                if 1000 <= amount <= 10000000:
                    try:
                        portfolio = algos.create_investment_portfolio(algos.stocks, amount)
                        await message.answer(tx.make_portfolio(portfolio))
                    except Exception as e:
                        await message.answer("Произошла ошибка при обработке запроса.")
                        print(f"Error: {e}")
                    finally:
                        await state.clear()
                else:
                    await message.answer(tx.low_money())
            else:
                await message.answer(tx.is_not_digit())
        else:
            await message.answer(tx.bad_responce())
            await state.clear()


@router.message(F.text == "Дай пасхалку")
async def answer(message: types.Message):
    await message.answer('https://www.youtube.com/watch?v=dQw4w9WgXcQ')


@router.message()
async def answer(message: types.Message):
    await message.answer('Прости, я не понимаю тебя')


async def main():
    dp.include_router(router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())