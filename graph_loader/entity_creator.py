"""
Entity creation and management for Neo4j graph.
"""

import logging
from typing import Any, Dict, List, Optional

from graph_loader.neo4j_connector import Neo4jConnector
from parsers.base_parser import ParsedEntity

logger = logging.getLogger(__name__)


class EntityCreator:
    """Creates and manages entities (nodes) in the Neo4j graph."""

    def __init__(self, connector: Neo4jConnector):
        """
        Initialize entity creator.

        Args:
            connector: Neo4jConnector instance
        """
        self.connector = connector

    def create_from_parsed_entity(self, entity: ParsedEntity) -> Optional[str]:
        """
        Create a node from parsed entity.

        Args:
            entity: ParsedEntity to create

        Returns:
            Node ID if successful
        """
        try:
            node_id = self.connector.create_node(entity.entity_type, entity.properties)
            logger.info(f"Created {entity.entity_type} node: {entity.entity_id}")
            return node_id
        except Exception as e:
            logger.error(f"Failed to create entity {entity.entity_id}: {e}")
            return None

    def create_batch(self, entities: List[ParsedEntity]) -> int:
        """
        Create multiple entities in batch.

        Args:
            entities: List of ParsedEntity objects

        Returns:
            Number of successfully created entities
        """
        count = 0
        for entity in entities:
            if self.create_from_parsed_entity(entity):
                count += 1
        logger.info(f"Batch creation complete: {count}/{len(entities)} entities created")
        return count

    def create_procurement(
        self,
        proc_id: str,
        number: str,
        status: str,
        budget: float,
        description: str = "",
        **kwargs,
    ) -> Optional[str]:
        """
        Create a Procurement node.

        Args:
            proc_id: Unique procurement ID
            number: Procurement number
            status: Status (active, closed, etc.)
            budget: Budget amount
            description: Description
            **kwargs: Additional properties

        Returns:
            Node ID if successful
        """
        properties = {
            "id": proc_id,
            "number": number,
            "status": status,
            "budget": budget,
            "description": description,
            **kwargs,
        }
        return self.connector.create_node("Procurement", properties)

    def create_organization(
        self,
        org_id: str,
        name: str,
        inn: str = "",
        region: str = "",
        **kwargs,
    ) -> Optional[str]:
        """
        Create an Organization node.

        Args:
            org_id: Unique organization ID
            name: Organization name
            inn: Tax identification number
            region: Region/location
            **kwargs: Additional properties

        Returns:
            Node ID if successful
        """
        properties = {
            "id": org_id,
            "name": name,
            "inn": inn,
            "region": region,
            **kwargs,
        }
        return self.connector.create_node("Organization", properties)

    def create_participant(
        self,
        participant_id: str,
        name: str,
        email: str = "",
        phone: str = "",
        region: str = "",
        **kwargs,
    ) -> Optional[str]:
        """
        Create a Participant node.

        Args:
            participant_id: Unique participant ID
            name: Participant name
            email: Email address
            phone: Phone number
            region: Region/location
            **kwargs: Additional properties

        Returns:
            Node ID if successful
        """
        properties = {
            "id": participant_id,
            "name": name,
            "email": email,
            "phone": phone,
            "region": region,
            **kwargs,
        }
        return self.connector.create_node("Participant", properties)

    def create_lot(
        self,
        lot_id: str,
        number: str,
        description: str = "",
        quantity: int = 0,
        unit: str = "",
        **kwargs,
    ) -> Optional[str]:
        """Create a Lot node."""
        properties = {
            "id": lot_id,
            "number": number,
            "description": description,
            "quantity": quantity,
            "unit": unit,
            **kwargs,
        }
        return self.connector.create_node("Lot", properties)

    def create_requirement(
        self,
        req_id: str,
        description: str,
        is_mandatory: bool = True,
        category: str = "",
        **kwargs,
    ) -> Optional[str]:
        """Create a Requirement node."""
        properties = {
            "id": req_id,
            "description": description,
            "is_mandatory": is_mandatory,
            "category": category,
            **kwargs,
        }
        return self.connector.create_node("Requirement", properties)

    def create_document(
        self,
        doc_id: str,
        doc_type: str,
        content: str = "",
        **kwargs,
    ) -> Optional[str]:
        """Create a Document node."""
        properties = {
            "id": doc_id,
            "type": doc_type,
            "content": content,
            **kwargs,
        }
        return self.connector.create_node("Document", properties)

    def create_chunk(
        self,
        chunk_id: str,
        content: str,
        source_document_id: str,
        chunk_type: str = "text",
        chunk_index: int = 0,
        embedding: Optional[List[float]] = None,
        **kwargs,
    ) -> Optional[str]:
        """Create a Chunk node."""
        properties = {
            "id": chunk_id,
            "content": content,
            "source_document_id": source_document_id,
            "chunk_type": chunk_type,
            "chunk_index": chunk_index,
            **kwargs,
        }
        if embedding:
            properties["embedding"] = embedding

        return self.connector.create_node("Chunk", properties)

    def create_tender(
        self,
        tender_id: str,
        tender_type: str,
        status: str,
        **kwargs,
    ) -> Optional[str]:
        """Create a Tender node."""
        properties = {
            "id": tender_id,
            "type": tender_type,
            "status": status,
            **kwargs,
        }
        return self.connector.create_node("Tender", properties)

    def update_entity(self, entity_type: str, entity_id: str, properties: Dict[str, Any]) -> bool:
        """
        Update entity properties.

        Args:
            entity_type: Type of entity (label)
            entity_id: Entity ID
            properties: Properties to update

        Returns:
            True if update successful
        """
        try:
            cypher = f"""
            MATCH (n:{entity_type} {{ id: $id }})
            SET n += $props
            RETURN n
            """
            result = self.connector.query(cypher, {"id": entity_id, "props": properties})
            return bool(result)
        except Exception as e:
            logger.error(f"Failed to update entity {entity_id}: {e}")
            return False

    def get_entity(self, entity_type: str, entity_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve entity data.

        Args:
            entity_type: Type of entity
            entity_id: Entity ID

        Returns:
            Entity properties or None
        """
        return self.connector.get_node_by_id(entity_type, entity_id)
