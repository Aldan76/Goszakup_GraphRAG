"""
Script to load sample procurement data into Neo4j.

Usage:
    python load_data.py                    # Load from data/samples/
    python load_data.py <path_to_file>    # Load specific file
    python load_data.py --clear            # Clear all data
"""

import argparse
import sys
from pathlib import Path

from config.settings import logger, settings
from graph_loader.data_pipeline import DataPipeline


def load_sample_data():
    """Load sample data from data/samples directory."""
    sample_dir = Path(__file__).parent / "data" / "samples"

    if not sample_dir.exists():
        logger.error(f"Sample directory not found: {sample_dir}")
        return False

    pipeline = DataPipeline()

    if not pipeline.connect():
        logger.error("Failed to connect to Neo4j")
        return False

    logger.info(f"Loading data from {sample_dir}")

    # Process all JSON files
    file_count = pipeline.process_directory(str(sample_dir))

    if file_count > 0:
        # Print statistics
        stats = pipeline.get_stats()
        logger.info("📊 Database statistics:")
        for label, count in stats.items():
            logger.info(f"  {label}: {count}")

        logger.info(f"✅ Successfully loaded {file_count} files")
    else:
        logger.warning("⚠️ No files were loaded")

    pipeline.disconnect()
    return file_count > 0


def load_specific_file(file_path: str) -> bool:
    """Load specific file into Neo4j."""
    path = Path(file_path)

    if not path.exists():
        logger.error(f"File not found: {file_path}")
        return False

    if not path.suffix.lower() in [".json", ".xml", ".pdf"]:
        logger.error(f"Unsupported file format: {path.suffix}")
        return False

    pipeline = DataPipeline()

    if not pipeline.connect():
        logger.error("Failed to connect to Neo4j")
        return False

    logger.info(f"Loading file: {file_path}")

    success = pipeline.process_file(str(path))

    if success:
        stats = pipeline.get_stats()
        logger.info("📊 Database statistics:")
        for label, count in stats.items():
            logger.info(f"  {label}: {count}")
        logger.info("✅ File loaded successfully")
    else:
        logger.error("❌ Failed to load file")

    pipeline.disconnect()
    return success


def clear_database() -> bool:
    """Clear all data from database."""
    pipeline = DataPipeline()

    if not pipeline.connect():
        logger.error("Failed to connect to Neo4j")
        return False

    logger.warning("⚠️ Clearing all data from database...")
    success = pipeline.clear_database()

    if success:
        logger.info("✅ Database cleared")
    else:
        logger.error("❌ Failed to clear database")

    pipeline.disconnect()
    return success


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description="Load procurement data into Neo4j GraphRAG system",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python load_data.py                 # Load sample data
  python load_data.py data/my_data.json  # Load specific file
  python load_data.py --clear         # Clear all data
        """,
    )

    parser.add_argument("file", nargs="?", default=None, help="Path to data file or directory")
    parser.add_argument("--clear", action="store_true", help="Clear all data from database")

    args = parser.parse_args()

    if args.clear:
        if not clear_database():
            return 1
        return 0

    if args.file:
        if not load_specific_file(args.file):
            return 1
    else:
        if not load_sample_data():
            return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
