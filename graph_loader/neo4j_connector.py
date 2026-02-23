"""
Neo4j database connection and management.
"""

import logging
from typing import Any, Dict, List, Optional

from neo4j import GraphDatabase, Session
from neo4j.exceptions import Neo4jError

from config.schema import NEO4J_SCHEMA_CYPHER, validate_node_properties, validate_relationship_properties
from config.settings import settings

logger = logging.getLogger(__name__)


class Neo4jConnector:
    """Manages Neo4j database connections and operations."""

    def __init__(self, uri: Optional[str] = None, user: Optional[str] = None, password: Optional[str] = None):
        """
        Initialize Neo4j connector.

        Args:
            uri: Neo4j connection URI (default from settings)
            user: Neo4j username (default from settings)
            password: Neo4j password (default from settings)
        """
        self.uri = uri or settings.neo4j_uri
        self.user = user or settings.neo4j_user
        self.password = password or settings.neo4j_password
        self.driver = None
        self._session = None

    def connect(self) -> bool:
        """
        Connect to Neo4j database.

        Returns:
            True if connection successful

        Raises:
            Neo4jError: If connection fails
        """
        try:
            self.driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))
            # Test connection
            self.driver.verify_connectivity()
            logger.info(f"Connected to Neo4j at {self.uri}")
            return True
        except Neo4jError as e:
            logger.error(f"Failed to connect to Neo4j: {e}")
            raise

    def disconnect(self) -> None:
        """Close Neo4j connection."""
        if self.driver:
            self.driver.close()
            logger.info("Disconnected from Neo4j")

    def _get_session(self) -> Session:
        """Get or create Neo4j session."""
        if not self.driver:
            raise RuntimeError("Not connected to Neo4j. Call connect() first.")
        return self.driver.session(database=settings.neo4j_database)

    def initialize_schema(self) -> bool:
        """
        Initialize database schema (constraints and indexes).

        Returns:
            True if schema initialization successful
        """
        session = self._get_session()
        try:
            for cypher in NEO4J_SCHEMA_CYPHER:
                session.run(cypher)
                logger.debug(f"Executed schema cypher: {cypher[:50]}...")
            logger.info("Schema initialization completed")
            return True
        except Neo4jError as e:
            logger.error(f"Failed to initialize schema: {e}")
            return False
        finally:
            session.close()

    def create_node(self, label: str, properties: Dict[str, Any]) -> Optional[str]:
        """
        Create a node in Neo4j using MERGE (upsert).

        Args:
            label: Node label
            properties: Node properties

        Returns:
            Node ID if successful, None otherwise

        Raises:
            ValueError: If properties are invalid
        """
        validate_node_properties(label, properties)

        session = self._get_session()
        try:
            # Build MERGE query with properties
            prop_string = ", ".join([f"n.{k} = ${k}" for k in properties.keys()])
            cypher = f"""
            MERGE (n:{label} {{ id: $id }})
            SET {prop_string}
            RETURN id(n) as node_id
            """

            result = session.run(cypher, {**properties, "id": properties.get("id", str(properties))})
            record = result.single()

            if record:
                logger.debug(f"Created/merged {label} node with ID: {properties.get('id')}")
                return str(record["node_id"])
            return None

        except Neo4jError as e:
            logger.error(f"Failed to create {label} node: {e}")
            return None
        finally:
            session.close()

    def create_relationship(
        self,
        from_label: str,
        from_id: str,
        rel_type: str,
        to_label: str,
        to_id: str,
        properties: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        Create a relationship between two nodes.

        Args:
            from_label: Label of source node
            from_id: ID of source node
            rel_type: Relationship type
            to_label: Label of target node
            to_id: ID of target node
            properties: Relationship properties

        Returns:
            True if relationship created successfully

        Raises:
            ValueError: If relationship is invalid
        """
        validate_relationship_properties(rel_type, from_label, to_label, properties or {})

        session = self._get_session()
        try:
            if properties:
                prop_string = ", ".join([f"r.{k} = ${k}" for k in properties.keys()])
                cypher = f"""
                MATCH (from:{from_label} {{ id: $from_id }})
                MATCH (to:{to_label} {{ id: $to_id }})
                MERGE (from)-[r:{rel_type}]->(to)
                SET {prop_string}
                """
                session.run(cypher, {**properties, "from_id": from_id, "to_id": to_id})
            else:
                cypher = f"""
                MATCH (from:{from_label} {{ id: $from_id }})
                MATCH (to:{to_label} {{ id: $to_id }})
                MERGE (from)-[r:{rel_type}]->(to)
                """
                session.run(cypher, from_id=from_id, to_id=to_id)

            logger.debug(f"Created {rel_type} relationship: {from_label}({from_id})->{to_label}({to_id})")
            return True

        except Neo4jError as e:
            logger.error(f"Failed to create relationship: {e}")
            return False
        finally:
            session.close()

    def create_nodes_batch(self, label: str, nodes: List[Dict[str, Any]]) -> int:
        """
        Create multiple nodes in a single batch operation.

        Args:
            label: Node label
            nodes: List of node properties

        Returns:
            Number of nodes created
        """
        session = self._get_session()
        try:
            count = 0
            for node in nodes:
                if self.create_node(label, node):
                    count += 1
            logger.info(f"Created {count}/{len(nodes)} {label} nodes in batch")
            return count
        except Exception as e:
            logger.error(f"Batch node creation failed: {e}")
            return 0
        finally:
            session.close()

    def query(self, cypher: str, parameters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Execute a Cypher query.

        Args:
            cypher: Cypher query string
            parameters: Query parameters

        Returns:
            List of result records
        """
        session = self._get_session()
        try:
            result = session.run(cypher, parameters or {})
            records = [dict(record) for record in result]
            logger.debug(f"Query returned {len(records)} records")
            return records
        except Neo4jError as e:
            logger.error(f"Query execution failed: {e}")
            return []
        finally:
            session.close()

    def get_node_by_id(self, label: str, node_id: str) -> Optional[Dict[str, Any]]:
        """Get a node by label and ID."""
        session = self._get_session()
        try:
            cypher = f"MATCH (n:{label} {{ id: $id }}) RETURN n"
            result = session.run(cypher, id=node_id)
            record = result.single()
            if record:
                return dict(record["n"])
            return None
        except Neo4jError as e:
            logger.error(f"Failed to get node: {e}")
            return None
        finally:
            session.close()

    def delete_all(self) -> bool:
        """
        Delete all nodes and relationships (WARNING: destructive!).

        Returns:
            True if deletion successful
        """
        session = self._get_session()
        try:
            session.run("MATCH (n) DETACH DELETE n")
            logger.warning("Deleted all nodes and relationships from Neo4j")
            return True
        except Neo4jError as e:
            logger.error(f"Failed to delete all: {e}")
            return False
        finally:
            session.close()

    def get_stats(self) -> Dict[str, Any]:
        """Get database statistics."""
        session = self._get_session()
        try:
            cypher = """
            MATCH (n) RETURN labels(n)[0] as label, count(*) as count
            UNION
            MATCH ()-[r]->() RETURN type(r) as label, count(*) as count
            """
            result = session.run(cypher)
            stats = {}
            for record in result:
                stats[record["label"]] = record["count"]
            return stats
        except Neo4jError as e:
            logger.error(f"Failed to get stats: {e}")
            return {}
        finally:
            session.close()
