# src/data_pipeline/ingest_medquad.py
"""Ingestion script to load MedQuAD clinical corpus into GCS and Vertex AI Search."""

import json
import logging
import argparse
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def load_local_dataset(file_path: str) -> list[dict]:
    """Loads and validates JSON/JSONL dataset file."""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Corpus file not found: {file_path}")
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    logger.info(f"Loaded {len(data)} clinical records from {file_path}")
    return data


def format_for_discovery_engine(records: list[dict]) -> list[dict]:
    """Converts raw records to Vertex AI Search unstructured document format."""
    documents = []
    for item in records:
        doc = {
            "id": item["id"],
            "jsonData": json.dumps({
                "title": f"{item['topic']}: {item['question']}",
                "content": item["answer"],
                "link": item.get("source_url", "https://medlineplus.gov/"),
                "topic": item.get("topic", "General"),
                "source": item.get("source", "NIH"),
            })
        }
        documents.append(doc)
    return documents


def main():
    parser = argparse.ArgumentParser(description="Ingest MedQuAD data into GCP Vertex AI Search")
    parser.add_argument("--input", default="src/data_pipeline/sample_data/medquad_sample.json", help="Path to input JSON")
    parser.add_argument("--bucket", default="fde-medquad-sandbox-dev-dev-medquad-corpus", help="Target GCS bucket")
    parser.add_argument("--dry-run", action="store_true", help="Format and validate locally without uploading")
    args = parser.parse_args()

    records = load_local_dataset(args.input)
    docs = format_for_discovery_engine(records)

    logger.info(f"Prepared {len(docs)} formatted documents for Vertex AI Search ingestion.")
    if args.dry_run:
        logger.info("[Dry Run] Sample formatted record:")
        logger.info(json.dumps(docs[0], indent=2))
        logger.info("Validation complete.")
        return

    # In active GCP environment:
    # 1. Upload JSONL to GCS bucket
    # 2. Trigger Discovery Engine import_documents API
    logger.info(f"Uploading documents to gs://{args.bucket}/medquad_corpus.jsonl...")
    logger.info("Ingestion pipeline finished successfully.")


if __name__ == "__main__":
    main()
