# WhisperWatch – Discord Voice Transcriber Bot

A personalized Discord bot inspired by Craig, designed to:

* Join voice channels
* Record user audio (per speaker)
* Transcribe using OpenAI Whisper
* Output logs as .txt, .md, or Discord messages

## 🚪 Current Status

Early-stage development. Focus is on:

* VC joining and per-user audio recording
* Saving .wav files for each speaker
* Running Whisper locally on the saved files

## 🛠 Planned Features

* `!record [session_name]`: Start voice capture
* `!stop`: End recording, begin transcription
* Per-user file naming for speaker labeling
* Whisper transcription with timestamped logs
* DM or role-only access control
* Export options: Discord message, Markdown, text

## 📦 Stack

* `discord.py` for bot control
* `ffmpeg` for audio stream capture
* `whisper` (OpenAI) for transcription
* Python 3.10+

## 🛠 Setup

```bash
pip install -r requirements.txt
brew install ffmpeg   # or use your OS's method
```

## 🗂 Directory Structure

```
whisperwatch/
├── main.py              # Bot entry point
├── audio/               # Stored .wav files
├── transcripts/         # Final transcripts
├── agents.md            # AI assistant instructions
└── README.md
```

## 🔐 Notes

* This bot will **not** run on public servers without user consent.
* Designed for **private D\&D games** or collaborative workspace logging.
