"""
Main entry point for development and testing.

Usage:
    python main.py pipeline           # Run data pipeline
    python main.py bot               # Run Telegram bot
"""

import asyncio
import logging
import sys

from config.settings import logger, settings
from graph_loader.data_pipeline import DataPipeline
from telegram_bot.bot import GoszakupBot


def run_pipeline():
    """Run the data pipeline."""
    logger.info("Starting GraphRAG data pipeline")

    try:
        # Initialize pipeline
        pipeline = DataPipeline()

        if not pipeline.connect():
            logger.error("Failed to connect to Neo4j")
            return 1

        logger.info("Pipeline initialized successfully")

        # Process sample data if it exists
        sample_dir = settings.raw_data_dir
        if sample_dir.exists():
            file_count = pipeline.process_directory(str(sample_dir))
            logger.info(f"Processed {file_count} files")

            # Get database stats
            stats = pipeline.get_stats()
            logger.info(f"Database stats: {stats}")
        else:
            logger.warning(f"Sample data directory not found: {sample_dir}")

        pipeline.disconnect()
        logger.info("Pipeline completed successfully")
        return 0

    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        return 1


async def run_bot():
    """Run the Telegram bot."""
    if not settings.telegram_bot_token:
        print("❌ Ошибка: TELEGRAM_BOT_TOKEN не установлен в .env")
        return 1

    print("🚀 Запуск Telegram бота для государственных закупок...")
    bot = GoszakupBot(settings.telegram_bot_token)
    await bot.run()
    return 0


def main():
    """Main function."""
    if len(sys.argv) < 2:
        print("GraphRAG System")
        print("\nИспользование:")
        print("  python main.py pipeline    - Запустить data pipeline")
        print("  python main.py bot         - Запустить Telegram бота")
        return 0

    command = sys.argv[1].lower()

    if command == "pipeline":
        return run_pipeline()
    elif command == "bot":
        return asyncio.run(run_bot())
    else:
        print(f"❌ Неизвестная команда: {command}")
        print("\nДоступные команды: pipeline, bot")
        return 1


if __name__ == "__main__":
    sys.exit(main())
