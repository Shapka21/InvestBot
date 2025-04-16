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
    keyboard=[
        [KeyboardButton(text="Составить портфель"),
         KeyboardButton(text="Узнать информацию об акции")],
    ],
    resize_keyboard=True
)

main_keyboard2 = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Минимальная волатильность"),
         KeyboardButton(text="Максимальный коэффициент Шарпа"),
         KeyboardButton(text="Главное меню")],
    ],
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
async def contacts(message: types.Message):
    await message.answer('Какой портфель ты хочешь сделать?',
                         reply_markup=main_keyboard2)


@router.message(F.text =="Минимальная волатильность")
async def contacts(message: types.Message, state: FSMContext):
    await message.answer(tx.request_money())
    await state.set_state(UserStates.Money_minvol)


@router.message(StateFilter(UserStates.Money_minvol))
async def save_user_name(message: types.Message, state: FSMContext):
    if message.text.lower() == 'отмена':
        await message.answer(tx.start_make_portfolio())
        await state.clear()
    else:
        if '/' not in message.text:
            if message.text.isdigit():
                amount = int(message.text)
                if 1000 <= amount <= 10000000:
                    try:
                        portfolio, rest = algos.min_volantily(algos.stocks, amount)
                        await message.answer(tx.make_portfolio_minvol(portfolio, rest))
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


@router.message(F.text =="Максимальный коэффициент Шарпа")
async def contacts(message: types.Message, state: FSMContext):
    await message.answer(tx.request_money())
    await state.set_state(UserStates.Money_maxsharp)


@router.message(StateFilter(UserStates.Money_maxsharp))
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
                        portfolio, rest = algos.max_sharp(algos.stocks, amount)
                        await message.answer(tx.make_portfolio_maxsharp(portfolio, rest))
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


@router.message(F.text =="Узнать информацию об акции")
async def contacts(message: types.Message, state: FSMContext):
    await message.answer(tx.request_stock_name())
    await state.set_state(UserStates.Stock)


@router.message(StateFilter(UserStates.Stock))
async def answer(message: types.Message, state: FSMContext):
    if message.text.lower() == 'отмена':
        await message.answer(tx.return_main())
        await state.clear()
    else:
        if '/' not in message.text:
            try:
                mu, Sigma, latest_prices, flag = algos.info_stock(message.text)
                if flag:
                    await message.answer(tx.get_info_stocks(mu, Sigma, latest_prices))
                else:
                    await message.answer(tx.bad_stock())
            except Exception as e:
                await message.answer("Произошла ошибка при обработке запроса.")
                print(f"Error: {e}")
            finally:
                await state.clear()
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