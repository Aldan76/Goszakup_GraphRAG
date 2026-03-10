"""
Knowledge Graph schema for expert consultant bot.
Nodes and relationships for normative documents, regulations, procedures.
"""

# Additional Cypher commands for Knowledge Graph
KNOWLEDGE_GRAPH_CYPHER = [
    # Create constraints for knowledge entities
    """
    CREATE CONSTRAINT concept_id_unique
    IF NOT EXISTS FOR (c:Concept)
    REQUIRE c.id IS UNIQUE
    """,
    """
    CREATE CONSTRAINT rule_id_unique
    IF NOT EXISTS FOR (r:Rule)
    REQUIRE r.id IS UNIQUE
    """,
    """
    CREATE CONSTRAINT definition_id_unique
    IF NOT EXISTS FOR (d:Definition)
    REQUIRE d.id IS UNIQUE
    """,
    """
    CREATE CONSTRAINT procedure_id_unique
    IF NOT EXISTS FOR (p:Procedure)
    REQUIRE p.id IS UNIQUE
    """,
    # Create indexes
    """
    CREATE INDEX concept_name_idx
    IF NOT EXISTS FOR (c:Concept)
    ON (c.name)
    """,
    """
    CREATE INDEX rule_description_idx
    IF NOT EXISTS FOR (r:Rule)
    ON (r.description)
    """,
    """
    CREATE INDEX definition_term_idx
    IF NOT EXISTS FOR (d:Definition)
    ON (d.term)
    """,
    """
    CREATE INDEX procedure_name_idx
    IF NOT EXISTS FOR (p:Procedure)
    ON (p.name)
    """,
    """
    CREATE INDEX chunk_language_idx
    IF NOT EXISTS FOR (c:Chunk)
    ON (c.language)
    """,
]

# Knowledge Graph node schema
KNOWLEDGE_NODE_SCHEMA = {
    "Concept": {
        "required": ["id", "name"],
        "optional": ["description", "definition", "language", "source_document", "created_at"],
        "description": "Абстрактное понятие или термин (например, 'Электронный аукцион')",
    },
    "Rule": {
        "required": ["id", "description"],
        "optional": ["applies_to", "exceptions", "source_document", "importance", "created_at"],
        "description": "Правило или требование (например, 'При сумме свыше 10млн тенге')",
    },
    "Definition": {
        "required": ["id", "term", "meaning"],
        "optional": ["language", "source_document", "context", "created_at"],
        "description": "Определение термина на казахском языке",
    },
    "Procedure": {
        "required": ["id", "name", "description"],
        "optional": ["steps", "timeline", "required_documents", "source_document", "created_at"],
        "description": "Процедура с пошаговыми инструкциями",
    },
    "Process": {
        "required": ["id", "name"],
        "optional": ["description", "stages", "responsible", "source_document", "created_at"],
        "description": "Общий процесс (например, 'Процесс подачи заявки')",
    },
    "Requirement": {
        "required": ["id", "description"],
        "optional": ["is_mandatory", "category", "applies_to", "source_document", "created_at"],
        "description": "Требование или условие",
    },
}

# Relationships for Knowledge Graph
KNOWLEDGE_RELATIONSHIP_SCHEMA = {
    "DEFINES": {
        "from": "Definition",
        "to": "Concept",
        "properties": ["created_at"],
        "description": "Определение раскрывает концепцию",
    },
    "RELATED_TO": {
        "from": "Concept",
        "to": "Concept",
        "properties": ["relationship_type", "created_at"],
        "description": "Концепции связаны между собой",
    },
    "GOVERNED_BY": {
        "from": "Concept",
        "to": "Rule",
        "properties": ["created_at"],
        "description": "Концепция управляется правилом",
    },
    "HAS_STEP": {
        "from": "Procedure",
        "to": "Procedure",
        "properties": ["step_number", "created_at"],
        "description": "Шаги в процедуре",
    },
    "USES_CONCEPT": {
        "from": "Procedure",
        "to": "Concept",
        "properties": ["created_at"],
        "description": "Процедура использует концепцию",
    },
    "MENTIONED_IN_CHUNK": {
        "from": "Concept",
        "to": "Chunk",
        "properties": ["created_at"],
        "description": "Концепция упоминается в текстовом фрагменте",
    },
    "DEFINED_IN_CHUNK": {
        "from": "Definition",
        "to": "Chunk",
        "properties": ["created_at"],
        "description": "Определение находится в фрагменте",
    },
    "FROM_DOCUMENT": {
        "from": ["Concept", "Rule", "Definition", "Procedure"],
        "to": "Document",
        "properties": ["created_at"],
        "description": "Знание из документа",
    },
}


def get_knowledge_graph_cypher() -> list:
    """Get all Knowledge Graph Cypher commands."""
    return KNOWLEDGE_GRAPH_CYPHER


def validate_knowledge_entity(entity_type: str, properties: dict) -> bool:
    """Validate knowledge entity against schema."""
    if entity_type not in KNOWLEDGE_NODE_SCHEMA:
        raise ValueError(f"Unknown entity type: {entity_type}")

    schema = KNOWLEDGE_NODE_SCHEMA[entity_type]
    required_props = schema["required"]

    for prop in required_props:
        if prop not in properties:
            raise ValueError(f"Missing required property '{prop}' for {entity_type} entity")

    return True
