"""
DOCX parser for normative documents and regulations.
Optimized for creating Knowledge Graphs from legislation, guides, and methodologies.
"""

from pathlib import Path
from typing import List, Optional

try:
    from docx import Document
except ImportError:
    Document = None

from parsers.base_parser import BaseParser, ParsedChunk, ParsedDocument, ParsedEntity


class DOCXParser(BaseParser):
    """Parser for DOCX documents to extract knowledge and create graphs."""

    def __init__(self):
        """Initialize DOCX parser."""
        super().__init__(parser_name="DOCXParser")
        self.supported_formats = ["docx"]

        if Document is None:
            raise ImportError("python-docx is required. Install with: pip install python-docx")

    def parse(self, file_path: str) -> ParsedDocument:
        """
        Parse DOCX document and extract knowledge.

        Args:
            file_path: Path to DOCX file

        Returns:
            ParsedDocument with extracted knowledge entities
        """
        if not self.is_supported(file_path):
            raise ValueError(f"File format not supported: {file_path}")

        try:
            doc = Document(file_path)
        except Exception as e:
            raise IOError(f"Cannot read DOCX file: {e}")

        # Extract document metadata
        document_id = Path(file_path).stem
        document_type = "regulatory_document"

        # Extract full text
        full_text = self._extract_text_from_docx(doc)

        # Extract knowledge entities
        entities = self._extract_knowledge_entities(doc, document_id)

        # Create chunks from document structure
        chunks = self._create_semantic_chunks(doc, document_id)

        # Create document
        parsed_doc = ParsedDocument(
            document_id=document_id,
            document_type=document_type,
            full_text=full_text,
            entities=entities,
            chunks=chunks,
            metadata={
                "source": file_path,
                "format": "docx",
                "language": "kk",  # Kazakh
                "paragraphs": len(doc.paragraphs),
            },
        )

        self.validate_parsed_document(parsed_doc)
        return parsed_doc

    def extract_text(self, file_path: str) -> str:
        """Extract full text from DOCX file."""
        try:
            doc = Document(file_path)
        except Exception as e:
            raise ValueError(f"Cannot read DOCX file: {e}")

        return self._extract_text_from_docx(doc)

    def _extract_text_from_docx(self, doc) -> str:
        """Extract all text from DOCX document."""
        text_parts = []

        for para in doc.paragraphs:
            if para.text.strip():
                text_parts.append(para.text.strip())

        # Add text from tables if present
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    if cell.text.strip():
                        text_parts.append(cell.text.strip())

        return "\n".join(text_parts)

    def _extract_knowledge_entities(self, doc, document_id: str) -> List[ParsedEntity]:
        """
        Extract knowledge entities (concepts, rules, processes) from document.
        """
        entities = []
        para_count = 0

        for para in doc.paragraphs:
            text = para.text.strip()
            if not text:
                continue

            para_count += 1
            style = para.style.name

            # Detect entity type based on content and style
            entity_type = self._detect_entity_type(text, style, para_count)

            if entity_type:
                entity_id = f"{document_id}_{entity_type}_{para_count}"

                entity = ParsedEntity(
                    entity_type=entity_type,
                    entity_id=entity_id,
                    properties={
                        "text": text,
                        "source_document": document_id,
                        "paragraph_number": para_count,
                        "style": style,
                        "language": "kk",
                    },
                )
                entities.append(entity)

        return entities

    def _detect_entity_type(self, text: str, style: str, para_num: int) -> Optional[str]:
        """
        Detect entity type from text content and style.

        Returns: 'Concept', 'Rule', 'Process', 'Definition', 'Procedure', or None
        """
        text_lower = text.lower()

        # Detect definitions (usually short phrases followed by ":"​ or "болады", "деп")
        if ":" in text or text_lower.endswith(("деп", "болады", "саналады")):
            if len(text) < 200:  # Usually definitions are shorter
                return "Definition"

        # Detect rules (contains conditional language)
        rule_keywords = [
            "мің",  # must
            "рұқсат",  # allowed
            "тыйым",  # forbidden
            "міндет",  # obligation
            "құқық",  # right
            "шарт",  # condition
            "негіз",  # basis
            "орындау",  # implement
            "ең болмағанда",  # at least
        ]
        if any(kw in text_lower for kw in rule_keywords):
            return "Rule"

        # Detect procedures/processes (contains step numbers or sequential language)
        if any(f"{i})" in text for i in range(1, 20)) or any(
            kw in text_lower for kw in ["қадам", "этап", "түрінде", "ретінде"]
        ):
            return "Procedure"

        # Detect processes (action-oriented)
        if any(
            kw in text_lower
            for kw in ["процесс", "рәсім", "тәртіп", "реестр", "тіркеу", "ұсыну"]
        ):
            return "Process"

        # Default to Concept for other paragraphs
        if len(text) > 50:  # Only concepts with meaningful content
            return "Concept"

        return None

    def _create_semantic_chunks(self, doc, document_id: str) -> List[ParsedChunk]:
        """
        Create semantic chunks preserving document structure.
        Chunks are created at paragraph level for better semantic coherence.
        """
        chunks = []
        chunk_index = 0
        accumulated_text = ""
        accumulated_paras = 0

        for para in doc.paragraphs:
            text = para.text.strip()
            if not text:
                continue

            accumulated_text += text + "\n"
            accumulated_paras += 1

            # Create chunk every 3-5 paragraphs or when text is long enough
            if accumulated_paras >= 3 or len(accumulated_text) > 1000:
                if accumulated_text.strip():
                    chunk = ParsedChunk(
                        content=accumulated_text.strip(),
                        chunk_type="regulation",
                        source_document_id=document_id,
                        chunk_index=chunk_index,
                        metadata={
                            "paragraphs_count": accumulated_paras,
                            "language": "kk",
                        },
                    )
                    chunks.append(chunk)
                    chunk_index += 1

                # Create overlap
                accumulated_text = text + "\n"
                accumulated_paras = 1

        # Add last chunk
        if accumulated_text.strip():
            chunk = ParsedChunk(
                content=accumulated_text.strip(),
                chunk_type="regulation",
                source_document_id=document_id,
                chunk_index=chunk_index,
                metadata={
                    "paragraphs_count": accumulated_paras,
                    "language": "kk",
                },
            )
            chunks.append(chunk)

        return chunks
