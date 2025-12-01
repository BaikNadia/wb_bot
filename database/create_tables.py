import sys
import os
from database.models import Base, engine
from sqlalchemy import text

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def create_tables():
    """Создание таблиц в PostgreSQL"""
    print("🔄 Создание таблиц в базе данных...")

    try:
        # Создаём таблицы через SQLAlchemy
        Base.metadata.create_all(bind=engine)
        print("✅ Таблицы созданы через SQLAlchemy")

        # Проверяем создание
        with engine.connect() as conn:
            result = conn.execute(
                text(
                    """
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name
            """
                )
            )
            tables = [row[0] for row in result]

            print(f"📊 Всего таблиц: {len(tables)}")
            for table in tables:
                print(f"  - {table}")

            # Проверяем нужные таблицы
            required_tables = ["fines", "notifications", "daily_stats"]
            for table in required_tables:
                if table in tables:
                    print(f"✅ Таблица '{table}' создана")
                else:
                    print(f"⚠️  Таблица '{table}' не найдена")

        return True

    except Exception as e:
        print(f"❌ Ошибка при создании таблиц: {e}")
        return False


def test_connection():
    """Тест подключения к БД"""
    from database.models import SessionLocal

    try:
        db = SessionLocal()
        # Простой запрос для проверки
        result = db.execute(text("SELECT 1"))
        print("✅ Подключение к БД успешно")
        db.close()
        return True
    except Exception as e:
        print(f"❌ Ошибка подключения: {e}")
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("СОЗДАНИЕ ТАБЛИЦ БАЗЫ ДАННЫХ")
    print("=" * 60)

    if test_connection():
        if create_tables():
            print("\n🎉 База данных готова к работе!")
        else:
            print("\n❌ Не удалось создать таблицы")
    else:
        print("\n❌ Не удалось подключиться к БД")
        print("Проверьте:")
        print("1. Запущен ли PostgreSQL: docker-compose up -d")
        print("2. Правильность настроек в .env файле")
        print("3. Существует ли база данных 'wb_fines_db'")
