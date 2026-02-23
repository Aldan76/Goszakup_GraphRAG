# 📚 Knowledge Graph Upload Guide

Expert Consultant Bot - система загрузки и управления нормативными документами.

## 🎯 Назначение

Система предназначена для пошаговой загрузки документов (законы, инструкции, методики) и создания Knowledge Graph для консультирования пользователей по государственным закупкам Казахстана.

## 📋 Поддерживаемые форматы

- **DOCX** (Microsoft Word) - основной формат
  - Извлекает текст, структуру
  - Автоматически выделяет:
    - Определения
    - Правила
    - Процедуры
    - Концепции

## 🔄 Процесс загрузки

### Шаг 1: Подготовка документа

Документ должен быть в формате `.docx`:
```
✅ Zakon_O_Gosudarstvennykh_Zakupkakh.docx
✅ Instrukciya_Tender.docx
✅ Metodologiya_Zakupok.docx

❌ document.pdf (не поддерживается)
❌ document.txt (не поддерживается)
```

### Шаг 2: Загрузка документа

#### Способ А: Интерактивный режим (рекомендуется)

```bash
python upload_knowledge.py
```

Меню:
```
📋 Menu:
  1. Upload DOCX document
  2. List uploaded documents
  3. Show knowledge summary
  4. Clear knowledge graph
  5. Exit
```

#### Способ Б: Командная строка

```bash
# Загрузить конкретный файл
python upload_knowledge.py Zakon.docx

# Показать загруженные документы
python upload_knowledge.py --list

# Показать статистику
python upload_knowledge.py --summary

# Очистить базу (для тестирования)
python upload_knowledge.py --clear
```

## 📊 Что происходит при загрузке

```
DOCX файл
    ↓
Парсер DOCXParser
├─ Извлекает текст
├─ Выделяет структуру (параграфы, заголовки)
└─ Классифицирует сущности:
    ├─ Definition (определение) - "болады", "деп"
    ├─ Rule (правило) - условия, требования
    ├─ Procedure (процедура) - пошаговые инструкции
    ├─ Process (процесс) - последовательности
    └─ Concept (концепция) - основные понятия
    ↓
HierarchicalChunker
├─ Разделяет на смысловые куски
├─ Сохраняет контекст (overlap)
└─ Создает chunks для embeddings
    ↓
Neo4j Graph Creation
├─ Узлы: Document, Concept, Rule, Definition, Procedure, Chunk
├─ Связи: DEFINES, RELATED_TO, GOVERNED_BY, USES_CONCEPT
└─ Embeddings: sentence-transformers для локального семантического поиска
    ↓
Knowledge Graph готов! ✅
```

## 🔗 Knowledge Graph Структура

### Узлы (Nodes)

| Тип | Назначение | Пример |
|-----|-----------|---------|
| **Document** | Исходный документ | "Zakon.docx" |
| **Concept** | Абстрактное понятие | "Электронный аукцион" |
| **Definition** | Определение термина | "Тендер - конкурс предложений" |
| **Rule** | Правило/требование | "При сумме > 10млн - обязателен аукцион" |
| **Procedure** | Процедура с шагами | "Процесс подачи заявки" |
| **Chunk** | Текстовый фрагмент | Часть документа с embeddings |

### Связи (Relationships)

```
Document
├─ FROM_DOCUMENT ─→ Concept
├─ FROM_DOCUMENT ─→ Rule
├─ FROM_DOCUMENT ─→ Definition
└─ FROM_DOCUMENT ─→ Procedure

Concept
├─ DEFINES ←─ Definition
├─ RELATED_TO ←─→ Concept (другие концепции)
├─ GOVERNED_BY ─→ Rule
└─ MENTIONED_IN_CHUNK ─→ Chunk

Procedure
├─ HAS_STEP ─→ Procedure (подшаги)
└─ USES_CONCEPT ─→ Concept
```

## 📖 Примеры использования

### Пример 1: Загрузить закон о государственных закупках

```bash
$ python upload_knowledge.py

👉 Select option (1-5): 1
📄 Enter path to DOCX file: data/samples/Zakon.docx

📄 Parsing document: Zakon.docx
✅ Parsed successfully:
   - Entities: 127
   - Chunks: 45
   - Language: kk

🔄 Loading into Neo4j...
✅ Document loaded successfully!

📊 Database statistics:
   Concept: 87
   Rule: 156
   Definition: 42
   Procedure: 23
   Chunk: 45
   Document: 1
```

### Пример 2: Показать загруженные документы

