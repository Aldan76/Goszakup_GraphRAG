"""
Graph-based retrieval for RAG queries.
"""

import logging
from typing import Any, Dict, List, Optional

from graph_loader.neo4j_connector import Neo4jConnector
from rag_engine.embeddings import EmbeddingsManager

logger = logging.getLogger(__name__)


class RetrievedContext:
    """Represents retrieved context for RAG."""

    def __init__(self, chunks: List[str], metadata: Dict[str, Any]):
        """
        Initialize retrieved context.

        Args:
            chunks: List of relevant text chunks
            metadata: Associated metadata
        """
        self.chunks = chunks
        self.metadata = metadata

    def to_prompt(self) -> str:
        """Convert context to prompt format."""
        context = "\n\n".join(self.chunks)
        return f"Context:\n{context}"


class GraphRetriever:
    """Retrieves relevant information from Neo4j graph for RAG queries."""

    def __init__(
        self,
        neo4j_connector: Neo4jConnector,
        embeddings_manager: EmbeddingsManager,
        top_k: int = 5,
    ):
        """
        Initialize graph retriever.

        Args:
            neo4j_connector: Neo4j connection
            embeddings_manager: Embeddings manager
            top_k: Number of top results to return
        """
        self.connector = neo4j_connector
        self.embeddings = embeddings_manager
        self.top_k = top_k

    def retrieve(self, query: str) -> Optional[RetrievedContext]:
        """
        Retrieve relevant context for a query.

        Args:
            query: Query text

        Returns:
            RetrievedContext with relevant chunks and metadata
        """
        try:
            # Generate embedding for query
            query_embedding = self.embeddings.embed_text(query)
            if not query_embedding:
                logger.error("Failed to generate query embedding")
                return None

            # Search for relevant chunks
            chunks = self._search_chunks(query, query_embedding)

            if not chunks:
                logger.warning(f"No chunks found for query: {query}")
                return RetrievedContext([], {"query": query, "chunk_count": 0})

            # Get related procurement metadata
            metadata = self._get_related_metadata(chunks)

            return RetrievedContext(chunks, metadata)

        except Exception as e:
            logger.error(f"Retrieval failed: {e}")
            return None

    def _search_chunks(self, query: str, query_embedding: List[float]) -> List[str]:
        """Search for relevant chunks."""
        try:
            # Query all chunks from database
            cypher = """
            MATCH (d:Document)-[r:CONTAINS_CHUNK]->(c:Chunk)
            RETURN c.content as content
            LIMIT 100
            """

            results = self.connector.query(cypher)

            if not results:
                return []

            # Score chunks by embedding similarity
            scored_chunks = []
            for result in results:
                content = result.get("content", "")
                if not content:
                    continue

                # Generate embedding for chunk
                chunk_embedding = self.embeddings.embed_text(content)
                if not chunk_embedding:
                    continue

                # Calculate similarity
                similarity = self.embeddings.similarity(query_embedding, chunk_embedding)
                scored_chunks.append((content, similarity))

            # Sort by similarity and return top-k
            scored_chunks.sort(key=lambda x: x[1], reverse=True)
            return [chunk[0] for chunk in scored_chunks[: self.top_k]]

        except Exception as e:
            logger.error(f"Chunk search failed: {e}")
            return []

    def _get_related_metadata(self, chunks: List[str]) -> Dict[str, Any]:
        """Get metadata related to retrieved chunks."""
        try:
            # Find source documents
            cypher = """
            MATCH (c:Chunk)-[:CONTAINS_CHUNK]-(d:Document)
            RETURN DISTINCT d.id as doc_id, d.type as doc_type
            LIMIT 10
            """

            results = self.connector.query(cypher)

            # Find related procurements
            proc_cypher = """
            MATCH (p:Procurement)-[:HAS_REQUIREMENT|:ORGANIZED_BY]->()
            RETURN DISTINCT p.id as proc_id, p.number as proc_number, p.status as status
            LIMIT 5
            """

            proc_results = self.connector.query(proc_cypher)

            return {
                "documents": [{"id": r["doc_id"], "type": r["doc_type"]} for r in results],
                "procurements": [
                    {"id": r["proc_id"], "number": r["proc_number"], "status": r["status"]}
                    for r in proc_results
                ],
            }

        except Exception as e:
            logger.error(f"Metadata retrieval failed: {e}")
            return {}

    def search_by_keyword(self, keyword: str) -> List[str]:
        """
        Search for chunks containing keyword.

        Args:
            keyword: Keyword to search for

        Returns:
            List of matching chunks
        """
        try:
            cypher = """
            MATCH (c:Chunk)
            WHERE c.content CONTAINS $keyword
            RETURN c.content as content
            LIMIT 10
            """

            results = self.connector.query(cypher, {"keyword": keyword})
            return [r["content"] for r in results if r.get("content")]

        except Exception as e:
            logger.error(f"Keyword search failed: {e}")
            return []

    def search_procurements(self, criteria: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Search for procurements by criteria.

        Args:
            criteria: Search criteria (status, region, etc.)

        Returns:
            List of matching procurements
        """
        try:
            # Build dynamic cypher query
            conditions = []
            params = {}

            if "status" in criteria:
                conditions.append("p.status = $status")
                params["status"] = criteria["status"]

            if "region" in criteria:
                conditions.append("p.region CONTAINS $region")
                params["region"] = criteria["region"]

            if "budget_min" in criteria:
                conditions.append("p.budget >= $budget_min")
                params["budget_min"] = criteria["budget_min"]

            if "budget_max" in criteria:
                conditions.append("p.budget <= $budget_max")
                params["budget_max"] = criteria["budget_max"]

            where_clause = " AND ".join(conditions) if conditions else "1=1"

            cypher = f"""
            MATCH (p:Procurement)
            WHERE {where_clause}
            RETURN p.id as id, p.number as number, p.status as status,
                   p.budget as budget, p.description as description
            LIMIT 20
            """

            results = self.connector.query(cypher, params)
            return results

        except Exception as e:
            logger.error(f"Procurement search failed: {e}")
            return []
