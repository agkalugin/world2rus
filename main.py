import os
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils import executor
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Получение токена бота из переменных окружения
TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise ValueError("BOT_TOKEN не задан. Установите переменную окружения BOT_TOKEN.")

# ID администратора
ADMIN_ID = 1418276861  

bot = Bot(token=TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# Определяем состояния для заказа
class OrderStates(StatesGroup):
    waiting_for_link = State()
    waiting_for_screenshot = State()
    waiting_for_telegram_id = State()
    waiting_for_phone = State()

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
    photo = message.photo[-1]
    await state.update_data(screenshot_file_id=photo.file_id)

    # Запросить ID в Telegram
    await OrderStates.waiting_for_telegram_id.set()
    await message.answer("Введите ваш ID в Telegram или username (например, @username).")

# Обработчик для получения ID Telegram
@dp.message_handler(state=OrderStates.waiting_for_telegram_id)
async def process_telegram_id(message: types.Message, state: FSMContext):
    await state.update_data(telegram_id=message.text.strip())

    # Создание клавиатуры для отправки номера телефона
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    keyboard.add(KeyboardButton("Отправить номер телефона", request_contact=True))

    await OrderStates.waiting_for_phone.set()
    await message.answer("Теперь отправьте ваш номер телефона, используя кнопку ниже.", reply_markup=keyboard)

# Обработчик для получения номера телефона
@dp.message_handler(content_types=types.ContentType.CONTACT, state=OrderStates.waiting_for_phone)
async def process_phone(message: types.Message, state: FSMContext):
    phone_number = message.contact.phone_number
    await state.update_data(phone=phone_number)

    data = await state.get_data()
    link = data.get('link')
    telegram_id = data.get('telegram_id')
    screenshot_file_id = data.get('screenshot_file_id')

    # Формируем сообщение для администратора
    order_info = (
        f"📦 *Новый заказ*\n"
        f"👤 Пользователь: {message.from_user.full_name} (ID: {message.from_user.id})\n"
        f"🔗 Ссылка: {link}\n"
        f"📬 Telegram ID: {telegram_id}\n"
        f"📞 Телефон: {phone_number}\n"
        f"📸 Скриншот прилагается ниже."
    )

    try:
        # Отправляем уведомление админу с фото
        await bot.send_photo(chat_id=ADMIN_ID, photo=screenshot_file_id, caption=order_info, parse_mode="Markdown")
        await message.answer("✅ Заявка принята! Она будет обработана в течение 1-2 часов, и администратор свяжется с вами.", reply_markup=types.ReplyKeyboardRemove())
    except Exception as e:
        logging.exception("Ошибка при отправке уведомления админу: %s", e)
        await message.answer("❌ Произошла ошибка при отправке уведомления админу. Попробуйте позже.", reply_markup=types.ReplyKeyboardRemove())

    await state.finish()

# Если пользователь отправляет не фотографию в состоянии ожидания скриншота
@dp.message_handler(lambda message: message.content_type != 'photo', state=OrderStates.waiting_for_screenshot)
async def invalid_screenshot(message: types.Message):
    await message.answer("Пожалуйста, отправьте скриншот в виде фотографии, чтобы мы могли увидеть выбранные параметры товара.")

# Если пользователь отправляет не контакт в состоянии ожидания номера телефона
@dp.message_handler(lambda message: message.content_type != 'contact', state=OrderStates.waiting_for_phone)
async def invalid_phone(message: types.Message):
    await message.answer("⚠️ Пожалуйста, используйте кнопку 'Отправить номер телефона' для передачи контакта.")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)