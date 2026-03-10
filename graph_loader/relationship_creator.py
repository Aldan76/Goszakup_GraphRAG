"""
Relationship creation and management for Neo4j graph.
"""

import logging
from typing import Any, Dict, Optional

from graph_loader.neo4j_connector import Neo4jConnector

logger = logging.getLogger(__name__)


class RelationshipCreator:
    """Creates and manages relationships (edges) in the Neo4j graph."""

    def __init__(self, connector: Neo4jConnector):
        """
        Initialize relationship creator.

        Args:
            connector: Neo4jConnector instance
        """
        self.connector = connector

    def create_has_lot(self, procurement_id: str, lot_id: str) -> bool:
        """Create Procurement -[HAS_LOT]-> Lot relationship."""
        return self.connector.create_relationship(
            "Procurement", procurement_id, "HAS_LOT", "Lot", lot_id, {"created_at": self._now()}
        )

    def create_organized_by(self, procurement_id: str, organization_id: str) -> bool:
        """Create Procurement -[ORGANIZED_BY]-> Organization relationship."""
        return self.connector.create_relationship(
            "Procurement", procurement_id, "ORGANIZED_BY", "Organization", organization_id, {"created_at": self._now()}
        )

    def create_included_in_tender(self, lot_id: str, tender_id: str) -> bool:
        """Create Lot -[INCLUDED_IN_TENDER]-> Tender relationship."""
        return self.connector.create_relationship(
            "Lot", lot_id, "INCLUDED_IN_TENDER", "Tender", tender_id, {"created_at": self._now()}
        )

    def create_received_bid_from(
        self, tender_id: str, participant_id: str, bid_price: Optional[float] = None
    ) -> bool:
        """Create Tender -[RECEIVED_BID_FROM]-> Participant relationship."""
        props = {"created_at": self._now()}
        if bid_price is not None:
            props["bid_price"] = bid_price

        return self.connector.create_relationship(
            "Tender", tender_id, "RECEIVED_BID_FROM", "Participant", participant_id, props
        )

    def create_submitted_document(self, participant_id: str, document_id: str) -> bool:
        """Create Participant -[SUBMITTED_DOCUMENT]-> Document relationship."""
        return self.connector.create_relationship(
            "Participant", participant_id, "SUBMITTED_DOCUMENT", "Document", document_id, {"created_at": self._now()}
        )

    def create_has_requirement(self, procurement_id: str, requirement_id: str) -> bool:
        """Create Procurement -[HAS_REQUIREMENT]-> Requirement relationship."""
        return self.connector.create_relationship(
            "Procurement", procurement_id, "HAS_REQUIREMENT", "Requirement", requirement_id, {"created_at": self._now()}
        )

    def create_lot_has_requirement(self, lot_id: str, requirement_id: str) -> bool:
        """Create Lot -[HAS_REQUIREMENT]-> Requirement relationship."""
        return self.connector.create_relationship(
            "Lot", lot_id, "HAS_REQUIREMENT", "Requirement", requirement_id, {"created_at": self._now()}
        )

    def create_contains_chunk(self, document_id: str, chunk_id: str) -> bool:
        """Create Document -[CONTAINS_CHUNK]-> Chunk relationship."""
        return self.connector.create_relationship(
            "Document", document_id, "CONTAINS_CHUNK", "Chunk", chunk_id, {"created_at": self._now()}
        )

    def create_registered_in(self, participant_id: str, organization_id: str) -> bool:
        """Create Participant -[REGISTERED_IN]-> Organization relationship."""
        return self.connector.create_relationship(
            "Participant", participant_id, "REGISTERED_IN", "Organization", organization_id, {"created_at": self._now()}
        )

    def _now(self) -> str:
        """Get current timestamp in ISO format."""
        from datetime import datetime

        return datetime.utcnow().isoformat()
