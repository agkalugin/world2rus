import os
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor

TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise ValueError("BOT_TOKEN не задан. Установите переменную окружения BOT_TOKEN.")

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

# Словарь для хранения временных данных пользователей
user_data = {}

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    user_data[message.from_user.id] = {}
    await message.answer("Привет! Отправьте ссылку на товар.")

@dp.message_handler(lambda message: 'http' in message.text.lower())
async def handle_link(message: types.Message):
    # Сохраняем ссылку в данных пользователя
    user_data[message.from_user.id]['link'] = message.text.strip()
    await message.answer("Спасибо! Теперь отправьте параметры товара (например, цвет, размер и т.д.).")

@dp.message_handler()
async def handle_params(message: types.Message):
    # Если ссылка уже была получена, считаем, что это параметры
    if message.from_user.id in user_data and 'link' in user_data[message.from_user.id]:
        user_data[message.from_user.id]['params'] = message.text.strip()
        # Отправляем уведомление администратору, можно заменить ID на свой
        admin_id = 123456789  
        order_info = f"Новый заказ от {message.from_user.full_name} (ID: {message.from_user.id}):\nСсылка: {user_data[message.from_user.id]['link']}\nПараметры: {user_data[message.from_user.id]['params']}"
        await bot.send_message(admin_id, order_info)
        await message.answer("Ваш заказ принят! Мы свяжемся с вами для уточнения деталей.")
        # Очистка данных пользователя
        del user_data[message.from_user.id]
    else:
        # Если ссылка не была получена, напомним пользователю
        await message.answer("Пожалуйста, сначала отправьте ссылку на товар.")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)