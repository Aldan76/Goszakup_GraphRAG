"""
PDF parser for government procurement documents.
"""

from pathlib import Path
from typing import List

try:
    import pdfplumber
except ImportError:
    pdfplumber = None

from parsers.base_parser import BaseParser, ParsedChunk, ParsedDocument, ParsedEntity


class PDFParser(BaseParser):
    """Parser for PDF formatted procurement data."""

    def __init__(self):
        """Initialize PDF parser."""
        super().__init__(parser_name="PDFParser")
        self.supported_formats = ["pdf"]
        if pdfplumber is None:
            raise ImportError("pdfplumber is required for PDF parsing. Install with: pip install pdfplumber")

    def parse(self, file_path: str) -> ParsedDocument:
        """
        Parse PDF procurement document.

        Args:
            file_path: Path to PDF file

        Returns:
            ParsedDocument with extracted data

        Raises:
            ValueError: If PDF format is invalid
            IOError: If file cannot be read
        """
        if not self.is_supported(file_path):
            raise ValueError(f"File format not supported: {file_path}")

        try:
            with pdfplumber.open(file_path) as pdf:
                document_id = Path(file_path).stem
                document_type = "pdf_document"

                # Extract full text
                full_text = self._extract_text_from_pdf(pdf)

                # Extract entities (simplified for PDF - would need more sophisticated NLP)
                entities = self._extract_entities_from_text(full_text)

                # Chunk text
                chunks = self._chunk_text(full_text, document_id)

        except Exception as e:
            raise IOError(f"Cannot read PDF file: {e}")

        # Create document
        doc = ParsedDocument(
            document_id=str(document_id),
            document_type=document_type,
            full_text=full_text,
            entities=entities,
            chunks=chunks,
            metadata={"source": file_path, "format": "pdf", "pages": len(pdf.pages)},
        )

        self.validate_parsed_document(doc)
        return doc

    def extract_text(self, file_path: str) -> str:
        """Extract full text from PDF file."""
        try:
            with pdfplumber.open(file_path) as pdf:
                return self._extract_text_from_pdf(pdf)
        except Exception as e:
            raise ValueError(f"Cannot read PDF file: {e}")

    def _extract_text_from_pdf(self, pdf) -> str:
        """Extract text from all PDF pages."""
        text_parts = []

        for page in pdf.pages:
            # Extract regular text
            page_text = page.extract_text() or ""
            if page_text:
                text_parts.append(page_text)

            # Extract table data if present
            tables = page.extract_tables()
            if tables:
                for table in tables:
                    for row in table:
                        row_text = " | ".join(str(cell or "") for cell in row)
                        text_parts.append(row_text)

        return "\n".join(text_parts)

    def _extract_entities_from_text(self, text: str) -> List[ParsedEntity]:
        """
        Extract entities from text using simple pattern matching.
        This is a simplified implementation - in production would use NLP.
        """
        entities = []

        # Look for procurement number patterns (e.g., "Закупка №123" or "Procurement #123")
        import re

        # Pattern for procurement numbers
        proc_patterns = [
            r"(?:Закупка|Procurement|Тендер|Tender)[\s#№]*(\d+)",
            r"(?:тендер|procurement)[\s:]*([0-9]+)",
        ]

        for pattern in proc_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                proc_id = f"proc_{match.group(1)}"
                entity = ParsedEntity(
                    entity_type="Procurement",
                    entity_id=proc_id,
                    properties={"number": match.group(1)},
                )
                # Avoid duplicates
                if not any(e.entity_id == entity.entity_id for e in entities):
                    entities.append(entity)

        return entities

    def _chunk_text(self, text: str, document_id: str, chunk_size: int = 500, overlap: int = 100) -> List[ParsedChunk]:
        """Split text into chunks."""
        chunks = []

        # Split by paragraphs first (separated by multiple newlines)
        paragraphs = text.split("\n\n")

        current_chunk = ""
        chunk_index = 0

        for paragraph in paragraphs:
            # Add paragraph to current chunk if it fits
            if len(current_chunk) + len(paragraph) <= chunk_size:
                current_chunk += "\n" + paragraph if current_chunk else paragraph
            else:
                # Save current chunk if not empty
                if current_chunk.strip():
                    chunk = ParsedChunk(
                        content=current_chunk.strip(),
                        chunk_type="text",
                        source_document_id=document_id,
                        chunk_index=chunk_index,
                    )
                    chunks.append(chunk)
                    chunk_index += 1

                # Create overlap
                overlap_lines = current_chunk.split("\n")[-1:]  # Last line
                overlap_text = "\n".join(overlap_lines) if overlap_lines else ""
                current_chunk = overlap_text + "\n" + paragraph if overlap_text else paragraph

        # Add last chunk
        if current_chunk.strip():
            chunk = ParsedChunk(
                content=current_chunk.strip(),
                chunk_type="text",
                source_document_id=document_id,
                chunk_index=chunk_index,
            )
            chunks.append(chunk)

        return chunks
