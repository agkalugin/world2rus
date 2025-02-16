<<<<<<< HEAD
import logging
import requests
from bs4 import BeautifulSoup
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.utils import executor

# Настройки
TOKEN = "YOUR_BOT_TOKEN"
ADMIN_ID = 1418276861  # ID администратора
COMMISSION = 1.07  # Наценка 7%

# Инициализация бота
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)
logging.basicConfig(level=logging.INFO)

# Главное меню
menu = ReplyKeyboardMarkup(resize_keyboard=True)
menu.add(KeyboardButton("📦 Отправить заказ на выкуп"))
menu.add(KeyboardButton("💰 Рассчитать курс выкупа"))
menu.add(KeyboardButton("🚚 Условия доставки"))
menu.add(KeyboardButton("🛍️ Наши рекомендации по магазинам"))

# Запрос телефона
phone_request = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
phone_request.add(KeyboardButton("📱 Отправить номер телефона", request_contact=True))

# Функция получения курса валют с ЦБ РФ
def get_exchange_rate():
    url = "https://www.cbr.ru/scripts/XML_daily.asp"
    response = requests.get(url)
    response.encoding = 'windows-1251'  # Указываем кодировку ответа

    soup = BeautifulSoup(response.text, "xml")
    usd = float(soup.find("Valute", {"ID": "R01235"}).Value.text.replace(",", ".")) * COMMISSION
    eur = float(soup.find("Valute", {"ID": "R01239"}).Value.text.replace(",", ".")) * COMMISSION

    return round(usd, 2), round(eur, 2)

# Обработчик команды /start
@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    await message.answer("Привет! Выберите действие:", reply_markup=menu)

# Обработчик расчета курса валют
@dp.message_handler(lambda message: message.text == "💰 Рассчитать курс выкупа")
async def calculate_exchange_rate(message: types.Message):
    try:
        usd_rate, eur_rate = get_exchange_rate()
        text = (
            f"📊 *Актуальный курс с наценкой 7%:*\n"
            f"💵 1 USD = {usd_rate} ₽\n"
            f"💶 1 EUR = {eur_rate} ₽\n\n"
            f"Этот курс применяется при расчете выкупа товаров."
        )
        await message.answer(text, parse_mode="Markdown")
    except Exception as e:
        logging.exception("Ошибка получения курса валют: %s", e)
        await message.answer("❌ Не удалось получить курс валют. Попробуйте позже.")

# Обработчик "Условия доставки"
@dp.message_handler(lambda message: message.text == "🚚 Условия доставки")
async def delivery_terms(message: types.Message):
    text = (
        "📦 *Доставка:*\n"
        "Грузы отправляются из США и Европы консолидированными партиями примерно раз в 7-10 дней. В зависимости от товаров, могут ехать разными маршрутами, через третьи страны и другими условиями. Как правило, все пошлины мы платим сами и они уже входят в стандартную дельту цены доставки. Вес мы не округляем.\n\n"
        "💰 *Стоимость доставки:*\n"
        "🇺🇸 США  — 2200-2500р. за 1кг груза\n"
        "🇪🇺 Европа — 1800-2000р. за 1кг груза\n"
        "🇮🇹 Италия — 2000-2200р. за 1кг груза\n"
        "🇬🇧 Великобритания — 2200-2400р. за 1кг груза\n\n"
        "⏳ *Сроки доставки:*\n"
        "Стандартные для всех стран — 35-40 дней.\n\n"
        "💳 *Оплата:*\n"
        "✅ Цена товара (цена за выкуп) оплачивается непосредственно перед выкупом вашего товара.\n"
        "✅ Комиссия (5-15% от цены вашего товара) оплачивается при поступлении груза в СПб и произведенных окончательных расчетов.\n"
        "✅ Цена доставки оплачивается при поступлении в СПб, исходя из физического веса вашего заказа.\n\n"
        "🔔 Если необходимы уведомления о процессе перемещения вашего заказа, пока это возможно только по вашему запросу."
    )
    await message.answer(text, parse_mode="Markdown")

# Обработчик "Наши рекомендации по магазинам"
@dp.message_handler(lambda message: message.text == "🛍️ Наши рекомендации по магазинам")
async def store_recommendations(message: types.Message):
    text = (
        "🛍️ *Рекомендуемые магазины:*\n"
        "🛒 Amazon - https://www.amazon.com\n"
        "🛒 eBay - https://www.ebay.com\n"
        "🛒 ASOS - https://www.asos.com\n"
        "🛒 6PM - https://www.6pm.com\n\n"
        "Мы выкупаем товары из любых магазинов. Присылайте ссылки!"
    )
    await message.answer(text, parse_mode="Markdown")

# Запуск бота
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
=======
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
>>>>>>> f77f98e (Первый коммит для бота)
