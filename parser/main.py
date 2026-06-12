import sys
import os
import time
import asyncio
import requests
from bs4 import BeautifulSoup

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import add_flat, init_db
from bot.bot import send


TARGET_URL = "https://realty.yandex.ru/sankt-peterburg_i_leningradskaya_oblast/snyat/kvartira/?priceMax=40000&areaMin=25&metroGeoId=20307&metroGeoId=20308&metroGeoId=20318&metroGeoId=20321&metroGeoId=20322&metroGeoId=20323&metroGeoId=20324&metroGeoId=20328&metroGeoId=20329&metroGeoId=20330&metroGeoId=20331&metroGeoId=20335&metroGeoId=20336&metroGeoId=20337&metroGeoId=20338&metroGeoId=20339&metroGeoId=20340&metroGeoId=20341&metroGeoId=101378&metroGeoId=114766&metroGeoId=114838&metroGeoId=114839&metroGeoId=189457"

# Маскируемся под живого пользователя, чтобы нас не забанили
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7"
}


def fetch_flats():
    print(f"[{time.strftime('%X')}] 📡 Идем на Яндекс...")

    try:
        # Cкачиваем реальную страницу
        response = requests.get(TARGET_URL, headers=HEADERS)
        response.raise_for_status()
        html_data = response.text
    except Exception as e:
        print(f"❌ Ошибка скачивания страницы: {e}")
        return

    # Парсим скачанный код
    soup = BeautifulSoup(html_data, "html.parser")
    flats = soup.find_all("li", class_="OffersSerpItem")

    if not flats:
        print("⚠️ Квартиры не найдены. Возможно, Яндекс выдал капчу или ссылка неверная.")
        return

    print(f"🔍 Найдено квартир: {len(flats)}")

    for flat in flats:
        price_block = flat.find(class_=lambda x: x and "OffersSerpItem__price" in x)
        link_tag = flat.find("a", class_=lambda x: x and "OffersSerpItem__link" in x)
        title_block = flat.find(class_=lambda x: x and "OffersSerpItemTitle__title" in x)
        metro_block = flat.find(class_=lambda x: x and "MetroStation__title" in x)
        distance_block = flat.find(class_=lambda x: x and "MetroWithTime__distance" in x)
        img_tag = flat.find("img")

        if price_block and link_tag:
            clean_price = price_block.text.replace("\xa0", " ")
            raw_url = link_tag.get("href")
            full_url = raw_url if raw_url.startswith("http") else f"https://realty.yandex.ru{raw_url}"

            area = title_block.text.replace("\xa0", " ").split("·")[0].strip() if title_block else "Площадь неизвестна"
            metro = metro_block.text if metro_block else "Метро не указано"
            distance = distance_block.text.replace("\xa0", " ") if distance_block else ""

            if img_tag and img_tag.get("src"):
                raw_img = img_tag.get("src")
                img_url = f"https:{raw_img}" if raw_img.startswith("//") else raw_img
            else:
                img_url = "Нет фото"

            # Работаем с БД и Телеграмом
            is_new = add_flat(full_url, area, clean_price, metro, img_url)

            if is_new:
                print(f"🆕 Новая квартира: {full_url}")
                asyncio.run(send(area, metro, distance, clean_price, full_url, img_url))


if __name__ == "__main__":
    print("🚀 Flat Hunter запущен в БОЕВОМ РЕЖИМЕ!")

    init_db()

    # 3. Бесконечный цикл мониторинга
    while True:
        fetch_flats()
        print("💤 Ждем 5 минут перед следующим запросом...\n")
        time.sleep(900)  # Пауза 15 минут