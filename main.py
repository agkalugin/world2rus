import os
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils import executor

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Получаем токен из переменных окружения
TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise ValueError("BOT_TOKEN не задан. Установите переменную окружения BOT_TOKEN.")

bot = Bot(token=TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# Определяем состояния для заказа
class OrderStates(StatesGroup):
    waiting_for_link = State()
    waiting_for_screenshot = State()

# Обработчик команды /start
@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    await message.answer("Привет! Отправьте, пожалуйста, ссылку на товар.")
    await OrderStates.waiting_for_link.set()

# Обработчик для получения ссылки на товар
@dp.message_handler(state=OrderStates.waiting_for_link)
async def process_link(message: types.Message, state: FSMContext):
    if 'http' not in message.text.lower():
        await message.answer("Пожалуйста, отправьте корректную ссылку, содержащую 'http'.")
        return
    await state.update_data(link=message.text.strip())
    await OrderStates.waiting_for_screenshot.set()
    await message.answer("Спасибо! Теперь отправьте скриншот, на котором видны выбранные параметры (размер, цвет, цена).")

# Обработчик для получения скриншота
@dp.message_handler(content_types=types.ContentType.PHOTO, state=OrderStates.waiting_for_screenshot)
async def process_screenshot(message: types.Message, state: FSMContext):
    # Отправляем сообщение, что фото получено
    await message.answer("Фото получено! Обрабатываю заказ...")

    # Получаем фотографию (наиболее качественную)
    photo = message.photo[-1]
    await state.update_data(screenshot_file_id=photo.file_id)
    data = await state.get_data()
    link = data.get('link')
    
    # Формируем сообщение для администратора
    admin_username = '@ikalugin'  # Админ — @ikalugin
    order_info = (
        f"Новый заказ от {message.from_user.full_name} (ID: {message.from_user.id}):\n"
        f"Ссылка: {link}\n"
        f"Скриншот с параметрами прилагается ниже."
    )
    
    try:
        # Попытка отправить уведомление админу
        await bot.send_photo(chat_id=admin_username, photo=photo.file_id, caption=order_info)
        await message.answer("Заявка принята! Она будет обработана в течение 1-2 часов, и администратор свяжется с вами.")
    except Exception as e:
        # Если возникает ошибка, отправляем информацию об ошибке пользователю (и логируем её)
        await message.answer("Произошла ошибка при отправке уведомления админу. Попробуйте позже.")
        logging.exception("Ошибка при отправке уведомления админу: %s", e)
    
    await state.finish()

# Если пользователь отправляет не фотографию в состоянии ожидания скриншота
@dp.message_handler(lambda message: message.content_type != 'photo', state=OrderStates.waiting_for_screenshot)
async def invalid_screenshot(message: types.Message):
    await message.answer("Пожалуйста, отправьте скриншот в виде фотографии, чтобы мы могли увидеть выбранные параметры товара.")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)