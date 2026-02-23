"""
Base parser class for all data sources.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ParsedEntity(BaseModel):
    """Represents a parsed entity from a document."""

    entity_type: str = Field(..., description="Type of entity (Procurement, Participant, etc.)")
    entity_id: str = Field(..., description="Unique identifier for the entity")
    properties: Dict[str, Any] = Field(default_factory=dict, description="Entity properties")
    relationships: List[Dict[str, Any]] = Field(default_factory=list, description="Relationships to other entities")


class ParsedChunk(BaseModel):
    """Represents a text chunk from a document."""

    content: str = Field(..., description="Chunk text content")
    chunk_type: str = Field(default="text", description="Type of chunk (text, table, etc.)")
    source_document_id: str = Field(..., description="ID of source document")
    chunk_index: int = Field(..., description="Index of chunk in document")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class ParsedDocument(BaseModel):
    """Represents a fully parsed document."""

    document_id: str = Field(..., description="Unique document identifier")
    document_type: str = Field(..., description="Type of document")
    full_text: str = Field(..., description="Complete document text")
    entities: List[ParsedEntity] = Field(default_factory=list, description="Extracted entities")
    chunks: List[ParsedChunk] = Field(default_factory=list, description="Text chunks")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Document metadata")

    class Config:
        """Pydantic config."""
        arbitrary_types_allowed = True


class BaseParser(ABC):
    """Abstract base class for all parsers."""

    def __init__(self, parser_name: str = "BaseParser"):
        """Initialize parser."""
        self.parser_name = parser_name
        self.supported_formats = []

    @abstractmethod
    def parse(self, file_path: str) -> ParsedDocument:
        """
        Parse a document and extract entities.

        Args:
            file_path: Path to the file to parse

        Returns:
            ParsedDocument with extracted entities and chunks

        Raises:
            ValueError: If file format is not supported
            IOError: If file cannot be read
        """
        pass

    @abstractmethod
    def extract_text(self, file_path: str) -> str:
        """
        Extract full text from document.

        Args:
            file_path: Path to the file

        Returns:
            Extracted text content
        """
        pass

    def is_supported(self, file_path: str) -> bool:
        """Check if file format is supported."""
        file_extension = file_path.split(".")[-1].lower()
        return file_extension in self.supported_formats

    def extract_entities(self, text: str) -> List[ParsedEntity]:
        """
        Extract entities from text. Override in subclasses for specific implementations.

        Args:
            text: Text to extract entities from

        Returns:
            List of extracted entities
        """
        return []

    def chunk_text(self, text: str, document_id: str) -> List[ParsedChunk]:
        """
        Split text into chunks. Override in subclasses for specific implementations.

        Args:
            text: Text to chunk
            document_id: ID of source document

        Returns:
            List of text chunks
        """
        return []

    def validate_parsed_document(self, doc: ParsedDocument) -> bool:
        """
        Validate parsed document for completeness.

        Args:
            doc: Document to validate

        Returns:
            True if document is valid

        Raises:
            ValueError: If document is invalid
        """
        if not doc.document_id:
            raise ValueError("Document must have a valid ID")
        if not doc.document_type:
            raise ValueError("Document must have a document type")
        if not doc.full_text:
            raise ValueError("Document must contain text content")

        return True
