"""
JSON parser for government procurement data.
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from parsers.base_parser import BaseParser, ParsedChunk, ParsedDocument, ParsedEntity


class JSONParser(BaseParser):
    """Parser for JSON formatted procurement data."""

    def __init__(self):
        """Initialize JSON parser."""
        super().__init__(parser_name="JSONParser")
        self.supported_formats = ["json"]

    def parse(self, file_path: str) -> ParsedDocument:
        """
        Parse JSON procurement document.

        Args:
            file_path: Path to JSON file

        Returns:
            ParsedDocument with extracted data

        Raises:
            ValueError: If JSON format is invalid
            IOError: If file cannot be read
        """
        if not self.is_supported(file_path):
            raise ValueError(f"File format not supported: {file_path}")

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON format: {e}")
        except IOError as e:
            raise IOError(f"Cannot read file: {e}")

        # Extract document ID and type
        document_id = data.get("id") or Path(file_path).stem
        document_type = data.get("type", "procurement_data")

        # Extract full text
        full_text = self._extract_text_from_data(data)

        # Extract entities
        entities = self._extract_entities_from_json(data)

        # Chunk text
        chunks = self._chunk_text(full_text, document_id)

        # Create document
        doc = ParsedDocument(
            document_id=str(document_id),
            document_type=document_type,
            full_text=full_text,
            entities=entities,
            chunks=chunks,
            metadata={"source": file_path, "format": "json"},
        )

        self.validate_parsed_document(doc)
        return doc

    def extract_text(self, file_path: str) -> str:
        """Extract full text from JSON file."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            raise ValueError(f"Cannot read file: {e}")

        return self._extract_text_from_data(data)

    def _extract_text_from_data(self, data: Dict[str, Any]) -> str:
        """Extract readable text from JSON data structure."""
        text_parts = []

        # Add title if exists
        if "title" in data:
            text_parts.append(str(data["title"]))
        elif "number" in data:
            text_parts.append(f"Procurement #{data['number']}")

        # Add description
        if "description" in data:
            text_parts.append(str(data["description"]))

        # Add lots
        if "lots" in data and isinstance(data["lots"], list):
            for lot in data["lots"]:
                text_parts.append(f"Lot {lot.get('number', 'N/A')}: {lot.get('description', '')}")

        # Add requirements
        if "requirements" in data and isinstance(data["requirements"], list):
            text_parts.append("Requirements:")
            for req in data["requirements"]:
                text_parts.append(f"- {req.get('description', '')}")

        # Add organization info
        if "organization" in data:
            org = data["organization"]
            text_parts.append(f"Organization: {org.get('name', '')} ({org.get('region', '')})")

        # Add all text values recursively
        text_parts.extend(self._extract_text_recursive(data, depth=0))

        return "\n".join(text_parts)

    def _extract_text_recursive(self, obj: Any, depth: int = 0, max_depth: int = 5) -> List[str]:
        """Recursively extract text from nested structures."""
        if depth >= max_depth:
            return []

        text_parts = []

        if isinstance(obj, dict):
            for key, value in obj.items():
                if key in ["id", "type", "number"]:  # Skip IDs and types
                    continue
                if isinstance(value, str) and len(value) > 10:
                    text_parts.append(value)
                elif isinstance(value, (dict, list)):
                    text_parts.extend(self._extract_text_recursive(value, depth + 1, max_depth))

        elif isinstance(obj, list):
            for item in obj:
                if isinstance(item, str) and len(item) > 10:
                    text_parts.append(item)
                elif isinstance(item, (dict, list)):
                    text_parts.extend(self._extract_text_recursive(item, depth + 1, max_depth))

        return text_parts

    def _extract_entities_from_json(self, data: Dict[str, Any]) -> List[ParsedEntity]:
        """Extract entities from JSON data."""
        entities = []

        # Extract procurement entity
        if "id" in data:
            procurement_entity = ParsedEntity(
                entity_type="Procurement",
                entity_id=str(data["id"]),
                properties={
                    "number": data.get("number"),
                    "status": data.get("status", "active"),
                    "budget": data.get("budget"),
                    "description": data.get("description", ""),
                    "deadline": data.get("deadline"),
                    "date_created": data.get("date_created"),
                },
            )
            entities.append(procurement_entity)

        # Extract organization entity
        if "organization" in data and isinstance(data["organization"], dict):
            org = data["organization"]
            organization_entity = ParsedEntity(
                entity_type="Organization",
                entity_id=str(org.get("id") or org.get("name")),
                properties={
                    "name": org.get("name"),
                    "inn": org.get("inn"),
                    "region": org.get("region"),
                    "contact_info": org.get("contact_info"),
                },
            )
            entities.append(organization_entity)

        # Extract lots
        if "lots" in data and isinstance(data["lots"], list):
            for lot in data["lots"]:
                lot_entity = ParsedEntity(
                    entity_type="Lot",
                    entity_id=f"{data.get('id', 'proc')}_lot_{lot.get('id', lot.get('number'))}",
                    properties={
                        "number": lot.get("number"),
                        "description": lot.get("description"),
                        "quantity": lot.get("quantity"),
                        "unit": lot.get("unit"),
                        "expected_price": lot.get("expected_price"),
                        "status": lot.get("status"),
                    },
                )
                entities.append(lot_entity)

        # Extract requirements
        if "requirements" in data and isinstance(data["requirements"], list):
            for req in data["requirements"]:
                req_id = req.get("id") or f"req_{len(entities)}"
                requirement_entity = ParsedEntity(
                    entity_type="Requirement",
                    entity_id=str(req_id),
                    properties={
                        "description": req.get("description"),
                        "is_mandatory": req.get("is_mandatory", True),
                        "category": req.get("category"),
                    },
                )
                entities.append(requirement_entity)

        # Extract participants
        if "participants" in data and isinstance(data["participants"], list):
            for participant in data["participants"]:
                participant_entity = ParsedEntity(
                    entity_type="Participant",
                    entity_id=str(participant.get("id") or participant.get("name")),
                    properties={
                        "name": participant.get("name"),
                        "registration_number": participant.get("registration_number"),
                        "email": participant.get("email"),
                        "phone": participant.get("phone"),
                        "region": participant.get("region"),
                    },
                )
                entities.append(participant_entity)

        return entities

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
