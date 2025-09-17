# 🧠 Agents Guide – Discord Bot Development

This document defines standards for building, extending, and operating Discord bot "agents" in this repository. Treat it as an engineering playbook: concise, prescriptive, and adaptable to multiple feature domains (commands, automation, audio, moderation, AI augmentation, etc.).

---

## 🌟 Core Objectives
 
1. Reliability first (predictable behavior, graceful failure)
2. Clarity over cleverness (explicit flows, typed where possible)
3. Least privilege (scopes, intents, and secrets minimized)
4. Observability built-in (structured logs + metrics hooks)
5. Extensibility through modular components (commands, cogs, services)
6. Offline-friendly where feasible (cache + optional external APIs)
7. Deterministic local dev parity with production

---

## 🧱 Recommended Tech Stack
 
| Concern | Preferred Tooling | Notes |
|---------|-------------------|-------|
| Discord API | `discord.py` (2.x) | Use Intents; enable only what is needed |
| Task scheduling | `apscheduler` or asyncio tasks | Avoid blocking loops |
| Persistence | Lightweight: SQLite / JSON; Scaled: Postgres | Abstract via a repository pattern |
| Config & Secrets | `.env` + `pydantic` settings | Never commit secrets |
| Audio (optional) | `ffmpeg`, opus libs | Lazy-load only if audio features enabled |
| Transcription (optional) | Local Whisper, Vosk, or external API wrapper | Feature-flag external services |
| Testing | `pytest` + `pytest-asyncio` | Fast unit tests + thin integration harness |
| Lint/Format | `ruff` + `black` + `mypy` | CI gate |
| Packaging | `uv` or `pip` | Pin versions in `requirements.txt` or `pyproject.toml` |
| Logging | `structlog` or stdlib w/ JSON formatter | Correlate by request/interaction ID |

---

## 🏗️ High-Level Architecture
 
Layers:

1. Entry / Runner (`bot.py`) – loads config, initializes logging, registers cogs.
2. Cogs (feature modules) – command groups, event listeners, background tasks.
3. Services – stateless logic (e.g., transcription service, moderation rules, formatting).
4. Adapters / Gateways – persistence, external APIs, audio capture.
5. Domain Models – typed dataclasses / pydantic models for durable data.
6. Utilities – shared helpers (time, parsing, caching).

Design Principles:
 
* Keep Discord objects at boundaries; transform into internal models early.
* Fail fast inside a cog, but never crash the process – catch, log, notify (if critical).
* Provide idempotent operations (e.g., starting a recorder twice is a no-op).
* Use dependency injection (simple constructor injection) for service wiring.

---

## 🧩 Command & Event Design
 
Guidelines:

* Prefer slash commands (`app_commands`) for discoverability.
* Keep command handlers < 60 logical lines – extract service logic.
* Use ephemeral responses for noisy control actions; public messages for results.
* Validate arguments early; return concise, action-oriented error messages.
* Rate-limit sensitive commands (cooldowns or custom guard decorator).
* Provide a `!help`/`/help` that enumerates enabled feature flags.

Common Command Categories:
 
* System: `/ping`, `/status`, `/reload` (controlled role only)
* Moderation: `/purge`, `/mute`, `/warn`
* Utility: `/roll`, `/remind`, `/quote`
* Audio (optional): `/record start|stop|status` (per-channel)
* AI / Content (optional): `/summarize`, `/transcribe`, `/analyze-log`

Event Handling Checklist:
 
* on_ready – log shard + guild counts
* on_error – structured capture
* on_guild_join / remove – persist membership state
* on_message – only if necessary (prefer intents minimized)
* background tasks – use `bot.loop.create_task` or cog `asyncio.TaskGroup`

---

## 🎙️ Optional Audio & Transcription Module
 
If implementing audio capture:

* Gate behind a feature flag: `ENABLE_AUDIO=1`.
* Join voice only on explicit command.
* Record per-user streams to `data/audio/<username>_<UTCISO>.wav`.
* Use `ffmpeg` piping; ensure sample rate normalization (e.g., 16kHz for speech models).
* Post-process asynchronously (queue of file jobs) – never block voice receive.
* Store transcription outputs in `data/transcripts/<session_id>.md` formatted as:
  `Username: "Utterance"` (optionally `[HH:MM:SS] Username: ...`).
* Provide a summarization command that can ingest multiple transcript files.

Fallback / Privacy:
 
* If username missing, use stable hash of user ID.
* Offer opt-out flag per user (respect a persisted deny-list).

---

## 💾 Persistence Strategy
 
Start simple: a lightweight repository interface.

```python
class SessionRepository(Protocol):
    async def create(self, session: Session) -> None: ...
    async def get(self, id: str) -> Session | None: ...
```

Swap adapters (in-memory -> SQLite -> Postgres) without changing cogs.

