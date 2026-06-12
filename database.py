import psycopg2
import os

# Данные для подключения (ровно те же, что мы писали в docker-compose.yml)
DB_USER = "hunter"
DB_PASSWORD = "hunter_password"
DB_NAME = "flathunter"
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = "5432"


def init_db():
    conn = None
    try:
        # 1. Устанавливаем соединение с базой
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        # Курсор — это как мышка или указатель в БД, который выполняет команды
        cursor = conn.cursor()
        print("✅ Успешное подключение к PostgreSQL!")

        # 2. Пишем SQL-запрос на создание таблицы
        create_table_query = """
        CREATE TABLE IF NOT EXISTS flats (
            id SERIAL PRIMARY KEY,
            url TEXT UNIQUE NOT NULL,
            title TEXT,
            price TEXT,
            metro TEXT,
            photo_url TEXT
            );
            """

        # 3. Выполняем запрос и сохраняем (коммитим) изменения
        cursor.execute(create_table_query)
        conn.commit()
        print("✅ Таблица 'flats' успешно создана (или уже существует)!")

    except Exception as e:
        print(f"❌ Ошибка при работе с БД: {e}")
    finally:
        # 4. Правило хорошего тона: всегда закрываем соединение
        if conn:
            cursor.close()
            conn.close()

def add_flat(url, title, price, metro, photo_url):
    conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT)
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

if __name__ == "__main__":
    init_db()