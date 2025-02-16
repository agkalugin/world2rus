from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
import os

TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise ValueError("BOT_TOKEN не задан. Установите переменную окружения BOT_TOKEN.")

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.answer("Привет! Отправьте ссылку на товар.")

@dp.message_handler()
async def handle_order(message: types.Message):
    admin_id = 123456789  # Замените на свой Telegram ID
    await bot.send_message(admin_id, f"Новый заказ:\n{message.text}")
    await message.answer("Ваш заказ принят! Спасибо.")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)