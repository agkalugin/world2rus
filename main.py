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
