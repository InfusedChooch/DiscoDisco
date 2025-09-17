from __future__ import annotations
import discord
from discord import app_commands
from discord.ext import commands
from pathlib import Path
from typing import Optional

from config import settings
from services import KnowledgeBaseService, VectorStore

# LM: Knowledge cog exposes user-facing commands for ingestion & querying.
# TODO Next Steps: Add `/kb_status` command for observability (counts & last sync time).
# ? Consideration: Introduce per-guild scoping if multi-guild deployment is needed.

# Instantiate vector store & KB service (simple global for now)
_vector_store: Optional[VectorStore] = None
_kb_service: Optional[KnowledgeBaseService] = None


def get_kb() -> KnowledgeBaseService:
    # LM: Lazy singleton initialization (acceptable for current scale; revisit for DI later).
    global _kb_service, _vector_store
    if _kb_service is None:
        _vector_store = VectorStore(settings.vector_dir)
        _kb_service = KnowledgeBaseService(settings.chunk_dir, _vector_store)
    return _kb_service


class Knowledge(commands.Cog):
    # LM: Encapsulates PDF knowledge commands.
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="sync_pdfs", description="Ingest PDFs from local drive_raw directory")
    async def sync_pdfs(self, interaction: discord.Interaction):
        # Important: Full reingest each call; duplicates not de-duplicated yet.
        if not settings.enable_pdf_qa:
            await interaction.response.send_message("PDF QA feature disabled.", ephemeral=True)
            return
        # For MVP we just scan local directory (Drive sync to be implemented separately)
        drive_dir = settings.drive_raw_dir
        pdfs = list(drive_dir.glob("*.pdf"))
        if not pdfs:
            await interaction.response.send_message("No PDFs found in drive_raw directory.", ephemeral=True)
            return
        kb = get_kb()
        total_chunks = 0
        for p in pdfs:
            ingested = kb.ingest_pdf(p)
            total_chunks += ingested
        await interaction.response.send_message(f"Ingested {len(pdfs)} PDFs into {total_chunks} chunks.", ephemeral=True)

    @app_commands.command(name="ask", description="Ask a question based on campaign PDFs")
    @app_commands.describe(question="Your question about the campaign")
    async def ask(self, interaction: discord.Interaction, question: str):
        # LM: Provides retrieval-based answer (extractive summary list).
        if not settings.enable_pdf_qa:
            await interaction.response.send_message("PDF QA feature disabled.", ephemeral=True)
            return
        kb = get_kb()
        answer = kb.ask(question)
        await interaction.response.send_message(answer[:1900], ephemeral=False)

    @app_commands.command(name="session_enemies", description="Estimate enemies fought in a session")
    @app_commands.describe(session="Session number (e.g., 4)")
    async def session_enemies(self, interaction: discord.Interaction, session: int):
        # Important: Approximate heuristic (regex + retrieval) – not authoritative.
        if not settings.enable_pdf_qa:
            await interaction.response.send_message("PDF QA feature disabled.", ephemeral=True)
            return
        kb = get_kb()
        answer = kb.session_enemies(session)
        await interaction.response.send_message(answer, ephemeral=False)


async def setup(bot: commands.Bot):
    # LM: Extension entry point used by discord.py auto loader.
    await bot.add_cog(Knowledge(bot))
