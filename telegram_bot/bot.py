"""
Main Telegram bot for government procurement queries.
"""

import asyncio
import logging
from typing import Optional

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

from config.settings import settings, logger
from graph_loader.neo4j_connector import Neo4jConnector
from rag_engine.embeddings import EmbeddingsManager
from rag_engine.rag_chain import RAGChain
from telegram_bot.maintenance import MaintenanceManager

# Configure logging
logger = logging.getLogger("goszakup.bot")


class GoszakupBot:
    """Main Telegram bot for government procurement queries."""

    def __init__(self, token: str):
        """
        Initialize bot.

        Args:
            token: Telegram bot token
        """
        self.token = token
        self.maintenance = MaintenanceManager()

        # Initialize RAG components
        try:
            self.neo4j_connector = Neo4jConnector()
            self.embeddings_manager = EmbeddingsManager()
            self.rag_chain = RAGChain(self.neo4j_connector, self.embeddings_manager)
            logger.info("RAG chain initialized")
        except Exception as e:
            logger.error(f"Failed to initialize RAG chain: {e}")
            self.rag_chain = None

        # Track user sessions
        self.user_sessions = {}

        # Build application
        self.application = Application.builder().token(token).build()
        self._setup_handlers()

    def _setup_handlers(self) -> None:
        """Setup message handlers."""
        # Commands
        self.application.add_handler(CommandHandler("start", self.cmd_start))
        self.application.add_handler(CommandHandler("help", self.cmd_help))
        self.application.add_handler(CommandHandler("search", self.cmd_search))
        self.application.add_handler(CommandHandler("details", self.cmd_details))
        self.application.add_handler(CommandHandler("status", self.cmd_status))
        self.application.add_handler(CommandHandler("maintenance", self.cmd_maintenance))

        # Messages
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))

    async def cmd_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /start command."""
        if self.maintenance.is_maintenance_enabled():
            await update.message.reply_text(self.maintenance.get_maintenance_message())
            return

        user = update.effective_user
        welcome_message = f"""👋 Привет, {user.first_name}!

Я помогу вам найти информацию о государственных закупках.

📋 **Доступные команды:**
/search <запрос> - Найти закупки
/details <ID> - Информация о закупке
/status - Статус системы
/help - Справка

💬 **Просто напишите свой вопрос** и я найду релевантные закупки!

