"""
XML parser for government procurement data in standard formats.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional
from xml.etree import ElementTree as ET

from parsers.base_parser import BaseParser, ParsedChunk, ParsedDocument, ParsedEntity


class XMLParser(BaseParser):
    """Parser for XML formatted procurement data."""

    def __init__(self):
        """Initialize XML parser."""
        super().__init__(parser_name="XMLParser")
        self.supported_formats = ["xml"]

    def parse(self, file_path: str) -> ParsedDocument:
        """
        Parse XML procurement document.

        Args:
            file_path: Path to XML file

        Returns:
            ParsedDocument with extracted data

        Raises:
            ValueError: If XML format is invalid
            IOError: If file cannot be read
        """
        if not self.is_supported(file_path):
            raise ValueError(f"File format not supported: {file_path}")

        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
        except ET.ParseError as e:
            raise ValueError(f"Invalid XML format: {e}")
        except IOError as e:
            raise IOError(f"Cannot read file: {e}")

        # Extract document ID and type
        document_id = root.get("id") or Path(file_path).stem
        document_type = root.tag

        # Extract full text
        full_text = self._extract_text_from_element(root)

        # Extract entities
        entities = self._extract_entities_from_xml(root)

        # Chunk text
        chunks = self._chunk_text(full_text, str(document_id))

        # Create document
        doc = ParsedDocument(
            document_id=str(document_id),
            document_type=document_type,
            full_text=full_text,
            entities=entities,
            chunks=chunks,
            metadata={"source": file_path, "format": "xml"},
        )

        self.validate_parsed_document(doc)
        return doc

    def extract_text(self, file_path: str) -> str:
        """Extract full text from XML file."""
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
        except (ET.ParseError, IOError) as e:
            raise ValueError(f"Cannot read file: {e}")

        return self._extract_text_from_element(root)

    def _extract_text_from_element(self, element: ET.Element, depth: int = 0, max_depth: int = 10) -> str:
        """Extract text from XML element recursively."""
        if depth >= max_depth:
            return ""

        text_parts = []

        # Add element text
        if element.text and element.text.strip():
            text_parts.append(element.text.strip())

        # Process child elements
        for child in element:
            child_text = self._extract_text_from_element(child, depth + 1, max_depth)
            if child_text:
                text_parts.append(child_text)

            # Add tail text
            if child.tail and child.tail.strip():
                text_parts.append(child.tail.strip())

        return " ".join(text_parts)

    def _extract_entities_from_xml(self, root: ET.Element) -> List[ParsedEntity]:
        """Extract entities from XML structure."""
        entities = []

        # Extract procurement
        procurement = root.find(".//procurement")
        if procurement is not None:
            proc_entity = ParsedEntity(
                entity_type="Procurement",
                entity_id=procurement.get("id", root.get("id")),
                properties={
                    "number": self._get_text(procurement, "number"),
                    "status": self._get_text(procurement, "status"),
                    "budget": self._get_text(procurement, "budget"),
                    "description": self._get_text(procurement, "description"),
                    "deadline": self._get_text(procurement, "deadline"),
                    "date_created": self._get_text(procurement, "date_created"),
                },
            )
            entities.append(proc_entity)

        # Extract organization
        organization = root.find(".//organization")
        if organization is not None:
            org_entity = ParsedEntity(
                entity_type="Organization",
                entity_id=organization.get("id"),
                properties={
                    "name": self._get_text(organization, "name"),
                    "inn": self._get_text(organization, "inn"),
                    "region": self._get_text(organization, "region"),
                    "contact_info": self._get_text(organization, "contact_info"),
                },
            )
            entities.append(org_entity)

        # Extract lots
        for lot in root.findall(".//lot"):
            lot_entity = ParsedEntity(
                entity_type="Lot",
                entity_id=lot.get("id"),
                properties={
                    "number": self._get_text(lot, "number"),
                    "description": self._get_text(lot, "description"),
                    "quantity": self._get_text(lot, "quantity"),
                    "unit": self._get_text(lot, "unit"),
                    "expected_price": self._get_text(lot, "expected_price"),
                    "status": self._get_text(lot, "status"),
                },
            )
            entities.append(lot_entity)

        # Extract requirements
        for requirement in root.findall(".//requirement"):
            req_entity = ParsedEntity(
                entity_type="Requirement",
                entity_id=requirement.get("id"),
                properties={
                    "description": self._get_text(requirement, "description"),
                    "is_mandatory": self._get_text(requirement, "is_mandatory") == "true",
                    "category": self._get_text(requirement, "category"),
                },
            )
            entities.append(req_entity)

        # Extract participants
        for participant in root.findall(".//participant"):
            participant_entity = ParsedEntity(
                entity_type="Participant",
                entity_id=participant.get("id"),
                properties={
                    "name": self._get_text(participant, "name"),
                    "registration_number": self._get_text(participant, "registration_number"),
                    "email": self._get_text(participant, "email"),
                    "phone": self._get_text(participant, "phone"),
                    "region": self._get_text(participant, "region"),
                },
            )
            entities.append(participant_entity)

        # Extract documents
        for document in root.findall(".//document"):
            doc_entity = ParsedEntity(
                entity_type="Document",
                entity_id=document.get("id"),
                properties={
                    "type": self._get_text(document, "type"),
                    "content": self._get_text(document, "content"),
                    "created_date": self._get_text(document, "created_date"),
                },
            )
            entities.append(doc_entity)

        return entities

    def _get_text(self, element: ET.Element, tag: str, default: str = "") -> str:
        """Get text from child element."""
        child = element.find(tag)
        if child is not None and child.text:
            return child.text.strip()
        return default

    def _chunk_text(self, text: str, document_id: str, chunk_size: int = 500, overlap: int = 100) -> List[ParsedChunk]:
        """Split text into chunks."""
        chunks = []
        sentences = text.split(". ")

        current_chunk = ""
        chunk_index = 0

        for sentence in sentences:
            # Add period back
            sentence = sentence + "." if not sentence.endswith(".") else sentence

            if len(current_chunk) + len(sentence) <= chunk_size:
                current_chunk += " " + sentence
            else:
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
                overlap_text = current_chunk[-overlap:] if len(current_chunk) > overlap else current_chunk
                current_chunk = overlap_text + " " + sentence

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
