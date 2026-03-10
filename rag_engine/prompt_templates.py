"""
Prompt templates for RAG queries to LLM.
"""


class PromptTemplates:
    """Collection of prompt templates for various RAG tasks."""

    # General Q&A template
    QA_TEMPLATE = """You are an expert in government procurement (госзакупки).
Answer the following question based on the provided context.

{context}

Question: {question}

Please provide a detailed and accurate answer based on the context above.
If the information is not in the context, say "I don't have information about this in the current knowledge base."

Answer:"""

    # Procurement search template
    PROCUREMENT_SEARCH_TEMPLATE = """Based on the government procurement data, help find relevant procurements.

{context}

User query: {query}

Summarize relevant procurements found, including:
- Procurement number/ID
- Status
- Budget range
- Key requirements
- Deadline if available

Answer:"""

    # Requirement analysis template
    REQUIREMENT_ANALYSIS_TEMPLATE = """Analyze the requirements for this procurement.

{context}

Question: {question}

Please provide:
1. Mandatory requirements
2. Optional requirements
3. Technical specifications
4. Financial conditions
5. Timeline

Answer:"""

    # Participant information template
    PARTICIPANT_TEMPLATE = """Based on procurement history, provide information about participants.

{context}

Question: {question}

Please provide information about:
- Company name and registration
- Region of operation
- Previous participation history
- Contact information

Answer:"""

    # Comparison template
    COMPARISON_TEMPLATE = """Compare the following procurements.

{context}

Question: {question}

Please compare:
- Budget amounts
- Requirements
- Timelines
- Participant types
- Key differences and similarities

Answer:"""

    @staticmethod
    def get_qa_prompt(context: str, question: str) -> str:
        """Get Q&A prompt."""
        return PromptTemplates.QA_TEMPLATE.format(context=context, question=question)

    @staticmethod
    def get_procurement_search_prompt(context: str, query: str) -> str:
        """Get procurement search prompt."""
        return PromptTemplates.PROCUREMENT_SEARCH_TEMPLATE.format(context=context, query=query)

    @staticmethod
    def get_requirement_analysis_prompt(context: str, question: str) -> str:
        """Get requirement analysis prompt."""
        return PromptTemplates.REQUIREMENT_ANALYSIS_TEMPLATE.format(context=context, question=question)

    @staticmethod
    def get_participant_prompt(context: str, question: str) -> str:
        """Get participant information prompt."""
        return PromptTemplates.PARTICIPANT_TEMPLATE.format(context=context, question=question)

    @staticmethod
    def get_comparison_prompt(context: str, question: str) -> str:
        """Get comparison prompt."""
        return PromptTemplates.COMPARISON_TEMPLATE.format(context=context, question=question)
