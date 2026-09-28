# Architecture Specification

## 1. Separation of Concerns: Deterministic Engine vs. AI Services

```
+-------------------------------------------------------------------------+
|                         DETERMINISTIC LAYER                             |
|                        (100% Python Logic)                              |
+-------------------------------------------------------------------------+
| - Competency Scores (Weighted evidence: self 10%, knowledge 35%,        |
|                      practical 40%, training 15%)                       |
| - Skill Gap Mathematics (gap = max(0, required - current))             |
| - Statutory Priority Ranking (gap * importance * mandatory * future_rel)|
| - Role Readiness Index (weighted percentage meeting target)             |
| - Recommendation Multi-Factor Ranking                                   |
| - Assessment Scoring (objective answer key comparison)                  |
| - Historical Audit Ledger Tracking                                      |
+-------------------------------------------------------------------------+
                                    │
                                    ▼
+-------------------------------------------------------------------------+
|                         AI & GENERATIVE LAYER                           |
|                    (Qwen3 / Gemini / OpenAI / Mock)                     |
+-------------------------------------------------------------------------+
| - Grounded Conversational Tutoring with Official Citations              |
| - Pydantic-Structured MCQ Generation from Chunks                        |
| - Two-Pass Question Validation & Distractor Review                     |
| - Natural Language Explanations of Recommendations                      |
| - Text Summarization & Semantic Keyword Tagging                         |
+-------------------------------------------------------------------------+
```

## 2. RAG Retrieval & Ingestion Pipeline

1. **Document Ingestion**:
   - Supported Formats: PDF, DOCX, PPTX, TXT.
   - Validation & Sanitization: Filename cleaning, MIME type verification, size constraints.
   - Text Extraction & Normalization: Stripping non-printable characters.
   - Semantic Chunking: Sliding window with 600-word tokens and 100-word overlap.
   - Metadata Tagging: Chapter headers, page numbers, competency classification.
2. **Vector Indexing & Embeddings**:
   - Provider Abstraction: BGE-M3 (Ollama), text-embedding-004 (Gemini), or normalized deterministic Mock Embeddings.
   - Vector Store: PostgreSQL `pgvector` with cosine distance and SQL metadata filters.
3. **Authority-Weighted Reranking**:
   - Raw cosine similarity is multiplied by the source organization's Authority Tier Weight:
     - Tier A (MoSPI, NSO, NSSTA, iGOT, UNSD): `1.25x`
     - Tier B (OECD, World Bank, IMF): `1.10x`
     - Tier C (Academic, ISI Kolkata): `0.95x`
     - Tier D (General Web): `0.70x`

## 3. iGOT Karmayogi & NSSTA Integration Adapters

- `LearningProvider` & `TrainingProvider` interfaces decouple core business logic from external API specifics.
- `MockIGOTProvider` returns realistic courses with competency codes, marked with `[DEMO/iGOT]`.
- `MockNSSTAProvider` returns realistic residential academy workshops (such as Advanced Sampling at Greater Noida campus), marked with `[DEMO/NSSTA]`.
- As official API credentials become available, `RealIGOTProvider` and `RealNSSTAProvider` can be plugged in without changing any recommendation, scoring, or frontend code.
