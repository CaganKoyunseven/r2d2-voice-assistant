import os
import sys

# When frozen as a PyInstaller .exe:
#   BASE_DIR   = directory containing the .exe  (writable: sounds, logs)
#   BUNDLE_DIR = _MEIPASS temp directory         (read-only: bundled assets)
if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
    BUNDLE_DIR = sys._MEIPASS
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    BUNDLE_DIR = BASE_DIR

# Voice phrases that activate the assistant
TRIGGER_PHRASES = [
    "hey r2", "r2", "are too", "artoo", "ar2", "hey are too",
    "hey auto", "hey arthur", "are 2", "r 2", "are two", "r two",
]

# Voice phrases that shut down the assistant
EXIT_PHRASES = ["exit", "quit", "kapat"]

# Browser to use — None means system default; "chrome" / "firefox" / "edge" also accepted
BROWSER = None

SOUND_DIR = os.path.join(BASE_DIR, "sounds")
SOUND_FILE = os.path.join(SOUND_DIR, "r2d2.wav")

ASSETS_DIR = os.path.join(BUNDLE_DIR, "assets")
ICON_FILE = os.path.join(ASSETS_DIR, "r2d2_icon.png")

LOG_FILE = os.path.join(BASE_DIR, "logs", "r2d2.log")

STARTUP_ENABLED = False
APP_NAME = "R2D2Assistant"

URLS = {
    "gemini": "https://gemini.google.com",
    "claude": "https://claude.ai",
    "youtube": "https://www.youtube.com/watch?v=_D0ZQPqeJkk",
}

# --- Audio ---
SAMPLE_RATE = 44100
