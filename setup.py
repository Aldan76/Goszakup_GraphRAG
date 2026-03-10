#!/usr/bin/env python3
"""
Interactive setup script for Goszakup GraphRAG with Claude AI
Настроит всё что нужно для запуска бота
"""

import os
import sys
from pathlib import Path


def print_header(text):
    """Печать заголовка"""
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60)


def print_success(text):
    """Печать успеха"""
    print(f"✅ {text}")


def print_error(text):
    """Печать ошибки"""
    print(f"❌ {text}")


def print_info(text):
    """Печать информации"""
    print(f"ℹ️  {text}")


def input_required(prompt, validate=None):
    """Получить обязательный ввод"""
    while True:
        value = input(f"\n👉 {prompt}: ").strip()
        if not value:
            print_error("Поле обязательно!")
            continue
        if validate and not validate(value):
            print_error("Некорректное значение!")
            continue
        return value


def input_optional(prompt, default=None):
    """Получить опциональный ввод"""
    suffix = f" (по умолчанию: {default})" if default else ""
    value = input(f"\n👉 {prompt}{suffix}: ").strip()
    return value if value else default


def validate_api_key(key):
    """Проверить формат API ключа"""
    return key.startswith("sk-ant-") and len(key) > 20


def validate_telegram_token(token):
    """Проверить формат Telegram токена"""
    return len(token) > 30 and ":" in token


def create_env_file(config):
    """Создать .env файл"""
    env_content = f"""# Neo4j Configuration
NEO4J_URI={config['neo4j_uri']}
NEO4J_USER={config['neo4j_user']}
NEO4J_PASSWORD={config['neo4j_password']}

# Anthropic Claude Configuration
ANTHROPIC_API_KEY={config['anthropic_api_key']}
ANTHROPIC_LLM_MODEL=claude-3-sonnet-20240229
ANTHROPIC_FALLBACK_MODEL=claude-3-haiku-20240307

# Embeddings Configuration (using sentence-transformers)
EMBEDDINGS_MODEL=sentence-transformers/all-MiniLM-L6-v2

# Telegram Bot
TELEGRAM_BOT_TOKEN={config['telegram_bot_token']}
TELEGRAM_ADMIN_IDS={config['telegram_admin_ids']}

# Redis Configuration (Optional)
REDIS_URL=redis://localhost:6379

# Application Settings
LOG_LEVEL=INFO
CHUNK_SIZE=500
CHUNK_OVERLAP=100
MAX_RETRIEVAL_RESULTS=5
MAINTENANCE_MODE=false

# Data Paths
RAW_DATA_PATH=./data/raw
PROCESSED_DATA_PATH=./data/processed
"""

    env_file = Path(".env")
    env_file.write_text(env_content)
    print_success(f"Создан .env файл")


def main():
    """Главная функция"""
    print("\n")
    print_header("🚀 Goszakup GraphRAG - Setup (Claude AI)")
    print("""
Добро пожаловать! Этот скрипт настроит бота для работы с Claude AI.

Нужно будет ввести:
1. API ключ Anthropic (Claude)
2. Telegram Bot Token
3. Параметры Neo4j (опционально)
4. Admin IDs для Telegram
    """)

    # Проверить существующий .env
    if Path(".env").exists():
        print_info(".env файл уже существует")
        overwrite = input("\n👉 Перезаписать его? (y/n): ").lower()
        if overwrite != "y":
            print_success("Сохранили существующий .env файл")
            return

    print_header("📋 Конфигурация")

    config = {}

    # Neo4j
    print("\n🗄️  Neo4j Database Configuration")
    print_info("Если запускаете локально, оставьте значения по умолчанию")

    config['neo4j_uri'] = input_optional(
        "Neo4j URI",
        default="bolt://localhost:7687"
    )
    config['neo4j_user'] = input_optional(
        "Neo4j User",
        default="neo4j"
    )
    config['neo4j_password'] = input_optional(
        "Neo4j Password",
        default="password"
    )

    # Anthropic
    print("\n🤖 Anthropic Claude API Configuration")
    print_info("Получите ключ на https://console.anthropic.com/")

    config['anthropic_api_key'] = input_required(
        "Anthropic API Key (sk-ant-...)",
        validate=validate_api_key
    )
    print_success("API ключ принят")

    # Telegram
    print("\n💬 Telegram Bot Configuration")
    print_info("Получите токен у @BotFather в Telegram")

    config['telegram_bot_token'] = input_required(
        "Telegram Bot Token",
        validate=validate_telegram_token
    )
    print_success("Telegram токен принят")

    config['telegram_admin_ids'] = input_optional(
        "Admin IDs (через запятую, опционально)",
        default=""
    )

    # Показать конфигурацию
    print("\n" + "="*60)
    print("  📝 Ваша конфигурация:")
    print("="*60)
    print(f"""
Neo4j:
  URI: {config['neo4j_uri']}
  User: {config['neo4j_user']}
  Password: {'*' * len(config['neo4j_password'])}

Anthropic Claude:
  API Key: {config['anthropic_api_key'][:20]}...

Telegram:
  Bot Token: {config['telegram_bot_token'][:20]}...
  Admin IDs: {config['telegram_admin_ids'] or '(не указаны)'}
    """)

    # Подтверждение
    confirm = input("\n👉 Всё правильно? (y/n): ").lower()
    if confirm != "y":
        print_error("Отменено")
        return

    # Создать .env файл
    create_env_file(config)

    # Предложить следующие шаги
    print("\n" + "="*60)
    print("  ✅ Настройка завершена!")
    print("="*60)
    print("""
Следующие шаги:

1️⃣  Установить зависимости:
   pip install -r requirements.txt

2️⃣  Убедитесь что Neo4j запущен:
   docker run --name neo4j -e NEO4J_AUTH=neo4j/password \\
     -p 7687:7687 -p 7474:7474 neo4j:latest

3️⃣  Запустить бота локально (для тестирования):
   python main.py bot

4️⃣  После тестирования развернуть на Railway:
   - Обновить переменные в Railway Dashboard
   - Перезапустить deployment

📚 Документация:
   - README.md - общая информация
   - TELEGRAM_BOT.md - как использовать бота
   - CLAUDE_MIGRATION.md - что изменилось с OpenAI
   - RAILWAY_DEPLOY.md - инструкция для Railway
    """)

    print_success("Готово к работе! 🚀\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print_error("\n\nОтменено пользователем")
        sys.exit(1)
    except Exception as e:
        print_error(f"\nОшибка: {e}")
        sys.exit(1)
