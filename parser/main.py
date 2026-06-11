import sys
import os
import asyncio # Обязательно нужен для запуска бота!

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import add_flat # Проверь, правильно ли у тебя импортируется БД
from bs4 import BeautifulSoup

# У тебя импорт может отличаться (зависит от того, как назван файл бота)
from bot.bot import send 

# Открываем наш локальный файл
with open("test.html", "r", encoding="utf-8") as file:
    html_data = file.read()

soup = BeautifulSoup(html_data, "html.parser")
flats = soup.find_all("li", class_="OffersSerpItem")

print(f"🔍 Найдено квартир на странице: {len(flats)}\n")

for flat in flats:
    # --- 1. ИЩЕМ БЛОКИ ---
    price_block = flat.find(class_=lambda x: x and "OffersSerpItem__price" in x)
    link_tag = flat.find("a", class_=lambda x: x and "OffersSerpItem__link" in x)
    title_block = flat.find(class_=lambda x: x and "OffersSerpItemTitle__title" in x)
    metro_block = flat.find(class_=lambda x: x and "MetroStation__title" in x)
    distance_block = flat.find(class_=lambda x: x and "MetroWithTime__distance" in x)
    img_tag = flat.find("img")

    # --- 2. ОБРАБАТЫВАЕМ ДАННЫЕ ---
    if price_block and link_tag:
        clean_price = price_block.text.replace("\xa0", " ")
        raw_url = link_tag.get("href")
        full_url = raw_url if raw_url.startswith("http") else f"https://realty.yandex.ru{raw_url}"

        # КВАДРАТУРА
        if title_block:
            full_title = title_block.text.replace("\xa0", " ")
            area = full_title.split("·")[0].strip()
        else:
            area = "Площадь неизвестна"

        # МЕТРО И ВРЕМЯ
        metro = metro_block.text if metro_block else "Метро не указано"
        distance = distance_block.text.replace("\xa0", " ") if distance_block else ""

        # ФОТО
        if img_tag and img_tag.get("src"):
            raw_img = img_tag.get("src")
            img_url = f"https:{raw_img}" if raw_img.startswith("//") else raw_img
        else:
            img_url = "Нет фото"

        # --- 3. РАБОТА С БД И ТЕЛЕГРАМОМ ---
        # Пытаемся добавить в БД
        is_new = add_flat(full_url, area, clean_price, metro, img_url)

        if is_new:
            print(f"🆕 Новая квартира в БД: {full_url}")
            # МАГИЯ ЗДЕСЬ: запускаем асинхронную отправку правильно!
            asyncio.run(send(area, metro, distance, clean_price, full_url, img_url))
        else:
            print(f"🔕 Уже отправляли, пропускаем: {full_url}")

def get_html(url):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}

    print(f"Запрос на: {url}")
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        print("Страница скачана")
        return response.text
    else:
        print(f"Ошибка доступа: {response.status_code}")
        return None

def parse_html(html):
    soup = BeautifulSoup(html, "html.parser")

    title = soup.find("title").text
    print(f"Заголовок страницы: {title}")

    #Дальше будет логика поиска карточек квартир
    #flast = soup.find_all("div", class="listing-item")

