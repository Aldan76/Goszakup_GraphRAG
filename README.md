# GraphRAG для Telegram-бота государственных закупок

Система для анализа и поиска информации по государственным закупкам с использованием граф-базы данных (Neo4j) и больших языковых моделей (OpenAI).

## Архитектура

### Компоненты

1. **Парсеры** (`parsers/`)
   - `base_parser.py` - Базовый класс для всех парсеров
   - `json_parser.py` - Парсер JSON документов
   - `xml_parser.py` - Парсер XML документов
   - `pdf_parser.py` - Парсер PDF документов

2. **Граф-база данных** (`graph_loader/`)
   - `neo4j_connector.py` - Подключение и управление Neo4j
   - `entity_creator.py` - Создание узлов в графе
   - `relationship_creator.py` - Создание связей в графе
   - `data_pipeline.py` - ETL пайплайн

3. **RAG Engine** (`rag_engine/`)
   - `graph_retriever.py` - Поиск информации в графе
   - `embeddings.py` - Работа с эмбеддингами
   - `rag_chain.py` - RAG цепь обработки
   - `prompt_templates.py` - Шаблоны промптов

4. **Telegram Bot** (`telegram_bot/`)
   - `bot.py` - Основной бот
   - `handlers.py` - Обработчики команд
   - `maintenance.py` - Управление режимом обслуживания

### Модель графа

```
Procurement (Закупка)
├── HAS_LOT → Lot (Лот)
├── ORGANIZED_BY → Organization (Организация)
├── HAS_REQUIREMENT → Requirement (Требование)
│
Lot
├── INCLUDED_IN_TENDER → Tender (Торги)
├── HAS_REQUIREMENT → Requirement

Tender
├── RECEIVED_BID_FROM → Participant (Участник)

Participant
├── SUBMITTED_DOCUMENT → Document (Документ)
├── REGISTERED_IN → Organization

Document
└── CONTAINS_CHUNK → Chunk (Фрагмент текста)
```

## Требования

- Python 3.10+
- Neo4j 5.0+
- OpenAI API ключ

## Установка

1. Клонируйте репозиторий
```bash
git clone <repo-url>
cd Goszakup_GraphRAG
```

2. Создайте виртуальное окружение
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate  # Windows
```

3. Установите зависимости
```bash
pip install -r requirements.txt
```

4. Настройте конфигурацию
```bash
cp .env.example .env
# Отредактируйте .env с вашими параметрами
```

5. Запустите Neo4j (Docker)
```bash
docker run --name neo4j -e NEO4J_AUTH=neo4j/password \
  -p 7687:7687 -p 7474:7474 neo4j:latest
```

## Использование

### Парсирование документов

```python
from parsers.json_parser import JSONParser

parser = JSONParser()
doc = parser.parse("data/raw/procurement_001.json")

print(f"Entities: {len(doc.entities)}")
print(f"Chunks: {len(doc.chunks)}")
```

### Загрузка в Neo4j

```python
from graph_loader.neo4j_connector import Neo4jConnector

connector = Neo4jConnector()
connector.connect()
connector.initialize_schema()

# Создание узлов
connector.create_node("Procurement", {
    "id": "proc_001",
    "number": "001",
    "budget": 1000000,
    "status": "active"
})
```

### RAG поиск

```python
from rag_engine.rag_chain import RAGChain

chain = RAGChain()
response = chain.query("Найди закупки по компьютерной технике")
print(response)
```

## Развёртывание

### Локальная разработка

```bash
python main.py
```

### Production

1. Развернуть Neo4j на выделенном сервере
2. Установить бота на VPS/Docker
3. Конфигурировать логирование и мониторинг
4. Установить TELEGRAM_BOT_TOKEN в .env
5. Запустить бота: `python -m telegram_bot.bot`

## Тестирование

```bash
pytest tests/ -v
pytest tests/ --cov=config,parsers,graph_loader,rag_engine,telegram_bot
```

## Логирование

Логи сохраняются в `logs/app.log` с уровнем, указанным в `.env` (LOG_LEVEL).

## Статус

- ✅ Парсеры (JSON, XML, PDF)
- ✅ Neo4j интеграция
- 🔄 RAG Engine (в разработке)
- 🔄 Telegram Bot (в разработке)
- ⏳ Тестирование (планируется)

## Лицензия

MIT

## Контакты

Автор: GraphRAG Development Team