```bash
$ python upload_knowledge.py --list

📚 Uploaded Documents (1):
----------------------------------------------------------------------
1. ID: Zakon
   Type: regulatory_document
   Created: 2024-02-23T15:30:00
```

### Пример 3: Статистика Knowledge Graph

```bash
$ python upload_knowledge.py --summary

📊 Knowledge Graph Summary:
----------------------------------------------------------------------
  Concept              : 87
  Rule                 : 156
  Definition           : 42
  Procedure            : 23
  Chunk                : 45
  Document             : 1
----------------------------------------------------------------------
  TOTAL                : 354
```

## 🎓 Как использовать в боте

После загрузки документов, бот может отвечать на вопросы:

### Пример запроса:
```
User: "Какие требования к участнику аукциона?"

Bot (через RAG):
1. Извлекает запрос в embedding (sentence-transformers)
2. Ищет в Knowledge Graph
3. Находит Definition и Rule узлы
4. Отправляет контекст в Claude AI
5. Получает ответ:
   "По закону, участник должен:
    - Быть зарегистрирован
    - Иметь финансовую способность
    - Соответствовать требованиям..."
```

## 🔍 Поиск в Knowledge Graph

Бот может искать:
- **Определения**: "Что такое электронный аукцион?"
- **Правила**: "Когда применяется открытый конкурс?"
- **Процедуры**: "Как подать заявку?"
- **Концепции**: "Какие виды закупок существуют?"

## 🛠️ Технические детали

### Парсер DOCX (docx_parser.py)

```python
from parsers.docx_parser import DOCXParser

parser = DOCXParser()
doc = parser.parse("Zakon.docx")

# Результат:
# - doc.entities: List[ParsedEntity] с типами Definition, Rule, Concept, etc.
# - doc.chunks: List[ParsedChunk] для embeddings
# - doc.metadata: информация о языке, количестве параграфов
```

### Загрузка в Neo4j

```python
from graph_loader.data_pipeline import DataPipeline

pipeline = DataPipeline()
pipeline.connect()
pipeline.load_document(doc)
pipeline.disconnect()
```

### Поиск в графе

```python
from rag_engine.graph_retriever import GraphRetriever

retriever = GraphRetriever(connector, embeddings)
context = retriever.retrieve("Какие требования?")

# context.chunks - релевантные фрагменты
# context.metadata - связанные узлы из графа
```

## ⚙️ Конфигурация

В `.env`:
```env
# Язык документов
LANGUAGE=kk  # Казахский

# Размер chunks для embeddings
CHUNK_SIZE=500
CHUNK_OVERLAP=100

# Anthropic Claude для генерации ответов
ANTHROPIC_API_KEY=sk-ant-...

# Embeddings (локально, без API)
EMBEDDINGS_MODEL=sentence-transformers/all-MiniLM-L6-v2
```

## 🔒 Безопасность

- Все документы хранятся в Neo4j
- Исходные файлы (DOCX) не передаются
- Только текстовое содержимое + embeddings
- Доступ через bot API

## 📈 Масштабируемость

System может обработать:
- ✅ 1-10 документов (легко)
- ✅ 50-100 документов (хорошо)
- ⚠️ 500+ документов (требует оптимизации)
- ⚠️ 1000+ узлов в графе (требует batch processing)

## 🚀 Развертывание

### Локально
```bash
python upload_knowledge.py
```

### В Docker
```dockerfile
FROM python:3.10
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
CMD ["python", "upload_knowledge.py"]
```

### На сервере
```bash
# Установить PM2
npm install -g pm2

# Запустить как сервис
pm2 start upload_knowledge.py --name "knowledge-uploader"
pm2 save
pm2 startup
```

## 📞 Помощь

### Проблема: "Cannot read DOCX file"
- Убедитесь что файл в формате .docx
- Попробуйте пересохранить в LibreOffice/MS Word

### Проблема: "Failed to connect to Neo4j"
- Проверьте что Neo4j запущен (http://localhost:7474)
- Проверьте URI и пароль в .env

### Проблема: "Package not found: python-docx"
```bash
pip install python-docx
```

## 📚 Дальнейшие шаги

1. ✅ **Загрузить документы**
   - Zakon_O_Gosudarstvennykh_Zakupkakh.docx
   - Instrukciya_Tender.docx
   - Metodologiya_Zakupok.docx

2. 🔄 **Тестировать в боте**
   - Задавать вопросы консультанту
   - Проверять качество ответов

3. 📊 **Оптимизировать**
   - Добавлять больше документов
   - Улучшать классификацию сущностей
   - Добавлять custom relationships

---

**Система готова к работе!** 🚀
