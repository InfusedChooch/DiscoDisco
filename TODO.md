# Project TODO Roadmap

A structured execution guide to bring DiscoDisco's PDF Knowledge features to a robust, production-ready state. Tasks are grouped by theme; follow roughly in order of sections. Use GitHub issues or PR checklists mirroring these.

Legend Tags (aligned with `Comments.md`):
 
Important: critical path
TODO: actionable item
! Bug / Issue: fix or regression risk
? Consideration: design choice to evaluate later
LM: explanatory context

---

## 0. Prerequisites / Environment

- [ ] Important: Create `.env` with `DISCORD_BOT_TOKEN` and `ENABLE_PDF_QA=1`.
- [ ] TODO: Add `data/` and `logs/` to `.gitignore` if not already.
- [ ] TODO: Install dependencies `pip install -r requirements.txt`.
- [ ] TODO: Place at least 1 sample campaign PDF in `data/drive_raw/` (name like `Session_01.pdf`).
- [ ] ? Consideration: Decide on virtualenv vs uv vs pipx; document in README.

## 1. Core Ingestion & Retrieval MVP

- [ ] Important: Verify `/sync_pdfs` ingests and reports non-zero chunk count.
- [ ] TODO: Implement hash-based reingest skip (store per-PDF hash manifest `data/chunks/index.json`).
- [ ] TODO: Add duplicate chunk ID guard (skip if ID already exists in vector store).
- [ ] TODO: Add basic exception handling around PDF parse (log + continue).
- [ ] TODO: Implement `/kb_status` (files, chunks, last ingest timestamp, vector entries).
- [ ] ? Consideration: Add max file size limit (e.g. 10MB per PDF) to avoid memory spikes.

## 2. Session & Metadata Enrichment

- [ ] TODO: Fallback session inference by scanning first page headings if filename lacks pattern.
- [ ] TODO: Store session number explicitly in chunk metadata (already) AND maintain `sessions_index.json` mapping.
- [ ] TODO: Track ingestion timestamp per PDF for status reporting.
- [ ] ? Consideration: Add language detection per PDF for future translation pipeline.

## 3. Query Quality Improvements

- [ ] TODO: Introduce explicit embedding model pipeline (use `EmbeddingProvider`) instead of Chroma default.
- [ ] TODO: Parameterize `k` for retrieval via config or command option.
- [ ] TODO: Add optional stopwords / trivial chunk skipping (very short < 40 chars).
- [ ] ? Consideration: Introduce cross-encoder re-rank (feature flag `ENABLE_RERANK`).
- [ ] ? Consideration: Add semantic answer summarization (LLM) behind `ENABLE_SUMMARIZATION`.

## 4. Enemy / Entity Extraction

- [ ] TODO: Expand regex list: hobgoblins, cultists, zombies, ogres, trolls, undead.
- [ ] TODO: Add normalization dict for irregular plurals (e.g., "wolves" -> "wolf").
- [ ] TODO: Provide uncertainty disclaimers when counts conflict.
- [ ] ? Consideration: Abstract pattern extraction into pluggable analyzers.

## 5. Observability & Logging

- [ ] Important: Replace basic logging with `structlog` JSON logger.
- [ ] TODO: Add per-command log entries (event="command.execute", command=name, user=id, guild=id).
- [ ] TODO: Log ingestion metrics (chunks_ingested, pdf_file, duration_ms).
- [ ] TODO: Track query latency – simple timing decorator.
- [ ] TODO: Expose `/kb_status` to show aggregated metrics.
- [ ] ? Consideration: Add optional Prometheus exporter or simple metrics file.

## 6. Testing Strategy

- [ ] Important: Set up `pytest` + `pytest-asyncio` baseline.
- [ ] TODO: Unit tests `guess_session_from_filename` (varied patterns).
- [ ] TODO: Unit tests `chunk_text` (empty, small page, long page).
- [ ] TODO: Unit tests `session_enemies` with synthetic text.
- [ ] TODO: Integration test: ingest 2 PDFs → ask query returns at least one chunk reference.
- [ ] TODO: Add fixture for temporary data directories.
- [ ] ? Consideration: Mock vector store with in-memory variant for speed.

