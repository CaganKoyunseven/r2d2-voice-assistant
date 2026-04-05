"""
R2D2 sound generation and playback.

Generates a synthetic R2D2-style chirp sound using frequency-modulated
sine waves and saves it as a WAV file. Plays back via pygame.mixer.
"""
import logging
import os

import numpy as np
from scipy.io import wavfile

import config

logger = logging.getLogger(__name__)


def generate_r2d2_wav(output_path: str) -> None:
    """Generates a synthetic R2D2 chirp sequence and saves as WAV."""
    rate = config.SAMPLE_RATE
    segments = []

    def chirp(duration: float, f_start: float, f_end: float, amplitude: float = 0.6):
        t = np.linspace(0, duration, int(duration * rate), endpoint=False)
        phase = 2 * np.pi * (f_start * t + (f_end - f_start) / (2 * duration) * t ** 2)
        return (amplitude * np.sin(phase)).astype(np.float32)

    def silence(duration: float):
        return np.zeros(int(duration * rate), dtype=np.float32)

    segments.append(chirp(0.12, 1000, 2800, 0.65))
    segments.append(silence(0.04))
    segments.append(chirp(0.08, 2500, 900, 0.55))
    segments.append(silence(0.03))
    segments.append(chirp(0.15, 600, 3200, 0.70))
    segments.append(silence(0.05))
    segments.append(chirp(0.07, 2000, 2000, 0.50))
    segments.append(silence(0.03))
    segments.append(chirp(0.10, 1200, 400, 0.60))

    audio = np.concatenate(segments)
    wavfile.write(output_path, rate, (audio * 32767).astype(np.int16))
    logger.info("R2D2 sound generated: %s", output_path)


def ensure_sound() -> None:
    """Generates the sound file if it does not already exist."""
    if os.path.exists(config.SOUND_FILE):
        return
    os.makedirs(config.SOUND_DIR, exist_ok=True)
    logger.info("Generating synthetic R2D2 sound...")
    generate_r2d2_wav(config.SOUND_FILE)


def play_r2d2() -> None:
    """Plays the R2D2 sound effect via pygame.mixer."""
    import pygame
    try:
        pygame.mixer.Sound(config.SOUND_FILE).play()
        logger.info("R2D2 sound played")
    except Exception:
        logger.exception("Failed to play sound")
