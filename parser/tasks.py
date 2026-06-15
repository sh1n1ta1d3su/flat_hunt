import sys
import os
import asyncio
import requests
from bs4 import BeautifulSoup

# Добавляем корень проекта в пути
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import add_flat, init_db, get_search_url
from bot.bot import send
from celery_app import app

# Маскируемся под живого пользователя
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7"
}

def format_price(raw_price_text):
    if not raw_price_text:
        return "Цена не указана"
    return raw_price_text.replace("\xa0", " ").strip()

@app.task(name="parser.tasks.parse_flats_task")
def parse_flats_task():
    print("Celery Worker взял задачу:  Идем на Яндекс...")

    # Проверяем/создаем таблицу в БД перед запуском парсера
    init_db()
    target_url = get_search_url()
    if not target_url:
        print(" Ссылка для поиска не задана. Жду команду /set в боте.")
        return

    print(f" Воркер взял задачу: Идем по ссылке: {target_url[:50]}...")
    # Делаем запрос
    response = requests.get(target_url, headers=HEADERS)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        flats = soup.find_all("li", class_="OffersSerpItem")
        print(f"🔍 Найдено квартир на странице: {len(flats)}\n")

        for flat in flats:
            # Ищем блоки
            price_block = flat.find(class_=lambda x: x and "OffersSerpItem__price" in x)
            link_tag = flat.find("a", class_=lambda x: x and "OffersSerpItem__link" in x)
            title_block = flat.find(class_=lambda x: x and "OffersSerpItemTitle__title" in x)
            metro_block = flat.find(class_=lambda x: x and "MetroStation__title" in x)
            distance_block = flat.find(class_=lambda x: x and "MetroWithTime__distance" in x)
            img_tag = flat.find("img")

            # Если базовые данные есть, обрабатываем
            if price_block and link_tag:
                clean_price = format_price(price_block.text)
                
                raw_url = link_tag.get("href")
                full_url = raw_url if raw_url.startswith("http") else f"https://realty.yandex.ru{raw_url}"

                # Квадратура
                if title_block:
                    full_title = title_block.text.replace("\xa0", " ")
                    area = full_title.split("·")[0].strip()
                else:
                    area = "Площадь неизвестна"

                # Метро и время
                metro = metro_block.text if metro_block else "Метро не указано"
                distance = distance_block.text.replace("\xa0", " ") if distance_block else ""

                # Фото
                if img_tag and img_tag.get("src"):
                    raw_img = img_tag.get("src")
                    img_url = f"https:{raw_img}" if raw_img.startswith("//") else raw_img
                else:
                    img_url = "Нет фото"

                # Пытаемся добавить в БД
                is_new = add_flat(full_url, area, clean_price, metro, img_url)
                if is_new:
                    print(f"🆕 Найдена новая квартира: {full_url}")
                    asyncio.run(send(area, metro, distance, clean_price, full_url, img_url))
                else:
                    print(f"Квартира уже есть в базе, пропускаем: {full_url}")
    else:
        print(f"Ошибка доступа к Яндексу: {response.status_code}")