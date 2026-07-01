import asyncio
import os
import sys

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.client.session.aiohttp import AiohttpSession

from aiohttp import ClientSession
from aiohttp_socks import ProxyConnector

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import set_search_url, get_search_url, init_db


BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
USER_ID = int(os.getenv("TELEGRAM_USER_ID", "0"))

proxy_url = "socks5://oRJ0UJ:8TBbVX@45.157.122.244:8000"

dp = Dispatcher()

_bot = None


def get_bot():
    global _bot

    if _bot is None:
        from aiohttp_socks import ProxyConnector
        from aiohttp import ClientSession
        from aiogram.client.session.aiohttp import AiohttpSession

        proxy_url = os.getenv(
            "PROXY_URL",
            "socks5://oRJ0UJ:8TBbVX@45.157.122.244:8000"
        )

        connector = ProxyConnector.from_url(proxy_url)
        aiohttp_session = ClientSession(connector=connector)
        session = AiohttpSession(client_session=aiohttp_session)

        _bot = Bot(token=BOT_TOKEN, session=session)

    return _bot

async def send(area, metro, distance, clean_price, full_url, img_url):
    bot = get_bot()
    text = (
        f"🏠 <b>Новая квартира!</b>\n"
        f"💰 Цена: {clean_price}\n"
        f"📏 Площадь: {area}\n"
        f"🚇 Метро: {metro} ({distance})\n\n"
        f"🔗 <a href='{full_url}'>Перейти к объявлению</a>"
    )

    if img_url.startswith("http"):
        await bot.send_photo(
            chat_id=USER_ID,
            photo=img_url,
            caption=text,
            parse_mode="HTML"
        )
    else:
        await bot.send_message(
            chat_id=USER_ID,
            text=text,
            parse_mode="HTML"
        )
dp = Dispatcher()


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        "Привет! Отправь мне команду:\n`/set <ссылка>` — чтобы задать фильтр.\n`/current` — посмотреть текущую ссылку.",
        parse_mode="Markdown")


@dp.message(Command("set"))
async def cmd_set(message: types.Message):
    if message.from_user.id != USER_ID:
        return await message.answer("Я слушаюсь только хозяина.")

    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        return await message.answer("❌ Пример:\n/set https://realty.yandex.ru/...")

    url = parts[1]
    if "realty.yandex.ru" not in url:
        return await message.answer("❌ Кидай только ссылку на Яндекс Недвижимость!")

    if set_search_url(url):
        await message.answer("✅ Ссылка обновлена! Теперь я мониторю только её.")
    else:
        await message.answer("❌ Произошла ошибка при сохранении.")


@dp.message(Command("current"))
async def cmd_current(message: types.Message):
    url = get_search_url()
    if url:
        await message.answer(f"🔍 Сейчас я мониторю эту ссылку:\n\n{url}")
    else:
        await message.answer("📭 Ссылка не задана. Задай её командой /set")

async def main():
    init_db()
    print("Бот запущен!")
    await dp.start_polling(get_bot())

if __name__ == "__main__":
    asyncio.run(main())