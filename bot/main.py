import asyncio
import logging
import os
import sys
from sqlalchemy.orm import Session

from bot.config import config
from bot.wb_client import WBClient
from bot.notifications import TelegramNotifier
from database.models import SessionLocal, init_db
from database.repository import FineRepository, NotificationRepository

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Настройка логирования
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("bot.log", encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger(__name__)


class WBFineBot:
    """Главный класс бота мониторинга"""

    def __init__(self):
        # Проверяем конфигурацию
        try:
            config.validate()
            config.print_config()
        except ValueError as e:
            logger.error(f"Ошибка конфигурации: {e}")
            raise

        # Инициализируем компоненты
        self.wb_client = WBClient()
        self.notifier = TelegramNotifier()

        # Инициализируем БД
        try:
            init_db()
            logger.info("База данных инициализирована")
        except Exception as e:
            logger.error(f"Ошибка инициализации БД: {e}")
            raise

        logger.info("Бот инициализирован")

    def get_db(self) -> Session:
        """Получение сессии БД"""
        return SessionLocal()

    async def check_fines(self):
        """Проверка новых штрафов"""
        logger.info("Проверка новых штрафов...")

        db = self.get_db()
        try:
            # Получаем штрафы за последний день
            fines = self.wb_client.get_fines(days_back=1)

            if not fines:
                logger.info("Штрафов не обнаружено")
                return 0

            # Обрабатываем штрафы
            fine_repo = FineRepository(db)
            notif_repo = NotificationRepository(db)
            new_fines_count = 0

            for fine_data in fines:
                try:
                    # Сохраняем штраф
                    fine, is_new = fine_repo.save_fine(fine_data)

                    # Если штраф новый и ещё не уведомлён
                    if is_new and not fine.notified:
                        # Отправляем уведомление
                        success = await self.notifier.send_fine_alert(fine_data)

                        if success:
                            # Отмечаем как уведомлённый
                            fine_repo.mark_as_notified(fine.id)

                            # Логируем уведомление
                            notif_repo.log_notification(fine.id, "telegram", True)

                            new_fines_count += 1
                            logger.info(f"Новый штраф: {fine.type} - {fine.amount} руб")
                        else:
                            logger.error(
                                f"Не удалось отправить уведомление для {fine.id}"
                            )

                except Exception as e:
                    logger.error(
                        f"Ошибка обработки штрафа {fine_data.get('id', 'unknown')}: {e}"
                    )
                    continue

            # Статистика
            total_fines = fine_repo.get_fines_count()

            if new_fines_count > 0:
                logger.info(f"Обнаружено новых штрафов: {new_fines_count}")
                # Отправляем статус только если есть новые штрафы
                await self.notifier.send_status_message(new_fines_count, total_fines)
            else:
                logger.info(f"Проверено штрафов: {len(fines)}, новых: 0")

            return new_fines_count

        except Exception as e:
            logger.error(f"Ошибка при проверке: {e}", exc_info=True)
            return 0

        finally:
            db.close()

    async def run(self):
        """Основной цикл работы бота"""
        logger.info("Запуск бота мониторинга штрафов WB")

        # Проверяем подключения
        logger.info("Проверка подключений...")

        # Проверка API
        if not self.wb_client.test_connection():
            logger.error("Не удалось подключиться к API")
            return

        logger.info("Все подключения работают")

        # НЕ отправляем стартовое сообщение - убираем эту проблему

        # Основной цикл
        logger.info(f"Начинаю мониторинг (интервал: {config.CHECK_INTERVAL} сек)")
        logger.info("Для остановки нажмите Ctrl+C")

        try:
            while True:
                await self.check_fines()
                await asyncio.sleep(config.CHECK_INTERVAL)

        except KeyboardInterrupt:
            logger.info("Остановка бота по запросу пользователя")
        except Exception as e:
            logger.error(f"Критическая ошибка: {e}")
        finally:
            logger.info("Бот остановлен")


def main():
    """Точка входа"""
    try:
        bot = WBFineBot()
        asyncio.run(bot.run())
    except KeyboardInterrupt:
        print("\nПрограмма завершена")
    except Exception as e:
        print(f"Ошибка запуска: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