## 7. Google Drive Sync (Future Feature)

- [ ] TODO: Implement `drive_sync.py` listing folder files (id, name, modifiedTime, md5Checksum).
- [ ] TODO: Diff remote list vs local hash manifest; download changed/new.
- [ ] TODO: Rate limit + exponential backoff on Drive API errors.
- [ ] TODO: Add `/sync_drive` command wrapping sync + ingest.
- [ ] Important: Secure credentials (path or base64 in env var) – never commit raw JSON.
- [ ] ? Consideration: Add manual override to re-download a single file.

## 8. Performance & Scale

- [ ] TODO: Measure ingest time per MB (log metrics) with a benchmark PDF set.
- [ ] TODO: Implement incremental ingest (skip unchanged pages if page-level hashing added).
- [ ] TODO: Add optional chunk size auto-tuning based on average sentence length.
- [ ] ? Consideration: Evaluate FAISS or LanceDB backend for larger corpora.
- [ ] ? Consideration: Implement background ingestion queue (off main interaction thread).

## 9. Security & Privacy

- [ ] Important: Ensure `data/` is .gitignored.
- [ ] TODO: Redact obvious secrets/emails from text before chunking (regex scrub pass).
- [ ] TODO: Limit `/sync_pdfs` & `/sync_drive` to authorized role or user ID allowlist.
- [ ] TODO: Add configuration validation: fail startup if feature flag enabled but required env missing.
- [ ] ? Consideration: Add retention policy (auto delete old raw PDFs after N days if hashed & chunked).

## 10. Command UX & Safeguards

- [ ] TODO: Provide ephemeral error messages for ingestion failures with summary counts.
- [ ] TODO: Add optional `--k <n>` argument to `/ask` (bounded e.g. 1..15).
- [ ] TODO: Add `/ask raw:bool` toggle to return full snippet vs summarized.
- [ ] ? Consideration: Add pagination if answer > 1900 chars (split into multiple messages or ephemeral follow-ups).

## 11. Documentation

- [ ] Important: Update `README.md` when new command added.
- [ ] TODO: Add architecture diagram (data flow PDF → chunks → vector → query).
- [ ] TODO: Add section describing heuristic limitations of `/session_enemies`.
- [ ] TODO: Provide sample anonymized PDF(s) for test fixtures.
- [ ] ? Consideration: Add `DEVELOPING.md` with local workflows (test, lint, ingest sample).

## 12. Refactoring & Abstractions

- [ ] TODO: Define protocols: `TextExtractor`, `Chunker`, `EmbeddingBackend`, `VectorStoreBackend`.
- [ ] TODO: Move enemy counting into `analyzers/enemy_extractor.py`.
- [ ] TODO: Introduce service factory for dependency injection & easier testing.
- [ ] ? Consideration: Plugin discovery via entry points for custom analyzers.

## 13. Summarization Layer (Optional)

- [ ] TODO: Add `ENABLE_SUMMARIZATION` flag.
- [ ] TODO: Implement context assembly (token budget aware) for summarizer.
- [ ] TODO: Integrate local model or OpenAI w/ safety guard (truncate long context).
- [ ] TODO: Add `/summarize_session` command using retrieval + summarizer.
- [ ] ? Consideration: Cache summaries with invalidation on re-ingest.

## 14. Release & Deployment Readiness

- [ ] Important: Add pre-commit hooks (ruff, mypy, pytest, detect-secrets).
- [ ] TODO: Add `mypy.ini` and ensure typing coverage in services.
- [ ] TODO: Create minimal Dockerfile (multi-stage, slim runtime).
- [ ] TODO: Add CI workflow: lint → type → tests → build.
- [ ] TODO: Embed git commit hash in startup log.
- [ ] ? Consideration: Provide `/status` command including version, uptime.

---

## Quick Start Execution Order (Suggested)

1. Environment & sample PDF
2. Core ingest + `/sync_pdfs` functional
3. `/ask` basic retrieval works
4. Hash skip + status command
5. Tests (unit then integration)
6. Observability (logging & metrics)
7. Drive sync + performance optimizations
8. Summarization / advanced features

---

LM: Keep this file lean—delete completed sections as they age out to avoid clutter.
