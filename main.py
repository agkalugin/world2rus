import os
import logging
import requests
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

# Кнопки главного меню
main_menu = ReplyKeyboardMarkup(resize_keyboard=True)
main_menu.add("📦 Отправить заказ на выкуп")
main_menu.add("💲 Рассчитать курс выкупа")
main_menu.add("🚚 Условия доставки")
main_menu.add("🛍 Наши рекомендации по магазинам")

# Функция для получения курса валют с ЦБ РФ
def get_currency_rates():
    url = "https://www.cbr-xml-daily.ru/daily_json.js"
    try:
        response = requests.get(url).json()
        usd = round(response['Valute']['USD']['Value'] * 1.07, 2)
        eur = round(response['Valute']['EUR']['Value'] * 1.07, 2)
        return usd, eur
    except Exception as e:
        logging.error(f"Ошибка при получении курса валют: {e}")
        return None, None

# Обработчик команды /start
@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    await message.answer("Привет! Выберите действие:", reply_markup=main_menu)

# Обработчик кнопки "📦 Отправить заказ на выкуп"
@dp.message_handler(lambda message: message.text == "📦 Отправить заказ на выкуп")
async def send_order(message: types.Message):
    await message.answer("Отправьте, пожалуйста, ссылку на товар.")
    await OrderStates.waiting_for_link.set()

# Обработчик кнопки "💲 Рассчитать курс выкупа"
@dp.message_handler(lambda message: message.text == "💲 Рассчитать курс выкупа")
async def get_exchange_rate(message: types.Message):
    usd, eur = get_currency_rates()
    if usd and eur:
        await message.answer(f"💰 *Актуальный курс выкупа:*
🇺🇸 Доллар: {usd}₽
🇪🇺 Евро: {eur}₽", parse_mode="Markdown")
    else:
        await message.answer("Ошибка при получении курса валют. Попробуйте позже.")

# Обработчик кнопки "🚚 Условия доставки"
@dp.message_handler(lambda message: message.text == "🚚 Условия доставки")
async def send_shipping_info(message: types.Message):
    text = (
        "🚛 *Доставка:*
"
        "Грузы отправляются из США и Европы консолидированными партиями примерно раз в 7-10 дней."
        " В зависимости от товаров, могут ехать разными маршрутами, через третьи страны и другими условиями."
        " Как правило, все пошлины мы платим сами и они уже входят в стандартную дельту цены доставки. Вес мы не округляем.\n\n"
        "💰 *Стоимость доставки:*
"
        "🇺🇸 США  — 2200-2500₽ за 1 кг груза
"
        "🇪🇺 Европа — 1800-2000₽ за 1 кг груза
"
        "🇮🇹 Италия — 2000-2200₽ за 1 кг груза
"
        "🇬🇧 Великобритания — 2200-2400₽ за 1 кг груза
"
        "⏳ Сроки доставки стандартные для всех стран — 35-40 дней.\n\n"
        "💳 *Оплата:*
"
        "- Цена товара (выкуп) оплачивается перед выкупом.
"
        "- Комиссия (5-15% от цены) оплачивается при поступлении груза.
"
        "- Цена доставки оплачивается при поступлении в СПб, исходя из физического веса."
    )
    await message.answer(text, parse_mode="Markdown")

# Обработчик кнопки "🛍 Наши рекомендации по магазинам"
@dp.message_handler(lambda message: message.text == "🛍 Наши рекомендации по магазинам")
async def send_store_recommendations(message: types.Message):
    text = (
        "🛒 *Рекомендованные магазины:*
"
        "🇺🇸 *США:*
"
        "- Amazon — https://www.amazon.com/
"
        "- eBay — https://www.ebay.com/
"
        "- 6pm — https://www.6pm.com/
"
        "- Nike — https://www.nike.com/ru/\n\n"
        "🇪🇺 *Европа:*
"
        "- Zalando — https://www.zalando.de/
"
        "- ASOS — https://www.asos.com/ru/
"
        "- Adidas — https://www.adidas.de/\n\n"
        "🇬🇧 *Великобритания:*
"
        "- Farfetch — https://www.farfetch.com/ru/
"
        "- End Clothing — https://www.endclothing.com/\n\n"
        "Если у вас есть вопросы по магазину или товару, пишите в поддержку!"
    )
    await message.answer(text, parse_mode="Markdown")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
