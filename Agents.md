# 🧠 Agent Instructions – WhisperWatch Bot

You are helping develop a Discord bot that:

* Records per-user audio from a voice channel
* Transcribes it with OpenAI Whisper (local install)
* Outputs labeled dialogue for D\&D-style session logs

## 🌟 Project Goals

* Clear voice capture by speaker
* Transcription accuracy over speed
* Simple commands (`!record`, `!stop`)
* Easy-to-read logs (optionally timestamped)
* No external APIs required (offline preferred)

## 💡 Coding Guidelines

* Use `discord.py` 2.0+ with VoiceClient and opus support
* Use `ffmpeg` to write .wav files from user streams
* Use OpenAI `whisper` locally (`whisper file.wav --model base`)
* Preserve usernames in filenames (`Elira_20250621.wav`)
* Output transcriptions in readable format:

  ```
  Tharn: “I search the bones.”
  Elira: “You do that, I'm backing up.”
  ```

## 🔍 Ask When In Doubt:

* Should transcription be timestamped or raw text?
* Should logs be posted in Discord or saved to a file?
* How should usernames be handled if anonymous?
* Should speaker identification fallback to voice IDs?

## 🧪 Test Cases

* VC with 2 users, short test audio
* No voice activity → bot should exit gracefully
* Overlapping dialogue should remain separate per user
