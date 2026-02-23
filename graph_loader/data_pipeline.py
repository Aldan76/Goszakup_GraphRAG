"""
ETL data pipeline for processing and loading procurement documents into Neo4j.
"""

import logging
from pathlib import Path
from typing import List, Optional

from chunking.chunker import HierarchicalChunker
from config.settings import settings
from graph_loader.entity_creator import EntityCreator
from graph_loader.neo4j_connector import Neo4jConnector
from graph_loader.relationship_creator import RelationshipCreator
from parsers.base_parser import ParsedDocument
from parsers.json_parser import JSONParser
from parsers.pdf_parser import PDFParser
from parsers.xml_parser import XMLParser

logger = logging.getLogger(__name__)


class DataPipeline:
    """
    ETL pipeline for processing procurement documents.

    Flow: Parse → Chunk → Extract Entities → Create Graph Nodes → Create Relationships
    """

    def __init__(
        self,
        neo4j_uri: Optional[str] = None,
        chunk_size: int = 500,
        chunk_overlap: int = 100,
    ):
        """
        Initialize data pipeline.

        Args:
            neo4j_uri: Neo4j connection URI
            chunk_size: Size for text chunks
            chunk_overlap: Overlap between chunks
        """
        self.connector = Neo4jConnector(uri=neo4j_uri)
        self.entity_creator = EntityCreator(self.connector)
        self.relationship_creator = RelationshipCreator(self.connector)
        self.chunker = HierarchicalChunker(chunk_size=chunk_size, overlap=chunk_overlap)

        # Parser registry
        self.parsers = {
            ".json": JSONParser(),
            ".xml": XMLParser(),
            ".pdf": PDFParser(),
        }

    def connect(self) -> bool:
        """Connect to Neo4j and initialize schema."""
        try:
            self.connector.connect()
            self.connector.initialize_schema()
            logger.info("Pipeline connected to Neo4j and schema initialized")
            return True
        except Exception as e:
            logger.error(f"Failed to connect: {e}")
            return False

    def disconnect(self) -> None:
        """Disconnect from Neo4j."""
        self.connector.disconnect()

    def process_file(self, file_path: str) -> bool:
        """
        Process a single document file.

        Args:
            file_path: Path to the file

        Returns:
            True if processing successful
        """
        file_ext = Path(file_path).suffix.lower()

        if file_ext not in self.parsers:
            logger.error(f"Unsupported file format: {file_ext}")
            return False

        try:
            logger.info(f"Processing file: {file_path}")

            # Parse document
            parser = self.parsers[file_ext]
            doc = parser.parse(file_path)

            # Load into graph
            return self.load_document(doc)

        except Exception as e:
            logger.error(f"Failed to process file {file_path}: {e}")
            return False

    def process_directory(self, directory: str) -> int:
        """
        Process all documents in a directory.

        Args:
            directory: Path to directory

        Returns:
            Number of successfully processed files
        """
        dir_path = Path(directory)
        count = 0

        for file_path in dir_path.rglob("*"):
            if file_path.is_file() and file_path.suffix.lower() in self.parsers:
                if self.process_file(str(file_path)):
                    count += 1

        logger.info(f"Processed {count} files from {directory}")
        return count

    def load_document(self, doc: ParsedDocument) -> bool:
        """
        Load parsed document into Neo4j.

        Args:
            doc: ParsedDocument to load

        Returns:
            True if loading successful
        """
        try:
            # Create document node
            doc_node_id = self.entity_creator.create_document(
                doc.document_id,
                doc.document_type,
                content=doc.full_text[:1000],  # Store truncated content
            )

            if not doc_node_id:
                logger.error(f"Failed to create document node: {doc.document_id}")
                return False

            logger.info(f"Created document node: {doc.document_id}")

            # Create entity nodes and relationships
            self._load_entities(doc)

            # Create and link chunks
            self._load_chunks(doc, doc.document_id)

            logger.info(f"Successfully loaded document: {doc.document_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to load document: {e}")
            return False

    def _load_entities(self, doc: ParsedDocument) -> None:
        """Load entities from parsed document."""
        for entity in doc.entities:
            self.entity_creator.create_from_parsed_entity(entity)
            logger.debug(f"Created entity: {entity.entity_type} - {entity.entity_id}")

    def _load_chunks(self, doc: ParsedDocument, doc_id: str) -> None:
        """Load text chunks from document."""
        for chunk in doc.chunks:
            chunk_id = f"{doc_id}_chunk_{chunk.chunk_index}"

            self.entity_creator.create_chunk(
                chunk_id,
                chunk.content,
                doc.document_id,
                chunk_type=chunk.chunk_type,
                chunk_index=chunk.chunk_index,
            )

            # Create relationship from document to chunk
            self.relationship_creator.create_contains_chunk(doc.document_id, chunk_id)

            logger.debug(f"Created chunk: {chunk_id}")

    def get_stats(self) -> dict:
        """Get database statistics."""
        return self.connector.get_stats()

    def clear_database(self) -> bool:
        """
        Clear all data from database (WARNING: destructive!).

        Returns:
            True if successful
        """
        if self.connector.delete_all():
            logger.warning("Database cleared")
            return True
        return False
