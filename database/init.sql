-- Таблица штрафов
CREATE TABLE IF NOT EXISTS fines (
    id VARCHAR(50) PRIMARY KEY,
    date TIMESTAMP NOT NULL,
    type VARCHAR(200) NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    order_id VARCHAR(50),
    status VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    notified BOOLEAN DEFAULT FALSE,
    dispute_created BOOLEAN DEFAULT FALSE
);

-- Индексы для ускорения поиска
CREATE INDEX IF NOT EXISTS idx_fines_date ON fines(date);
CREATE INDEX IF NOT EXISTS idx_fines_status ON fines(status);
CREATE INDEX IF NOT EXISTS idx_fines_notified ON fines(notified);
CREATE INDEX IF NOT EXISTS idx_fines_amount ON fines(amount);

-- Таблица уведомлений
CREATE TABLE IF NOT EXISTS notifications (
    id SERIAL PRIMARY KEY,
    fine_id VARCHAR(50),
    channel VARCHAR(50) NOT NULL,
    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    success BOOLEAN DEFAULT TRUE,
    error_message TEXT,
    retry_count INTEGER DEFAULT 0
);

-- Статистика
CREATE TABLE IF NOT EXISTS daily_stats (
    date DATE PRIMARY KEY,
    total_fines INTEGER DEFAULT 0,
    total_amount DECIMAL(15, 2) DEFAULT 0,
    new_fines INTEGER DEFAULT 0,
    disputed_fines INTEGER DEFAULT 0,
    average_amount DECIMAL(10, 2) DEFAULT 0
);

-- Создаём представление для удобства
CREATE OR REPLACE VIEW fines_summary AS
SELECT
    DATE(date) as fine_date,
    COUNT(*) as fines_count,
    SUM(amount) as total_amount,
    AVG(amount) as average_amount,
    SUM(CASE WHEN status = 'Оспорен' THEN 1 ELSE 0 END) as disputed_count
FROM fines
GROUP BY DATE(date)
ORDER BY fine_date DESC;

-- Логируем создание таблиц (опционально)
DO $$
BEGIN
    RAISE NOTICE 'Таблицы для бота WB созданы/проверены';
END $$;
