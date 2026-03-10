"""
Knowledge Document Upload System
Interactive interface for uploading and managing DOCX documents in Knowledge Graph.

Usage:
    python upload_knowledge.py                  # Interactive mode
    python upload_knowledge.py <path>          # Upload specific file
    python upload_knowledge.py --list          # List uploaded documents
    python upload_knowledge.py --clear         # Clear knowledge graph
"""

import argparse
import sys
from datetime import datetime
from pathlib import Path

from config.settings import logger, settings
from graph_loader.data_pipeline import DataPipeline
from graph_loader.neo4j_connector import Neo4jConnector
from parsers.docx_parser import DOCXParser


def upload_knowledge_document(file_path: str, pipeline: DataPipeline) -> bool:
    """
    Upload and parse a knowledge document into Neo4j.

    Args:
        file_path: Path to DOCX file
        pipeline: DataPipeline instance

    Returns:
        True if successful
    """
    path = Path(file_path)

    if not path.exists():
        logger.error(f"❌ File not found: {file_path}")
        return False

    if path.suffix.lower() != ".docx":
        logger.error(f"❌ Expected .docx file, got: {path.suffix}")
        return False

    try:
        # Parse document
        logger.info(f"\n📄 Parsing document: {path.name}")
        parser = DOCXParser()
        doc = parser.parse(str(path))

        logger.info(f"✅ Parsed successfully:")
        logger.info(f"   - Entities: {len(doc.entities)}")
        logger.info(f"   - Chunks: {len(doc.chunks)}")
        logger.info(f"   - Language: {doc.metadata.get('language', 'unknown')}")

        # Load into Neo4j
        logger.info(f"\n🔄 Loading into Neo4j...")
        success = pipeline.load_document(doc)

        if success:
            logger.info(f"✅ Document loaded successfully!")

            # Get updated stats
            stats = pipeline.get_stats()
            logger.info(f"\n📊 Database statistics:")
            for label, count in stats.items():
                logger.info(f"   {label}: {count}")

            return True
        else:
            logger.error(f"❌ Failed to load document into Neo4j")
            return False

    except Exception as e:
        logger.error(f"❌ Error parsing document: {e}")
        import traceback
        traceback.print_exc()
        return False


def list_uploaded_documents(connector: Neo4jConnector) -> None:
    """List all uploaded documents in database."""
    try:
        cypher = """
        MATCH (d:Document)
        RETURN d.id as id, d.type as type, d.created_at as created_at
        ORDER BY d.created_at DESC
        """

        results = connector.query(cypher)

        if not results:
            logger.info("📭 No documents uploaded yet")
            return

        logger.info(f"\n📚 Uploaded Documents ({len(results)}):")
        logger.info("-" * 70)

        for i, doc in enumerate(results, 1):
            logger.info(f"{i}. ID: {doc.get('id', 'N/A')}")
            logger.info(f"   Type: {doc.get('type', 'N/A')}")
            logger.info(f"   Created: {doc.get('created_at', 'N/A')}")

    except Exception as e:
        logger.error(f"❌ Failed to list documents: {e}")


def show_knowledge_summary(connector: Neo4jConnector) -> None:
    """Show summary of knowledge graph."""
    try:
        cypher = """
        MATCH (n) RETURN labels(n)[0] as label, count(*) as count
        ORDER BY count DESC
        """

        results = connector.query(cypher)

        if not results:
            logger.info("📭 Knowledge graph is empty")
            return

        logger.info(f"\n📊 Knowledge Graph Summary:")
        logger.info("-" * 70)

        total = 0
        for item in results:
            label = item.get("label", "Unknown")
            count = item.get("count", 0)
            total += count
            logger.info(f"  {label:20} : {count:,}")

        logger.info("-" * 70)
        logger.info(f"  {'TOTAL':20} : {total:,}")

    except Exception as e:
        logger.error(f"❌ Failed to get summary: {e}")


def interactive_mode() -> None:
    """Interactive mode for uploading documents."""
    pipeline = DataPipeline()

    if not pipeline.connect():
        logger.error("❌ Failed to connect to Neo4j")
        return

    logger.info("\n" + "=" * 70)
    logger.info("🤖 Knowledge Document Upload System")
    logger.info("For Government Procurement Consultant Bot")
    logger.info("=" * 70)

    while True:
        logger.info("\n📋 Menu:")
        logger.info("  1. Upload DOCX document")
        logger.info("  2. List uploaded documents")
        logger.info("  3. Show knowledge summary")
        logger.info("  4. Clear knowledge graph")
        logger.info("  5. Exit")

        choice = input("\n👉 Select option (1-5): ").strip()

        if choice == "1":
            file_path = input("📄 Enter path to DOCX file: ").strip()
            if file_path:
                upload_knowledge_document(file_path, pipeline)

        elif choice == "2":
            list_uploaded_documents(pipeline.connector)

        elif choice == "3":
            show_knowledge_summary(pipeline.connector)

        elif choice == "4":
            confirm = input("⚠️  Clear all knowledge? (yes/no): ").strip().lower()
            if confirm == "yes":
                pipeline.clear_database()
                logger.info("✅ Knowledge graph cleared")

        elif choice == "5":
            logger.info("\n👋 Goodbye!")
            break

        else:
            logger.info("❌ Invalid option")

    pipeline.disconnect()


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description="Upload normative documents to knowledge graph",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python upload_knowledge.py                      # Interactive mode
  python upload_knowledge.py Zakon.docx           # Upload specific file
  python upload_knowledge.py --list               # List documents
  python upload_knowledge.py --summary            # Show stats
  python upload_knowledge.py --clear              # Clear all data
        """,
    )

    parser.add_argument("file", nargs="?", help="Path to DOCX file")
    parser.add_argument("--list", action="store_true", help="List uploaded documents")
    parser.add_argument("--summary", action="store_true", help="Show knowledge graph summary")
    parser.add_argument("--clear", action="store_true", help="Clear all knowledge")

    args = parser.parse_args()

    # Initialize pipeline
    pipeline = DataPipeline()

    if not pipeline.connect():
        logger.error("❌ Failed to connect to Neo4j")
        return 1

    try:
        if args.file:
            # Upload specific file
            success = upload_knowledge_document(args.file, pipeline)
            return 0 if success else 1

        elif args.list:
            # List documents
            list_uploaded_documents(pipeline.connector)
            return 0

        elif args.summary:
            # Show summary
            show_knowledge_summary(pipeline.connector)
            return 0

        elif args.clear:
            # Clear graph
            confirm = input("⚠️  Clear all knowledge? (yes/no): ").strip().lower()
            if confirm == "yes":
                pipeline.clear_database()
                logger.info("✅ Knowledge graph cleared")
            return 0

        else:
            # Interactive mode
            interactive_mode()
            return 0

    finally:
        pipeline.disconnect()


if __name__ == "__main__":
    sys.exit(main())
