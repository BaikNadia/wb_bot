import os
from dotenv import load_dotenv
from urllib.parse import quote_plus

load_dotenv()


class Config:
    # === Режим работы ===
    MODE = os.getenv("APP_MODE", "MOCK")  # MOCK или PROD

    # === База данных ===
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "5432")
    DB_NAME = os.getenv("DB_NAME", "wb_fines_db")
    DB_USER = os.getenv("DB_USER", "postgres")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")

    # === Telegram ===
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
    TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

    # === API Wildberries ===
    WB_API_KEY = os.getenv("WB_API_KEY", "")

    # === Настройки приложения ===
    CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", 30))  # 30 секунд для тестов
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    HIGH_FINE_THRESHOLD = float(os.getenv("HIGH_FINE_THRESHOLD", 5000))

    # === Вычисляемые свойства ===
    @property
    def WB_API_URL(self):
        """URL API в зависимости от режима"""
        return (
            "http://localhost:8000"
            if self.MODE == "MOCK"
            else "https://suppliers-api.wildberries.ru"
        )

    @property
    def DATABASE_URL(self):
        """URL подключения к БД с экранированием пароля"""
        if self.DB_PASSWORD:
            password_escaped = quote_plus(self.DB_PASSWORD)
        else:
            password_escaped = ""

        return f"postgresql://{self.DB_USER}:{password_escaped}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    def validate(self):
        """Проверка конфигурации"""
        errors = []

        # Проверка Telegram
        if not self.TELEGRAM_BOT_TOKEN or self.TELEGRAM_BOT_TOKEN == "ваш_токен_бота":
            errors.append("Не настроен TELEGRAM_BOT_TOKEN в .env файле")

        if not self.TELEGRAM_CHAT_ID or self.TELEGRAM_CHAT_ID == "ваш_chat_id":
            errors.append("Не настроен TELEGRAM_CHAT_ID в .env файле")

        # Проверка режима
        if self.MODE not in ["MOCK", "PROD"]:
            errors.append(f"Неверный APP_MODE: {self.MODE}. Должно быть MOCK или PROD")

        # Для PROD режима нужен API ключ
        if self.MODE == "PROD" and not self.WB_API_KEY:
            errors.append("Для PROD режима нужен WB_API_KEY")

        if errors:
            raise ValueError("\n".join([f"❌ {error}" for error in errors]))

        return True

    def print_config(self):
        """Вывод конфигурации"""
        print("=" * 50)
        print("⚙️  КОНФИГУРАЦИЯ БОТА")
        print("=" * 50)

        config_info = {
            "Режим": self.MODE,
            "База данных": f"{self.DB_NAME} на {self.DB_HOST}:{self.DB_PORT}",
            "Пользователь БД": self.DB_USER,
            "Telegram": (
                "✅ Настроен"
                if self.TELEGRAM_BOT_TOKEN and self.TELEGRAM_CHAT_ID
                else "❌ Не настроен"
            ),
            "API URL": self.WB_API_URL,
            "Интервал проверки": f"{self.CHECK_INTERVAL} сек",
            "Порог уведомлений": f"{self.HIGH_FINE_THRESHOLD} руб",
        }

        for key, value in config_info.items():
            print(f"{key:25}: {value}")

        print("=" * 50)


# Создаём экземпляр конфигурации
config = Config()
