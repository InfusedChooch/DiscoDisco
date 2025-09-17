from __future__ import annotations
from pydantic import BaseSettings, Field
from pathlib import Path
from typing import Optional

# LM: Centralized runtime configuration using pydantic BaseSettings.
# Important: All secrets (tokens, credentials) are loaded from environment / .env; never hardcode sensitive values.
# TODO Next Steps: Add validation to ensure at least one feature flag is enabled or warn on no-feature mode.
# ? Consideration: Might introduce a SettingsFactory for multi-environment overrides (local, staging, prod).

class Settings(BaseSettings):
    # Discord
    discord_bot_token: str = Field(..., alias="DISCORD_BOT_TOKEN")  # Important: Required to start the bot.

    # Feature flags
    enable_pdf_qa: bool = Field(default=False, alias="ENABLE_PDF_QA")  # TODO Next Steps: Document in README feature flags section.
    enable_openai: bool = Field(default=False, alias="ENABLE_OPENAI")  # TODO Next Steps: Gate LLM-based summarization when added.

    # Google Drive
    google_drive_folder_id: Optional[str] = Field(default=None, alias="GOOGLE_DRIVE_FOLDER_ID")  # TODO Next Steps: Required when Drive sync implemented.
    google_credentials_json: Optional[str] = Field(default=None, alias="GOOGLE_CREDENTIALS_JSON")  # path or inline JSON

    # Embeddings
    embeddings_provider: str = Field(default="local", alias="EMBEDDINGS_PROVIDER")  # local|openai
    embeddings_model: str = Field(default="all-MiniLM-L6-v2", alias="EMBEDDINGS_MODEL")  # ? Consideration: Expose list of allowed models.

    # Paths
    data_dir: Path = Field(default=Path("data"))  # LM: Base data directory (git-ignored).
    drive_raw_dir: Path = Field(default=Path("data/drive_raw"))  # LM: Original PDF sources.
    ingest_dir: Path = Field(default=Path("data/ingest"))  # TODO Next Steps: Future extracted text caching.
    chunk_dir: Path = Field(default=Path("data/chunks"))  # LM: Chunk metadata (JSONL).
    vector_dir: Path = Field(default=Path("data/vector"))  # LM: Persistent vector DB files.

    class Config:
        env_file = ".env"
        case_sensitive = False

# Important: Instantiating settings triggers .env load & field coercion.
settings = Settings()  # type: ignore

# LM: Ensure expected filesystem layout exists at import so later services can rely on it.
# TODO Next Steps: Add safety check to warn if directories already contain unexpected large files.
for p in [
    settings.data_dir,
    settings.drive_raw_dir,
    settings.ingest_dir,
    settings.chunk_dir,
    settings.vector_dir,
]:
    p.mkdir(parents=True, exist_ok=True)
