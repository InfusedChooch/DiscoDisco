# DiscoDisco – Campaign Knowledge & PDF Q&A Bot

DiscoDisco turns your campaign PDFs (session logs, notes, lore handouts) into a searchable knowledge base directly inside Discord. Ask questions like:

> "How many enemies did we fight in session 4?"  
> "What artifact did we recover in the desert ruins?"  
> "Summarize Session 7's boss fight."  

Core focus (current phase): PDF ingestion, semantic search, and structured session queries.

---

## ✨ Features (Implemented / In Progress)

* Google Drive (planned) or local directory PDF ingestion
* Text extraction + chunking with metadata (page, session)
* Vector similarity search over chunks
* `/ask` semantic question command
* `/session_enemies` heuristic enemy count extraction
* `/sync_pdfs` to ingest new/changed PDFs
* Feature-flagged (`ENABLE_PDF_QA`)

Planned next:
 
* Google Drive API sync (folder ID polling)
* Advanced entity extraction (NPCs, locations, loot)
* Summarization mode (local model or OpenAI, flag-controlled)
* Re-ranking and better answer synthesis

---

## 🧱 Architecture Overview

Layers:
 
1. `bot.py` – startup, config, extension loading
2. `knowledge_cog.py` – Discord slash commands
3. `services.py` – PDF parsing, chunking, vector store, query logic
4. `config.py` – settings + directory preparation
5. `data/` – raw PDFs, processed text, chunk metadata, vector index

Chunk metadata includes: file name, session (heuristic), page number, offset, hash.

---

## 🗄 Directory Layout (current)

```text
DiscoDisco/
├── bot.py
├── knowledge_cog.py
├── services.py
├── config.py
├── requirements.txt
├── Agents.md
├── README.md
└── data/
    ├── drive_raw/      # Place PDFs here (until Drive sync added)
    ├── ingest/         # Reserved for extracted text (future)
    ├── chunks/         # JSONL chunk metadata
    └── vector/         # Vector database persistence
```

---

## ⚙️ Setup

Python 3.10+ recommended.

1. Create and activate a virtual environment.
2. Install deps:

```bash
pip install -r requirements.txt
```

1. Create a `.env` file:

```dotenv
DISCORD_BOT_TOKEN=your_token_here
ENABLE_PDF_QA=1
# Optional / future
# GOOGLE_DRIVE_FOLDER_ID=...
# GOOGLE_CREDENTIALS_JSON=... (path or inline JSON)
```

1. Place campaign PDFs into `data/drive_raw/`.
1. Run the bot:

```bash
python bot.py
```

1. Use `/sync_pdfs` then `/ask`.

---

## 🧪 Example Commands

| Command | Description | Notes |
|---------|-------------|-------|
| `/sync_pdfs` | Ingest all PDFs in `data/drive_raw/` | Admin usage recommended |
| `/ask question:<text>` | Ask a semantic question | Returns top relevant excerpts |
| `/session_enemies session:<n>` | Estimate enemies fought | Regex + retrieval heuristic |

---

## 🔍 How Retrieval Works (MVP)

1. Extract text per page using `pypdf`.
2. Chunk pages (1100 char window, 180 overlap).
3. Store chunks + metadata in Chroma vector store.
4. Query: similarity search (k≈6–8) → simple snippet collation.
5. (Planned) Optional summarization / answer synthesis layer.

Session inference heuristic: filenames like `Session_04.pdf`, `session-7-notes.pdf`, `S08_Recap.pdf`.

---

## 🧩 Tech Stack

* `discord.py` – bot interface
* `pypdf` – PDF text extraction
* `chromadb` – vector persistence
* `sentence-transformers` – embeddings (local model)
* `pydantic` / `python-dotenv` – settings
* `structlog` (future) – structured logging

Optional future integrations: Google Drive API, OpenAI / local LLMs, re-rankers.

---

## 🔐 Security & Privacy

* Only ingest PDFs you explicitly place in the directory (or Drive folder when enabled).
* No external API calls unless feature flags (e.g., `ENABLE_OPENAI`) are set.
* Do not commit PDFs containing secrets; `data/` should be git-ignored (add if not already).

---

## 🧭 Roadmap (Short-Term)

| Item | Status |
|------|--------|
| Local PDF ingestion | ✅ |
| Vector search baseline | ✅ |
| Session enemy heuristic | ✅ |
| Drive sync | ☐ |
| NPC / Loot extraction | ☐ |
| Summarization layer | ☐ |
| Re-ranking (cross-encoder) | ☐ |

---

## 🛠 Development Notes

* Keep Discord intents minimal; message content not required yet.
* Add tests around chunking + session inference before expanding features.
* Consider abstraction boundary for vector store to allow FAISS or other backends.

---

## 🆘 Troubleshooting

| Issue | Hint |
|-------|------|
| Slash commands not showing | Ensure bot has application.commands scope & guild sync delay (can take minutes globally) |
| No results from `/ask` | Verify PDFs processed (`/sync_pdfs` output) and content not image-only PDFs |
| Session not detected | Rename file to include `Session_XX` pattern |

---


## 📄 License

See `LICENSE`.

---

For contributor guidelines and architectural standards see `Agents.md`.
