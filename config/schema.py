"""
Neo4j database schema initialization with Cypher commands.
"""

# Cypher commands to create constraints and indexes
NEO4J_SCHEMA_CYPHER = [
    # Create constraints (uniqueness)
    """
    CREATE CONSTRAINT procurement_id_unique
    IF NOT EXISTS FOR (p:Procurement)
    REQUIRE p.id IS UNIQUE
    """,
    """
    CREATE CONSTRAINT participant_id_unique
    IF NOT EXISTS FOR (p:Participant)
    REQUIRE p.id IS UNIQUE
    """,
    """
    CREATE CONSTRAINT organization_id_unique
    IF NOT EXISTS FOR (o:Organization)
    REQUIRE o.id IS UNIQUE
    """,
    """
    CREATE CONSTRAINT lot_id_unique
    IF NOT EXISTS FOR (l:Lot)
    REQUIRE l.id IS UNIQUE
    """,
    """
    CREATE CONSTRAINT tender_id_unique
    IF NOT EXISTS FOR (t:Tender)
    REQUIRE t.id IS UNIQUE
    """,
    """
    CREATE CONSTRAINT document_id_unique
    IF NOT EXISTS FOR (d:Document)
    REQUIRE d.id IS UNIQUE
    """,
    """
    CREATE CONSTRAINT requirement_id_unique
    IF NOT EXISTS FOR (r:Requirement)
    REQUIRE r.id IS UNIQUE
    """,
    """
    CREATE CONSTRAINT chunk_id_unique
    IF NOT EXISTS FOR (c:Chunk)
    REQUIRE c.id IS UNIQUE
    """,
    # Create indexes for search
    """
    CREATE INDEX procurement_number_idx
    IF NOT EXISTS FOR (p:Procurement)
    ON (p.number)
    """,
    """
    CREATE INDEX procurement_status_idx
    IF NOT EXISTS FOR (p:Procurement)
    ON (p.status)
    """,
    """
    CREATE INDEX organization_name_idx
    IF NOT EXISTS FOR (o:Organization)
    ON (o.name)
    """,
    """
    CREATE INDEX participant_name_idx
    IF NOT EXISTS FOR (p:Participant)
    ON (p.name)
    """,
    """
    CREATE INDEX participant_region_idx
    IF NOT EXISTS FOR (p:Participant)
    ON (p.region)
    """,
    """
    CREATE INDEX lot_status_idx
    IF NOT EXISTS FOR (l:Lot)
    ON (l.status)
    """,
    """
    CREATE INDEX tender_type_idx
    IF NOT EXISTS FOR (t:Tender)
    ON (t.type)
    """,
    """
    CREATE INDEX tender_status_idx
    IF NOT EXISTS FOR (t:Tender)
    ON (t.status)
    """,
    """
    CREATE INDEX document_type_idx
    IF NOT EXISTS FOR (d:Document)
    ON (d.type)
    """,
    """
    CREATE INDEX chunk_source_idx
    IF NOT EXISTS FOR (c:Chunk)
    ON (c.source_document_id)
    """,
]

# Node labels and their expected properties
NODE_SCHEMA = {
    "Procurement": {
        "required": ["id", "number", "status", "budget"],
        "optional": ["date_created", "deadline", "description", "full_text", "created_at", "updated_at"],
    },
    "Participant": {
        "required": ["id", "name"],
        "optional": ["registration_number", "email", "phone", "contact_info", "region", "created_at"],
    },
    "Organization": {
        "required": ["id", "name"],
        "optional": ["inn", "registration_number", "region", "contact_info", "created_at"],
    },
    "Lot": {
        "required": ["id", "number"],
        "optional": ["quantity", "unit", "description", "expected_price", "min_price", "status", "created_at"],
    },
    "Tender": {
        "required": ["id", "type", "status"],
        "optional": ["start_date", "end_date", "created_at", "updated_at"],
    },
    "Document": {
        "required": ["id", "type"],
        "optional": ["content", "created_date", "file_path", "file_size", "created_at"],
    },
    "Requirement": {
        "required": ["id", "description"],
        "optional": ["is_mandatory", "category", "created_at"],
    },
    "Chunk": {
        "required": ["id", "content", "source_document_id"],
        "optional": ["chunk_type", "chunk_index", "embedding", "created_at"],
    },
}

# Relationship schema
RELATIONSHIP_SCHEMA = {
    "HAS_LOT": {
        "from": "Procurement",
        "to": "Lot",
        "properties": ["created_at"],
    },
    "ORGANIZED_BY": {
        "from": "Procurement",
        "to": "Organization",
        "properties": ["created_at"],
    },
    "INCLUDED_IN_TENDER": {
        "from": "Lot",
        "to": "Tender",
        "properties": ["created_at"],
    },
    "RECEIVED_BID_FROM": {
        "from": "Tender",
        "to": "Participant",
        "properties": ["bid_price", "bid_date", "created_at"],
    },
    "SUBMITTED_DOCUMENT": {
        "from": "Participant",
        "to": "Document",
        "properties": ["submission_date", "created_at"],
    },
    "HAS_REQUIREMENT": {
        "from": "Procurement",
        "to": "Requirement",
        "properties": ["created_at"],
    },
    "LOT_HAS_REQUIREMENT": {
        "from": "Lot",
        "to": "Requirement",
        "properties": ["created_at"],
    },
    "CONTAINS_CHUNK": {
        "from": "Document",
        "to": "Chunk",
        "properties": ["created_at"],
    },
    "REGISTERED_IN": {
        "from": "Participant",
        "to": "Organization",
        "properties": ["registration_date", "created_at"],
    },
}


def get_schema_initialization_cypher() -> list[str]:
    """Get all Cypher commands for schema initialization."""
    return NEO4J_SCHEMA_CYPHER


def validate_node_properties(node_type: str, properties: dict) -> bool:
    """Validate node properties against schema."""
    if node_type not in NODE_SCHEMA:
        raise ValueError(f"Unknown node type: {node_type}")

    schema = NODE_SCHEMA[node_type]
    required_props = schema["required"]

    for prop in required_props:
        if prop not in properties:
            raise ValueError(f"Missing required property '{prop}' for {node_type} node")

    return True


def validate_relationship_properties(
    relationship_type: str, from_node: str, to_node: str, properties: dict
) -> bool:
    """Validate relationship properties against schema."""
    if relationship_type not in RELATIONSHIP_SCHEMA:
        raise ValueError(f"Unknown relationship type: {relationship_type}")

    schema = RELATIONSHIP_SCHEMA[relationship_type]
    if schema["from"] != from_node or schema["to"] != to_node:
        raise ValueError(
            f"Invalid relationship direction: {from_node}-[{relationship_type}]->{to_node}. "
            f"Expected: {schema['from']}-[{relationship_type}]->{schema['to']}"
        )

    return True
