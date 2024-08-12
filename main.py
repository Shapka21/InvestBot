from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import ReplyKeyboardMarkup
from aiogram.dispatcher import FSMContext

from userStates import UserStates
from configure.env import config
import algorithms as algos
import texts as tx

bot = Bot(token=config['token'])
dp = Dispatcher(bot, storage=MemoryStorage())


main_keyboard1 = ReplyKeyboardMarkup(resize_keyboard=True)
main_keyboard1.add('Составить портфель').add('Узнать иформацию об акции')

main_keyboard2 = ReplyKeyboardMarkup(resize_keyboard=True)
main_keyboard2.add('Минимальная волантильность').add('Максимальный коэффициент Шарпа').add('Главное меню')


@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    await message.answer(
        tx.start_command(),
        reply_markup=main_keyboard1)


@dp.message_handler(text='Главное меню')
async def contacts(message: types.Message):
    await message.answer(tx.return_main(), reply_markup=main_keyboard1)


@dp.message_handler(text='Составить портфель')
async def contacts(message: types.Message):
    await message.answer('Какой портфель ты хочешь сделать?',
                         reply_markup=main_keyboard2)


@dp.message_handler(text='Минимальная волантильность')
async def contacts(message: types.Message):
    await message.answer(tx.request_money())
    await UserStates.Money_minvol.set()


@dp.message_handler(state=UserStates.Money_minvol)
async def save_user_name(message: types.Message, state: FSMContext):
    if message.text == 'отмена':
        await message.answer(tx.start_make_portfolio())
        await state.finish()
    else:
        if '/' not in message.text:
            if message.text.isdigit():
                if int(message.text) >= 1000 and int(message.text) <= 10000000:
                    portfolio, rest = algos.min_volantily(algos.stocks, int(message.text))
                    await message.answer(tx.make_portfolio_minvol(portfolio, rest))
                    await state.finish()
                else:
                    await message.answer(tx.low_money())
            else:
                await message.answer(tx.is_not_digit())
        else:
            await message.answer(tx.bad_responce())
            await state.finish()


@dp.message_handler(text='Максимальный коэффициент Шарпа')
async def contacts(message: types.Message):
    await message.answer(tx.request_money())
    await UserStates.Money_maxsharp.set()


@dp.message_handler(state=UserStates.Money_maxsharp)
async def answer(message: types.Message, state: FSMContext):
    if message.text == 'отмена':
        await message.answer(tx.start_make_portfolio())
        await state.finish()
    else:
        if '/' not in message.text:
            if message.text.isdigit():
                if int(message.text) >= 1000:
                    portfolio, rest = algos.max_sharp(algos.stocks, int(message.text))
                    await message.answer(tx.make_portfolio_maxsharp(portfolio, rest))
                    await state.finish()
                else:
                    await message.answer(tx.low_money())
            else:
                await message.answer(tx.is_not_digit())
        else:
            await message.answer(tx.bad_responce())
            await state.finish()


@dp.message_handler(text='Узнать иформацию об акции')
async def contacts(message: types.Message):
    await message.answer(tx.request_stock_name())
    await UserStates.Stock.set()


@dp.message_handler(state=UserStates.Stock)
async def answer(message: types.Message, state: FSMContext):
    if message.text == 'отмена':
        await message.answer(tx.return_main())
        await state.finish()
    else:
        if '/' not in message.text:
                mu, Sigma, latest_prices, flag = algos.info_stock(message.text)
                if flag:
                    await message.answer(tx.get_info_stocks(mu, Sigma, latest_prices))
                else:
                    await message.answer(tx.bad_stock())
                await state.finish()
        else:
            await message.answer(tx.bad_responce())
            await state.finish()


@dp.message_handler(text='Дай пасхалку')
async def answer(message: types.Message):
    await message.answer('https://www.youtube.com/watch?v=dQw4w9WgXcQ')


@dp.message_handler()
async def answer(message: types.Message):
    await message.answer('Прости, я не понимаю тебя')


if __name__ == '__main__':
    executor.start_polling(dp)
