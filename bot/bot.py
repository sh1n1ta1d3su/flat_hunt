import asyncio
import os
import sys
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import set_search_url, get_search_url, init_db

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
USER_ID = int(os.getenv("TELEGRAM_USER_ID","0"))


async def send(area, metro, distance, clean_price, full_url, img_url):
    bot = Bot(token=BOT_TOKEN)

    # Формируем красивый текст
    text = (
        f"🏠 <b>Новая квартира!</b>\n"
        f"💰 Цена: {clean_price}\n"
        f"📏 Площадь: {area}\n"
        f"🚇 Метро: {metro} ({distance})\n\n"
        f"🔗 <a href='{full_url}'>Перейти к объявлению</a>"
    )

    try:
        # Если ссылка на картинку нормальная, отправляем ФОТО с подписью
        if img_url.startswith("http"):
            await bot.send_photo(
                chat_id=USER_ID,
                photo=img_url,
                caption=text,
                parse_mode="HTML"
            )
        else:
            # Если фото нет, отправляем просто текст
            await bot.send_message(
                chat_id=USER_ID,
                text=text,
                parse_mode="HTML"
            )
    finally:
        # Обязательно закрываем сессию, чтобы не было таймаутов
        await bot.session.close()

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
    bot = Bot(token=BOT_TOKEN)
    print("🤖 Бот запущен!")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())