Data Directories (git-ignored):
 
* `data/audio/`
* `data/transcripts/`
* `data/cache/`
* `logs/`

---

## 📦 Configuration & Secrets
 
* Use `.env` (development) and environment variables (deployment).
* Never hardcode token; variable name: `DISCORD_BOT_TOKEN`.
* Centralize config in `config.py` (pydantic BaseSettings recommended).
* Provide feature flags: `ENABLE_AUDIO`, `ENABLE_TRANSCRIPTION`, `ENABLE_AI`.
* Validate required settings at startup and exit with clear log if missing.

---

## 🪵 Logging & Observability
 
Minimum fields: timestamp, level, event, correlation_id (interaction / message ID), guild_id, user_id (when available).

Levels:

* DEBUG – developer diagnostics
* INFO – lifecycle events (startup, shutdown, command executed)
* WARNING – recoverable issues (rate limits, transient fails)
* ERROR – unexpected exceptions
* CRITICAL – requires human intervention

Optional enhancements:
 
* Metrics: counts of commands, errors, audio minutes processed.
* Health command `/status` returns uptime, guild count, queue depths.

---

## 🧪 Testing Strategy
 
Pyramid:

1. Unit (services, formatters)
2. Integration (cog + fake Discord objects)
3. System (minimal live test with sandbox guild – optional)

Patterns:
 
* Use dependency injection so services can be mocked.
* Freeze time (e.g., `freezegun`) for timestamped artifacts.
* Provide fixtures for temporary data directories.
* Avoid network in unit tests (patch external clients).

---

## � Deployment & Operations
 
Environments: `local`, `staging`, `prod`.
Checklist:

* Pin dependencies.
* Run lint + type + tests in CI.
* Fail build on ANY secret committed (secret scanning pre-commit hook optional).
* Provide a container image (multi-stage: builder -> runtime slim) if deploying to container platform.
* Graceful shutdown: cancel background tasks, flush queues.

Rollouts:
 
* Use staged rollout by limiting guild allow-list initially.
* Log version/hash at startup.

---

## 🔐 Security & Privacy
 
* Principle of least intents – disable message content unless required.
* Sanitize user-generated content before logging.
* Respect user opt-out for recording or analytics.
* Rotate tokens if exposed (immediate revoke + regenerate).
* Avoid storing raw audio long-term unless necessary; provide retention policy (e.g., auto-delete after 30 days).

---

## 🤝 Contribution Workflow
 
1. Branch: `feature/<short-slug>`
2. Add/update tests for changes.
3. Run: format, lint, type-check, tests.
4. Open PR with: purpose, screenshots/log samples, migration notes.
5. Reviewer checks: scope, security, performance, observability additions.
6. Squash merge; tag release if user-facing commands changed.

Pre-Commit (recommended hooks):
 
* `ruff --fix` / `black` / `mypy`
* `pytest -q`
* Secret scanner (e.g., `detect-secrets`)

---

## ✅ Agent Feature Checklist (Per New Module)
 
| Item | Status |
|------|--------|
| Clear user command(s) defined | ☐ |
| Error handling path decided | ☐ |
| Logging fields added | ☐ |
| Config / flags documented | ☐ |
| Tests (unit + integration) | ☐ |
| Permissions / intents validated | ☐ |
| Persistence (if needed) abstracted | ☐ |
| Rate limiting / cooldown | ☐ |
| Docs updated (`README.md`) | ☐ |
| Cleanup on shutdown | ☐ |

---

## 🔮 Extension Ideas (Optional Modules)
 
* Structured session logging (RPG / meeting summaries)
* Auto-moderation (keyword patterns, toxicity scoring)
* Voice channel analytics (peak concurrency, talk time distribution)
* AI-assisted summarization of channel history
* Reminder / scheduling assistant with natural language parsing
* Knowledge base Q&A backed by vector store (opt-in)

---

## ❓ When to Ask for Clarification
 
* Introduces irreversible data mutation.
* Requires new external API / paid service.
* Impacts privacy (new data collected/stored).
* Adds persistent background task consuming noticeable resources.
* Alters command naming conventions.

---

## 📄 Formatting Conventions
 
* Use fenced code blocks for multi-line examples.
* Document slash commands with: Name, Args, Permissions, Short description.
* Keep line width ~100 chars for readability.
* Favor present tense: "Creates session" vs "Will create".

---

## 🏁 Quick Start (Example)
 
1. Create `.env` with `DISCORD_BOT_TOKEN=...`
2. Install dependencies.
3. Run `python bot.py` (ensuring intents configured).
4. Invoke `/ping` to verify responsiveness.
5. Enable additional feature flags incrementally.

---

This guide is living documentation—update it when patterns evolve. Keep it concise; remove obsolete sections rather than appending noise.
