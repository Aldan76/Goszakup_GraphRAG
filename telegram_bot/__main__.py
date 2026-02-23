"""
Telegram bot entry point.
"""

import asyncio
import sys

from config.settings import settings
from telegram_bot.bot import GoszakupBot


async def main():
    """Run the bot."""
    if not settings.telegram_bot_token:
        print("❌ Ошибка: TELEGRAM_BOT_TOKEN не установлен в .env")
        sys.exit(1)

    print("🚀 Запуск Telegram бота для государственных закупок...")
    print(f"📱 Режим обслуживания: {'Включен' if settings.maintenance_mode else 'Выключен'}")

    bot = GoszakupBot(settings.telegram_bot_token)
    await bot.run()


if __name__ == "__main__":
    asyncio.run(main())
