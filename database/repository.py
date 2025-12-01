from sqlalchemy.orm import Session
from datetime import datetime
from typing import List, Optional
from database.models import Fine, Notification


class FineRepository:
    def __init__(self, db: Session):
        self.db = db

    def save_fine(self, fine_data: dict) -> Optional[Fine]:
        """Сохранение или обновление штрафа"""
        try:
            # Проверяем, есть ли уже такой штраф
            fine = self.db.query(Fine).filter(Fine.id == fine_data["id"]).first()

            if fine:
                # Обновляем существующий
                fine.type = fine_data["type"]
                fine.amount = fine_data["amount"]
                fine.status = fine_data["status"]
                is_new = False
            else:
                # Создаём новый
                fine = Fine(
                    id=fine_data["id"],
                    date=datetime.fromisoformat(
                        fine_data["date"].replace("Z", "+00:00")
                    ),
                    type=fine_data["type"],
                    amount=fine_data["amount"],
                    order_id=fine_data.get("order_id", ""),
                    status=fine_data["status"],
                )
                self.db.add(fine)
                is_new = True

            self.db.commit()
            return fine, is_new

        except Exception as e:
            self.db.rollback()
            raise e

    def get_unnotified_fines(self) -> List[Fine]:
        """Получение неуведомленных штрафов"""
        return self.db.query(Fine).filter(Fine.notified == False).all()

    def mark_as_notified(self, fine_id: str):
        """Отметить штраф как уведомлённый"""
        fine = self.db.query(Fine).filter(Fine.id == fine_id).first()
        if fine:
            fine.notified = True
            self.db.commit()

    def get_fines_count(self) -> int:
        """Общее количество штрафов"""
        return self.db.query(Fine).count()


class NotificationRepository:
    def __init__(self, db: Session):
        self.db = db

    def log_notification(
        self, fine_id: str, channel: str = "telegram", success: bool = True
    ):
        """Логирование уведомления"""
        notification = Notification(fine_id=fine_id, channel=channel, success=success)
        self.db.add(notification)
        self.db.commit()
