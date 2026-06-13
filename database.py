import psycopg2
import os

# Данные для подключения
DB_USER = "hunter"
DB_PASSWORD = "hunter_password"
DB_NAME = "flathunter"
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = "5432"

# 1. Единая функция для подключения к БД
def get_db_connection():
    return psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )

def init_db():
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        print("Успешное подключение к PostgreSQL!")

        # 2. Создаем таблицу для квартир
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS flats (
            id SERIAL PRIMARY KEY,
            url TEXT UNIQUE NOT NULL,
            title TEXT,
            price TEXT,
            metro TEXT,
            photo_url TEXT
        );
        """)

        # 3. Создаем таблицу для ссылок (исправили форматирование)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS search_urls (
            id SERIAL PRIMARY KEY,
            url TEXT UNIQUE NOT NULL
        );
        """)

        # Сохраняем изменения
        conn.commit()
        print("Таблицы 'flats' и 'search_urls' успешно созданы (или уже существуют)!")

    except Exception as e:
        print(f"Ошибка при работе с БД: {e}")
    finally:
        if conn:
            cursor.close()
            conn.close()

# Добавление квартиры в базу
def add_flat(url, title, price, metro, photo_url):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO flats (url, title, price, metro, photo_url) VALUES (%s, %s, %s, %s, %s)",
            (url, title, price, metro, photo_url)
        )
        conn.commit()
        return True # Успешно добавили
    except psycopg2.errors.UniqueViolation:
        return False # Такая квартира уже есть
    finally:
        cursor.close()
        conn.close()

# Устанавливает новую ссылку (и удаляет старую)
def set_search_url(url):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM search_urls")
        cursor.execute("INSERT INTO search_urls (url) VALUES (%s)", (url,))
        conn.commit()
        return True
    except Exception as e:
        print(f"Ошибка сохранения ссылки: {e}")
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()

# Получает текущую активную ссылку
def get_search_url():
    conn = get_db_connection()
    cursor = conn.cursor()
    # Берем единственную ссылку, которая там есть
    cursor.execute("SELECT url FROM search_urls LIMIT 1")
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    return row[0] if row else None

if __name__ == "__main__":
    init_db()