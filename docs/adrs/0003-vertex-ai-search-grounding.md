# ADR 0003: Grounded Retrieval via Vertex AI Search (GEAP) for NIH MedQuAD

## Status
Accepted

## Context
Clinical researchers require answers strictly grounded in peer-reviewed and authoritative sources (NIH Q&A datasets) with verifiable citations back to original medical publications.

## Decision
We utilize Google Cloud Vertex AI Search (Gemini Enterprise Agent Search) backed by Google Cloud Storage:
1. Raw MedQuAD datasets are staged in versioned Cloud Storage buckets.
2. Vertex AI Search indexes the documents using semantic vector representations (`text-embedding-004`) with automatic 500-token semantic chunking and 10% overlap.
3. The ResearcherAgent queries the Data Store engine via the Discovery Engine API and maps snippet IDs to citations.

## Alternatives Considered
- **Self-Hosted ChromaDB / pgvector on Cloud SQL**: Requires manual chunking, embedding generation, index maintenance, and infrastructure operations.
- **Direct Prompt Context Ingestion (Long Context Window)**: Inefficient and cost-prohibitive for searching tens of thousands of medical articles dynamically.

## Consequences
- **Positive**: Managed scalability, sub-second vector search, built-in citation metadata, and zero infrastructure overhead.
- **Trade-offs**: Requires API enablement for Discovery Engine API and Cloud Storage bucket access.
