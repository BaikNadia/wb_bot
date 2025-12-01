from fastapi import FastAPI
from datetime import datetime
import random
from typing import List
from pydantic import BaseModel

app = FastAPI(title="Mock WB API")


# Модели
class Fine(BaseModel):
    id: str
    date: str
    type: str
    amount: float
    order_id: str
    status: str


class FinesResponse(BaseModel):
    data: List[Fine]


# Определяем fine_types ДО использования
fine_types = [
    ("Просрочка поставки", 1000, 5000),
    ("Несоответствие упаковки", 500, 3000),
    ("Брак товара", 2000, 10000),
    ("Нарушение сроков", 1500, 8000),
    ("Ошибка в документах", 300, 2000),
]


# Генератор штрафов
def generate_fines(count: int = 3):
    """Генерация тестовых штрафов с уникальными ID"""
    fines = []

    for i in range(count):
        fine_type, min_amount, max_amount = random.choice(fine_types)

        # Уникальный ID на основе timestamp и случайного числа
        timestamp = int(datetime.now().timestamp())
        random_suffix = random.randint(1000, 9999)
        unique_id = f"FINE_{timestamp}_{random_suffix}"

        fine = Fine(
            id=unique_id,
            date=datetime.now().isoformat(),
            type=fine_type,
            amount=round(random.uniform(min_amount, max_amount), 2),
            order_id=f"ORDER_{random.randint(100000, 999999)}",
            status=random.choice(["Начислен", "Оспорен", "Оплачен"]),
        )
        fines.append(fine)

    print(f"[Mock Server] Сгенерировано {len(fines)} штрафов")
    return fines


@app.get("/")
def root():
    return {
        "message": "Mock Wildberries API",
        "endpoints": {"fines": "/api/v3/fines?days=1", "health": "/health"},
    }


@app.get("/health")
def health():
    return {"status": "ok", "timestamp": datetime.now().isoformat()}


@app.get("/api/v3/fines", response_model=FinesResponse)
def get_fines(days: str = "1"):
    """
    Получение штрафов

    Parameters:
    - days: за сколько дней (по умолчанию "1")
    """
    try:
        days_int = int(days)
    except ValueError:
        days_int = 1

    # Всегда генерируем 1-3 новых штрафа
    import random

    count = random.randint(1, 3)

    fines = generate_fines(count)
    return FinesResponse(data=fines)


if __name__ == "__main__":
    import uvicorn

    print("=" * 50)
    print("Mock WB API запущен: http://localhost:8000")
    print("Документация: http://localhost:8000/docs")
    print("=" * 50)
    uvicorn.run(app, host="0.0.0.0", port=8000)