🔍 **Примеры запросов:**
- Закупки компьютерной техники
- Тендеры по ремонту
- Требования по документам
"""
        await update.message.reply_text(welcome_message, parse_mode="Markdown")
        logger.info(f"User {user.id} started bot")

    async def cmd_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /help command."""
        if self.maintenance.is_maintenance_enabled():
            await update.message.reply_text(self.maintenance.get_maintenance_message())
            return

        help_text = """📚 **Справка по командам:**

/search <запрос> - Найти закупки по ключевым словам
  Пример: /search компьютеры

/details <ID> - Получить детали закупки
  Пример: /details proc_001

/status - Проверить статус базы данных

💬 **Естественные запросы:**
Просто напишите вопрос и я найду ответ!
Примеры:
  - Какие есть закупки от мэрии?
  - Сколько лотов в этой закупке?
  - Какие требования к участникам?

⚙️ **Администраторам:**
/maintenance on|off - Включить/выключить режим обслуживания
"""
        await update.message.reply_text(help_text, parse_mode="Markdown")

    async def cmd_search(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /search command."""
        if self.maintenance.is_maintenance_enabled():
            await update.message.reply_text(self.maintenance.get_maintenance_message())
            return

        if not context.args:
            await update.message.reply_text("❌ Использование: /search <запрос>\nПример: /search компьютеры")
            return

        query = " ".join(context.args)

        # Show typing indicator
        await update.message.chat.send_action("typing")

        if not self.rag_chain:
            await update.message.reply_text("❌ Система недоступна. Попробуйте позже.")
            return

        # Search procurements
        response = self.rag_chain.search_procurements(query)

        if response:
            await update.message.reply_text(response, parse_mode="Markdown")
        else:
            await update.message.reply_text("❌ Ошибка при поиске. Попробуйте позже.")

        logger.info(f"Search query: {query}")

    async def cmd_details(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /details command."""
        if self.maintenance.is_maintenance_enabled():
            await update.message.reply_text(self.maintenance.get_maintenance_message())
            return

        if not context.args:
            await update.message.reply_text("❌ Использование: /details <ID>\nПример: /details proc_001")
            return

        proc_id = context.args[0]

        try:
            # Get procurement details from Neo4j
            proc = self.neo4j_connector.get_node_by_id("Procurement", proc_id)

            if not proc:
                await update.message.reply_text(f"❌ Закупка {proc_id} не найдена.")
                return

            # Format details
            details = f"""📋 **Детали закупки:**

**№ Закупки:** {proc.get('number', 'N/A')}
**Статус:** {proc.get('status', 'N/A')}
**Бюджет:** {proc.get('budget', 'N/A')} руб.
**Описание:** {proc.get('description', 'N/A')}
**Дедлайн:** {proc.get('deadline', 'N/A')}
"""
            await update.message.reply_text(details, parse_mode="Markdown")

        except Exception as e:
            logger.error(f"Failed to get details: {e}")
            await update.message.reply_text("❌ Ошибка при получении деталей.")

    async def cmd_status(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /status command."""
        try:
            stats = self.neo4j_connector.get_stats()

            status_text = "📊 **Статус системы:**\n\n"
            status_text += "**Данные в базе:**\n"

            for label, count in stats.items():
                status_text += f"• {label}: {count}\n"

            status_text += f"\n🟢 Система работает нормально"
            await update.message.reply_text(status_text, parse_mode="Markdown")

        except Exception as e:
            logger.error(f"Status check failed: {e}")
            await update.message.reply_text("🔴 Ошибка при проверке статуса системы.")

    async def cmd_maintenance(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /maintenance command (admin only)."""
        user_id = update.effective_user.id

        # Check if user is admin
        if user_id not in settings.admin_ids:
            await update.message.reply_text("❌ У вас нет прав администратора.")
            return

        if not context.args:
            status = "✅ Включен" if self.maintenance.is_maintenance_enabled() else "❌ Выключен"
            await update.message.reply_text(f"Режим обслуживания: {status}\n\nИспользование: /maintenance on|off")
            return

        command = context.args[0].lower()

        if command == "on":
            self.maintenance.enable_maintenance()
            await update.message.reply_text("🔧 Режим обслуживания **включен**.", parse_mode="Markdown")
            logger.info(f"Maintenance mode enabled by {user_id}")

        elif command == "off":
            self.maintenance.disable_maintenance()
            await update.message.reply_text("✅ Режим обслуживания **выключен**.", parse_mode="Markdown")
            logger.info(f"Maintenance mode disabled by {user_id}")

        else:
            await update.message.reply_text("❌ Неизвестная команда. Используйте: on|off")

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle regular messages (queries)."""
        if self.maintenance.is_maintenance_enabled():
            await update.message.reply_text(self.maintenance.get_maintenance_message())
            return

        message_text = update.message.text

        # Show typing indicator
        await update.message.chat.send_action("typing")

        if not self.rag_chain:
            await update.message.reply_text("❌ Система недоступна. Попробуйте позже.")
            return

        # Process query through RAG
        response = self.rag_chain.query(message_text)

        if response:
            # Split long responses
            if len(response) > 4000:
                chunks = [response[i : i + 4000] for i in range(0, len(response), 4000)]
                for chunk in chunks:
                    await update.message.reply_text(chunk, parse_mode="Markdown")
            else:
                await update.message.reply_text(response, parse_mode="Markdown")
        else:
            await update.message.reply_text("❌ Ошибка при обработке запроса. Попробуйте позже.")

        logger.info(f"Query from {update.effective_user.id}: {message_text[:50]}")

    async def run(self) -> None:
        """Start the bot."""
        logger.info("🤖 Запуск Telegram бота...")

        try:
            # Connect to Neo4j
            if not self.neo4j_connector.driver:
                self.neo4j_connector.connect()
                logger.info("Connected to Neo4j")

            # Start polling
            await self.application.run_polling()

        except KeyboardInterrupt:
            logger.info("Bot stopped by user")
        except Exception as e:
            logger.error(f"Bot error: {e}")
        finally:
            if self.neo4j_connector.driver:
                self.neo4j_connector.disconnect()
            logger.info("Bot shutdown complete")

    def run_sync(self) -> None:
        """Run bot synchronously."""
        asyncio.run(self.run())


async def main():
    """Main entry point."""
    bot = GoszakupBot(settings.telegram_bot_token)
    await bot.run()


if __name__ == "__main__":
    asyncio.run(main())
