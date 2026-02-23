"""
Main entry point for development and testing.
"""

import logging
import sys

from config.settings import logger, settings
from graph_loader.data_pipeline import DataPipeline


def main():
    """Main function for development."""
    logger.info("Starting GraphRAG system")

    try:
        # Initialize pipeline
        pipeline = DataPipeline()

        if not pipeline.connect():
            logger.error("Failed to connect to Neo4j")
            return 1

        logger.info("Pipeline initialized successfully")

        # Process sample data if it exists
        sample_dir = settings.raw_data_dir
        if sample_dir.exists():
            file_count = pipeline.process_directory(str(sample_dir))
            logger.info(f"Processed {file_count} files")

            # Get database stats
            stats = pipeline.get_stats()
            logger.info(f"Database stats: {stats}")
        else:
            logger.warning(f"Sample data directory not found: {sample_dir}")

        pipeline.disconnect()
        logger.info("Pipeline completed successfully")
        return 0

    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
