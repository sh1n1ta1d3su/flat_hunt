import os
from dotenv import load_dotenv
from aiogram import Bot

# Загружаем секреты
load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
USER_ID = os.getenv("TELEGRAM_USER_ID")


async def send(area, metro, distance, clean_price, full_url, image_url):
    bot = Bot(token=TOKEN)
    try:
        # 1. Формируем текст (убрали строку с картинкой из текста)
        text = (
            f"🏠 <b>Новая квартира!</b>\n"
            f"💰 Цена: {clean_price}\n"
            f"📏 Площадь: {area}\n"
            f"🚇 Метро: {metro} ({distance})\n\n"
            f"🔗 <a href='{full_url}'>Перейти к объявлению</a>"
        )

        # 2. Если ссылка на картинку нормальная (из интернета), отправляем ФОТО с подписью
        if image_url.startswith("http"):
            await bot.send_photo(
                chat_id=USER_ID,
                photo=image_url,
                caption=text,  # Текст становится подписью под фото
                parse_mode="HTML"
            )
        else:
            # 3. Если фото нет (или оно из test.html), отправляем просто текст
            await bot.send_message(
                chat_id=USER_ID,
                text=text,
                parse_mode="HTML"
            )

        print("✅ Сообщение успешно отправлено!")

    except Exception as e:
        print(f"❌ Ошибка отправки: {e}")
    finally:
        await bot.session.close()