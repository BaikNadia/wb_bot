import requests
import logging
from datetime import datetime, timedelta
from typing import List, Dict
from bot.config import config

logger = logging.getLogger(__name__)


class WBClient:
    """Клиент для работы с API Wildberries"""

    def __init__(self):
        self.base_url = config.WB_API_URL
        self.headers = {}

        # Добавляем API ключ только если он есть и не содержит не-ASCII символы
        if config.WB_API_KEY and config.WB_API_KEY != "ваш_api_ключ_здесь":
            # Проверяем, что ключ состоит только из ASCII символов
            try:
                config.WB_API_KEY.encode("ascii")
                self.headers = {"Authorization": config.WB_API_KEY}
            except UnicodeEncodeError:
                logger.warning("API ключ содержит не-ASCII символы, не использую")

        logger.info(f"WBClient: режим {config.MODE}, URL: {self.base_url}")

    def get_fines(self, days_back: int = 1) -> List[Dict]:
        """
        Получение штрафов

        Args:
            days_back: за сколько дней получать штрафы (только для MOCK режима)
        """
        try:
            params = {}

            if config.MODE == "MOCK":
                # Для мок-сервера используем параметр days
                params = {"days": str(days_back)}
                url = f"{self.base_url}/api/v3/fines"
            else:
                # Для реального API
                date_from = (
                    datetime.now() - timedelta(days=days_back)
                ).isoformat() + "Z"
                params = {"dateFrom": date_from}
                url = f"{self.base_url}/api/v3/fines"

            # Убираем не-ASCII символы из headers если есть
            safe_headers = {}
            for key, value in self.headers.items():
                if isinstance(value, str):
                    # Оставляем только ASCII символы
                    safe_value = "".join(c for c in value if ord(c) < 128)
                    safe_headers[key] = safe_value
                else:
                    safe_headers[key] = value

            response = requests.get(
                url, headers=safe_headers, params=params, timeout=30
            )

            if response.status_code == 200:
                data = response.json()
                fines = data.get("data", [])

                logger.info(f"Получено штрафов: {len(fines)}")

                # Логируем первый штраф для отладки
                if fines:
                    first_fine = fines[0]
                    logger.debug(
                        f"Пример штрафа: {first_fine['type']} - {first_fine['amount']} руб"
                    )

                return fines
            else:
                logger.error(
                    f"Ошибка API {response.status_code}: {response.text[:100]}"
                )
                return []

        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка подключения: {e}")
            return []
        except Exception as e:
            logger.error(f"Неизвестная ошибка: {e}")
            return []

    def test_connection(self) -> bool:
        """Тест подключения к API"""
        try:
            if config.MODE == "MOCK":
                response = requests.get(f"{self.base_url}/health", timeout=5)
                return response.status_code == 200
            else:
                response = requests.get(
                    f"{self.base_url}/api/v1/info", headers=self.headers, timeout=10
                )
                return response.status_code == 200
        except requests.exceptions.RequestException:
            return False
