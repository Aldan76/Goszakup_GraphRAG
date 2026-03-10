# ⚡ Быстрый старт GraphRAG Telegram Bot

Полный процесс от установки до запуска бота за 10 минут.

## 🚀 Установка (5 минут)

### 1. Клонируйте репо и установите зависимости

```bash
git clone https://github.com/Aldan76/Goszakup_GraphRAG.git
cd Goszakup_GraphRAG

python -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate     # Windows

pip install -r requirements.txt
```

### 2. Настройте переменные окружения

```bash
cp .env.example .env
```

Отредактируйте `.env`:
```env
# Обязательные
TELEGRAM_BOT_TOKEN=8617987568:AAGkDlRS5yQxxfA2ZUrgTbQj-V3uFJGuKmU
OPENAI_API_KEY=sk-your-key-here

# Neo4j (если локально)
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password

# Админы (ваш ID в Telegram)
TELEGRAM_ADMIN_IDS=123456789
```

### 3. Запустите Neo4j

**Вариант A: Docker (проще)**
```bash
docker run -d --name neo4j \
  -e NEO4J_AUTH=neo4j/password \
  -p 7687:7687 -p 7474:7474 \
  neo4j:latest
```

**Вариант B: Установить локально**
- Скачайте с https://neo4j.com/download/
- Запустите с паролем `password`

Проверка:
```bash
# Перейдите на http://localhost:7474
# Логин: neo4j, Пароль: password
```

## 📊 Загрузка данных (2 минуты)

### Загрузить образцы данных

```bash
python load_data.py
```

Будет загружено 2 образца закупок:
- procurement_001.json - Закупка компьютерного оборудования
- procurement_002.json - Ремонтные работы офиса

Проверка в Neo4j Browser (http://localhost:7474):
```cypher
MATCH (p:Procurement) RETURN p LIMIT 10
```

### Загрузить свои данные

Поместите JSON файлы в `data/raw/` и запустите:
```bash
python load_data.py data/raw/
```

## 🤖 Запуск Telegram бота (1 минута)

### Запустить бота

```bash
python main.py bot
```

Или:
```bash
python -m telegram_bot
```

Должны увидеть:
```
🚀 Запуск Telegram бота для государственных закупок...
🤖 Запуск Telegram бота...
```

## 💬 Тестирование бота

### В Telegram:

1. **Найдите бота** - ищите `@goszakup_graphrag_bot` (замените на ваш username)

2. **Напишите**:
   ```
   /start
   ```

3. **Попробуйте команды**:
   ```
   /search компьютеры
   /status
   Найди все закупки
   ```

4. **Примеры запросов**:
   - "Какие требования у этого тендера?"
   - "Сколько лотов в закупке?"
   - "Найди закупки по ремонту"
   - "Какие компании участвуют?"

## 🧪 Тестирование (опционально)

```bash
# Запустить тесты
pytest tests/ -v

# С покрытием кода
pytest tests/ --cov=. --cov-report=html
```

## 📋 Структура проекта

```
Goszakup_GraphRAG/
├── config/              # Конфигурация и схема БД
├── parsers/             # Парсеры JSON, XML, PDF
├── graph_loader/        # Neo4j интеграция
├── rag_engine/          # RAG и поиск
├── telegram_bot/        # Telegram бот
├── data/samples/        # Образцы данных ✨
├── load_data.py         # Скрипт загрузки данных
└── main.py              # Главная точка входа
```

## 🔧 Решение проблем

### Бот не запускается
```bash
# Проверьте токен в .env
echo $TELEGRAM_BOT_TOKEN

# Проверьте логи
cat logs/app.log
```

### Neo4j не подключается
```bash
# Проверьте что работает
docker ps | grep neo4j

# Или перезагрузите
docker stop neo4j
docker rm neo4j
docker run -d --name neo4j -e NEO4J_AUTH=neo4j/password -p 7687:7687 -p 7474:7474 neo4j:latest
```

### OpenAI ошибка
```bash
# Проверьте ключ
echo $OPENAI_API_KEY

# Проверьте баланс на https://platform.openai.com/account/billing/overview
```

## 📚 Дополнительно

- **[README.md](README.md)** - Полная документация проекта
- **[TELEGRAM_BOT.md](TELEGRAM_BOT.md)** - Детальная справка по боту
- **[GitHub PR](https://github.com/Aldan76/Goszakup_GraphRAG/pull/1)** - История разработки

## 🎯 Дальнейшие шаги

1. **Добавить свои данные**
   - Подготовьте JSON файлы с вашими закупками
   - Используйте структуру из `data/samples/`
   - Загрузите: `python load_data.py data/raw/`

2. **Оптимизировать бота**
   - Настроить промпты в `rag_engine/prompt_templates.py`
   - Добавить нужные команды в `telegram_bot/bot.py`

3. **Production deploy**
   - Развернуть на VPS
   - Настроить систему мониторинга
   - Добавить резервное копирование Neo4j

---

**Готово!** Ваша GraphRAG система работает. 🚀
