import logging
from telegram import Bot
from telegram.error import TelegramError
from bot.config import config

logger = logging.getLogger(__name__)


class TelegramNotifier:
    """Отправка уведомлений в Telegram"""

    def __init__(self):
        self.bot = Bot(token=config.TELEGRAM_BOT_TOKEN)
        self.chat_id = config.TELEGRAM_CHAT_ID

    async def send_fine_alert(self, fine: dict) -> bool:
        """Отправка уведомления о штрафе"""
        try:
            message = self._format_message(fine)

            # Отправляем БЕЗ parse_mode и с очисткой текста
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=message,
                parse_mode=None,  # Важно: отключаем Markdown/HTML
            )

            logger.info(f"Уведомление отправлено: {fine['id']}")
            return True

        except TelegramError as e:
            logger.error(f"Ошибка отправки: {e}")

            # Пробуем отправить максимально простой текст
            try:
                simple_text = (
                    f"НОВЫЙ ШТРАФ WB\n"
                    f"Тип: {fine['type']}\n"
                    f"Сумма: {fine['amount']} руб\n"
                    f"ID: {fine['id']}"
                )

                await self.bot.send_message(chat_id=self.chat_id, text=simple_text)
                logger.info(f"Уведомление отправлено (простая версия): {fine['id']}")
                return True
            except TelegramError as e2:
                logger.error(f"Ошибка отправки простой версии: {e2}")
                return False

    def _format_message(self, fine: dict) -> str:
        """Форматирование сообщения - БЕЗ спецсимволов Markdown"""
        # Очищаем текст от потенциальных символов Markdown
        clean_type = (
            fine["type"]
            .replace("*", "")
            .replace("_", "")
            .replace("`", "")
            .replace("[", "")
            .replace("]", "")
        )

        return f"""Новый штраф Wildberries

Тип нарушения: {clean_type}
Сумма штрафа: {fine['amount']} рублей
Дата: {fine['date'][:10]}
Номер заказа: {fine.get('order_id', 'не указан')}
Статус: {fine['status']}
ID штрафа: {fine['id']}

Мониторинг активен"""

    async def send_status_message(self, new_fines: int, total_fines: int):
        """Отправка статусного сообщения"""
        try:
            message = (
                f"Статус мониторинга WB\n\n"
                f"Новых штрафов: {new_fines}\n"
                f"Всего в базе: {total_fines}\n"
                f"Режим работы: {config.MODE}\n"
                f"Бот активен"
            )

            await self.bot.send_message(chat_id=self.chat_id, text=message)

            return True

        except TelegramError as e:
            logger.error(f"Ошибка отправки статуса: {e}")
            return False
