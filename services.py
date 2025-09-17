from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Optional, Sequence
import hashlib
import json

from pypdf import PdfReader
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.utils import embedding_functions

# LM: Core ingestion & retrieval services: PDF -> text -> chunks -> embeddings (via collection default) -> vector store.
# TODO Next Steps: Introduce interface abstractions (ITextExtractor, IVectorStore) for easier swapping.
# ? Consideration: We currently rely on Chroma default embedding; for reproducibility we might switch to explicit SentenceTransformer usage.


@dataclass
class Chunk:
    # LM: Represents a single semantic chunk of text with provenance metadata.
    id: str
    source_file: str
    page: int
    session: Optional[int]
    offset: int
    text: str
    sha256: str

    def to_metadata(self) -> dict:
        return {
            "source_file": self.source_file,
            "page": self.page,
            "session": self.session,
            "offset": self.offset,
            "sha256": self.sha256,
        }


def guess_session_from_filename(name: str) -> Optional[int]:
    # LM: Extract session number from typical filename patterns.
    # ? Consideration: Might add mapping file for irregular naming.
    # Heuristic: file names like Session_04.pdf, session-7.pdf, S08_Notes.pdf
    import re
    m = re.search(r"[Ss](?:ession)?[ _-]?([0-9]{1,2})", name)
    if m:
        try:
            return int(m.group(1))
        except ValueError:
            return None
    return None


def extract_text_from_pdf(path: Path) -> List[str]:
    # LM: Returns list of page texts; blank string placeholder on extraction failure to preserve page indexing.
    reader = PdfReader(str(path))
    pages: List[str] = []
    for p in reader.pages:
        try:
            pages.append(p.extract_text() or "")
        except Exception:
            pages.append("")
    return pages


def chunk_text(pages: Sequence[str], *, max_chars: int = 1100, overlap: int = 180) -> List[tuple[int, int, str]]:
    # Important: Overlap preserves context continuity across boundaries for retrieval coherence.
    # TODO Next Steps: Consider token-based segmentation for multilingual support.
    chunks: List[tuple[int, int, str]] = []  # (page, offset, text)
    for page_index, page_text in enumerate(pages, start=1):
        txt = page_text.strip()
        if not txt:
            continue
        start = 0
        while start < len(txt):
            end = min(len(txt), start + max_chars)
            piece = txt[start:end]
            chunks.append((page_index, start, piece))
            if end == len(txt):
                break
            start = max(0, end - overlap)
    return chunks


class EmbeddingProvider:
    # LM: (Currently unused) retained for potential switch to explicit embedding pipeline.
    def __init__(self, model_name: str = "all-MiniLM-L6-v2") -> None:
        self.model = SentenceTransformer(model_name)

    def embed(self, texts: Sequence[str]) -> List[List[float]]:
        return [list(vec) for vec in self.model.encode(list(texts), show_progress_bar=False)]


class VectorStore:
    # LM: Thin wrapper around Chroma persistent collection.
    def __init__(self, persist_dir: Path, collection_name: str = "campaign") -> None:
        self.client = chromadb.PersistentClient(path=str(persist_dir))
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            embedding_function=embedding_functions.DefaultEmbeddingFunction(),
            metadata={"hnsw:space": "cosine"},
        )

    def upsert_chunks(self, chunks: Sequence[Chunk]) -> None:
        # TODO Next Steps: Skip already-present chunk IDs to reduce storage duplication.
        if not chunks:
            return
        self.collection.add(
            ids=[c.id for c in chunks],
            documents=[c.text for c in chunks],
            metadatas=[c.to_metadata() for c in chunks],
        )

    def similarity_search(self, query: str, k: int = 8) -> List[dict]:
        # LM: Returns list of hit dicts with text + metadata + distance (if available).
        res = self.collection.query(query_texts=[query], n_results=k)
        out: List[dict] = []
        for i in range(len(res["ids"][0])):
            out.append(
                {
                    "id": res["ids"][0][i],
                    "text": res["documents"][0][i],
                    "metadata": res["metadatas"][0][i],
                    "distance": res["distances"][0][i] if "distances" in res else None,
                }
            )
        return out


class KnowledgeBaseService:
    # LM: Orchestrates ingestion & query logic; business-facing API.
    def __init__(self, base_dir: Path, vector_store: VectorStore) -> None:
        self.base_dir = base_dir
        self.vector_store = vector_store

    def ingest_pdf(self, pdf_path: Path) -> int:
        # Important: Full re-chunk each ingest; no incremental diffing yet.
        # TODO Next Steps: Implement hash index to skip re-indexing unchanged chunks.
        pages = extract_text_from_pdf(pdf_path)
        session = guess_session_from_filename(pdf_path.name)
        raw_chunks = chunk_text(pages)
        chunks: List[Chunk] = []
        for idx, (page, offset, text) in enumerate(raw_chunks):
            sha = hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]
            chunk_id = f"{pdf_path.stem}_p{page}_o{offset}_{sha}"
            chunks.append(
                Chunk(
                    id=chunk_id,
                    source_file=pdf_path.name,
                    page=page,
                    session=session,
                    offset=offset,
                    text=text,
                    sha256=sha,
                )
            )
        self.vector_store.upsert_chunks(chunks)
        # Optionally persist chunk metadata
        meta_file = self.base_dir / f"{pdf_path.stem}.chunks.jsonl"
        with meta_file.open("w", encoding="utf-8") as f:
            for c in chunks:
                rec = {"id": c.id, **c.to_metadata()}
                rec["len"] = len(c.text)
                f.write(json.dumps(rec) + "\n")
        return len(chunks)

    def ask(self, query: str, k: int = 6) -> str:
        # LM: Naive retrieve-and-summarize (extractive) answer; future summarizer may condense multi-chunk context.
        hits = self.vector_store.similarity_search(query, k=k)
        if not hits:
            return "No relevant passages found."

        def summarize(text: str) -> str:
            # Simple heuristic summary: first 220 chars up to sentence end.
            snippet = text.strip().replace("\n", " ")
            if len(snippet) > 220:
                snippet = snippet[:220].rsplit(".", 1)[0] + "."
            return snippet

        lines: List[str] = []
        for h in hits:
            meta = h["metadata"]
            loc = f"{meta.get('source_file')} p{meta.get('page')}"
            if meta.get("session"):
                loc += f" (Session {meta['session']})"
            lines.append(f"- {loc}: {summarize(h['text'])}")
        answer = "Top relevant excerpts:\n" + "\n".join(lines)
        return answer

    def session_enemies(self, session: int) -> str:
        # Important: Heuristic pattern matching—results are approximate.
        # TODO Next Steps: Replace simple regex with entity extraction pass.
        # Query for potential enemy lines
        base_query = f"Session {session} enemies battle fight encountered"
        hits = self.vector_store.similarity_search(base_query, k=12)
        import re
        enemy_counts: dict[str, int] = {}
        total = 0
        pat = re.compile(r"(\b\d+\b)\s+(goblins?|orcs?|bandits?|wolves?|skeletons?|enemies?)", re.I)
        for h in hits:
            for m in pat.finditer(h["text"]):
                num = int(m.group(1))
                enemy = m.group(2).lower().rstrip("s")
                enemy_counts[enemy] = enemy_counts.get(enemy, 0) + num
                total += num
        if not enemy_counts:
            return f"No enemy data inferred for session {session}."
        breakdown = ", ".join(f"{k}: {v}" for k, v in sorted(enemy_counts.items()))
        return f"Session {session}: total {total} enemies ({breakdown})."
