"""
RAG chain for processing queries through Claude AI with graph context.
"""

import logging
from typing import Optional

import anthropic

from config.settings import settings
from graph_loader.neo4j_connector import Neo4jConnector
from rag_engine.embeddings import EmbeddingsManager
from rag_engine.graph_retriever import GraphRetriever, RetrievedContext
from rag_engine.prompt_templates import PromptTemplates

logger = logging.getLogger(__name__)


class RAGChain:
    """Complete RAG chain: Query → Retrieve → Generate."""

    def __init__(
        self,
        neo4j_connector: Neo4jConnector,
        embeddings_manager: EmbeddingsManager,
        llm_model: Optional[str] = None,
    ):
        """
        Initialize RAG chain.

        Args:
            neo4j_connector: Neo4j connection
            embeddings_manager: Embeddings manager
            llm_model: LLM model to use (default from settings)
        """
        self.connector = neo4j_connector
        self.embeddings = embeddings_manager
        self.retriever = GraphRetriever(neo4j_connector, embeddings_manager)
        self.llm_model = llm_model or settings.anthropic_llm_model
        self.client = anthropic.Anthropic(api_key=settings.anthropic_api_key)

    def query(self, question: str, query_type: str = "qa") -> Optional[str]:
        """
        Process a query through the RAG chain.

        Args:
            question: User question
            query_type: Type of query (qa, search, analysis, etc.)

        Returns:
            Generated answer or None if failed
        """
        try:
            # Step 1: Retrieve relevant context
            context = self.retriever.retrieve(question)

            if not context or not context.chunks:
                logger.warning(f"No context found for question: {question}")
                return self._generate_fallback_response(question)

            # Step 2: Build prompt
            prompt = self._build_prompt(question, context, query_type)

            # Step 3: Generate response
            response = self._generate_response(prompt)

            return response

        except Exception as e:
            logger.error(f"RAG chain failed: {e}")
            return None

    def search_procurements(self, query: str) -> Optional[str]:
        """
        Search for procurements matching query.

        Args:
            query: Search query

        Returns:
            Formatted search results
        """
        try:
            # Search for relevant procurements
            procurements = self.retriever.search_procurements({"status": "active"})

            if not procurements:
                return "❌ Не найдено активных закупок."

            # Format results
            results = self._format_procurement_results(procurements, query)
            return results

        except Exception as e:
            logger.error(f"Procurement search failed: {e}")
            return None

    def _build_prompt(self, question: str, context: RetrievedContext, query_type: str) -> str:
        """Build prompt based on query type."""
        context_text = context.to_prompt()

        if query_type == "search":
            return PromptTemplates.get_procurement_search_prompt(context_text, question)
        elif query_type == "analysis":
            return PromptTemplates.get_requirement_analysis_prompt(context_text, question)
        elif query_type == "participant":
            return PromptTemplates.get_participant_prompt(context_text, question)
        elif query_type == "comparison":
            return PromptTemplates.get_comparison_prompt(context_text, question)
        else:  # Default: qa
            return PromptTemplates.get_qa_prompt(context_text, question)

    def _generate_response(self, prompt: str) -> Optional[str]:
        """Generate response using Claude AI."""
        try:
            message = self.client.messages.create(
                model=self.llm_model,
                max_tokens=1500,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
            )

            answer = message.content[0].text.strip()
            logger.info(f"Generated response ({len(answer)} chars)")
            return answer

        except Exception as e:
            logger.error(f"LLM generation failed: {e}")
            # Try fallback model
            return self._generate_with_fallback(prompt)

    def _generate_with_fallback(self, prompt: str) -> Optional[str]:
        """Generate response using fallback Claude model."""
        try:
            logger.info(f"Trying fallback model: {settings.anthropic_fallback_model}")

            message = self.client.messages.create(
                model=settings.anthropic_fallback_model,
                max_tokens=1000,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
            )

            return message.content[0].text.strip()

        except Exception as e:
            logger.error(f"Fallback generation also failed: {e}")
            return None

    def _generate_fallback_response(self, question: str) -> str:
        """Generate simple fallback response when no context available."""
        keywords = question.lower().split()

        if any(word in keywords for word in ["количество", "сколько", "count"]):
            return "📊 Попробуйте уточнить запрос с названием закупки или организации."

        if any(word in keywords for word in ["бюджет", "стоимость", "цена", "budget"]):
            return "💰 Информация о бюджете недоступна. Попробуйте поискать по номеру закупки."

        return "🤔 Не могу найти информацию по вашему запросу. Попробуйте переформулировать вопрос или использовать команду /search."

    def _format_procurement_results(self, procurements: list, query: str) -> str:
        """Format procurement search results."""
        if not procurements:
            return "❌ Не найдено закупок."

        result_lines = [f"🔍 **Найдено {len(procurements)} закупок:**\n"]

        for i, proc in enumerate(procurements[:5], 1):  # Show top 5
            proc_id = proc.get("id", "N/A")
            proc_number = proc.get("number", "N/A")
            status = proc.get("status", "N/A")
            budget = proc.get("budget", "N/A")

            result_lines.append(f"{i}. **Закупка {proc_number}** (ID: {proc_id})")
            result_lines.append(f"   Статус: {status}")
            result_lines.append(f"   Бюджет: {budget}")
            result_lines.append("")

        result_lines.append("Для деталей используйте: `/details <ID>`")
        return "\n".join(result_lines)
