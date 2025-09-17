from __future__ import annotations
import asyncio
import logging
import discord
from discord.ext import commands

from config import settings

# LM: Bot entrypoint configuring intents & dynamically loading feature extensions.
# TODO Next Steps: Add structured logging (structlog) and correlation IDs.
# ? Consideration: Provide CLI args to override feature flags at runtime.

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(name)s %(message)s')
logger = logging.getLogger("bot")

INTENTS = discord.Intents.none()
INTENTS.guilds = True
INTENTS.messages = True  # Important: Enabled preemptively for future contextual features.


class Bot(commands.Bot):
    # LM: Minimal subclass to hook extension loading & lifecycle logging.
    def __init__(self):
        super().__init__(command_prefix="!", intents=INTENTS)

    async def setup_hook(self):
        # Important: Conditional extension load based on feature flags => keeps runtime lean.
        if settings.enable_pdf_qa:
            await self.load_extension("knowledge_cog")
        logger.info("Extensions loaded. PDF_QA=%s", settings.enable_pdf_qa)

    async def on_ready(self):
        logger.info("Logged in as %s (ID: %s)", self.user, self.user.id if self.user else "?")


def main():
    # LM: Entrypoint wrapper for potential future async setup tasks.
    bot = Bot()
    bot.run(settings.discord_bot_token)


if __name__ == "__main__":
    main()
