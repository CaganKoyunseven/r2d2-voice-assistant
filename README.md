# R2D2 Voice Assistant

> **For entertainment purposes only.** This is a fun personal project inspired by Star Wars. Not affiliated with Disney, Lucasfilm, or any official Star Wars product.

A Windows desktop assistant that wakes up when you say **"Hey R2"** and launches your favorite tools — just like having your own little droid.

## What it does

Say **"Hey R2"** and it will:
1. Play an R2D2 sound effect
2. Open a Star Wars theme on YouTube
3. Open Google Gemini
4. Open Claude
5. Launch VSCode with your last workspace

Say **"exit"** or **"quit"** to shut it down by voice.

It lives quietly in the system tray and listens in the background.

## Requirements

- Windows 10 / 11
- Python 3.8+
- Microphone
- Internet connection (for speech recognition)

## Installation

**1. Install PyAudio (Windows)**
```bash
pip install pyaudio
```
If that fails:
```bash
pip install pipwin && pipwin install pyaudio
```

**2. Install all dependencies**
```bash
pip install -r requirements.txt
```

**3. Run**
```bash
python main.py
```

On first launch the R2D2 sound is generated automatically in `sounds/`.

## Voice commands

| Say | Action |
|---|---|
| "Hey R2" | Plays sound, opens YouTube / Gemini / Claude, launches VSCode |
| "exit" / "quit" | Shuts down the assistant |

## Configuration

Edit `config.py` to customise behaviour:

| Setting | Description | Default |
|---|---|---|
| `TRIGGER_PHRASES` | Phrases that activate the assistant | `["hey r2", "r2", ...]` |
| `EXIT_PHRASES` | Phrases that shut it down | `["exit", "quit", "kapat"]` |
| `BROWSER` | Browser to use (`None` = system default) | `None` |
| `STARTUP_ENABLED` | Launch on Windows startup | `False` |
| `URLS` | URLs to open on trigger | YouTube, Gemini, Claude |

## Tests

```bash
pytest tests/ -v
```

## Disclaimer

This project is purely for fun. R2D2 is a trademark of Lucasfilm Ltd. The synthesized sound effect is generated programmatically and is not sampled from any official source.
