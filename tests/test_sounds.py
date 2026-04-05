import os
import tempfile
import numpy as np
import pytest
from unittest.mock import patch, MagicMock

import config


def test_generate_r2d2_wav_creates_file():
    from r2d2_sounds import generate_r2d2_wav
    with tempfile.TemporaryDirectory() as tmpdir:
        out_path = os.path.join(tmpdir, "test.wav")
        generate_r2d2_wav(out_path)
        assert os.path.exists(out_path)
        assert os.path.getsize(out_path) > 1000  # gerçek ses verisi içermeli


def test_generate_r2d2_wav_produces_valid_audio():
    from r2d2_sounds import generate_r2d2_wav
    from scipy.io import wavfile
    with tempfile.TemporaryDirectory() as tmpdir:
        out_path = os.path.join(tmpdir, "test.wav")
        generate_r2d2_wav(out_path)
        sample_rate, data = wavfile.read(out_path)
        assert sample_rate == config.SAMPLE_RATE
        assert len(data) > 0
        assert data.max() > 0  # sessiz değil


def test_ensure_sound_generates_when_missing(tmp_path, monkeypatch):
    from r2d2_sounds import ensure_sound
    monkeypatch.setattr(config, "SOUND_FILE", str(tmp_path / "r2d2.wav"))
    monkeypatch.setattr(config, "SOUND_DIR", str(tmp_path))
    ensure_sound()
    assert os.path.exists(config.SOUND_FILE)


def test_ensure_sound_skips_when_exists(tmp_path, monkeypatch):
    from r2d2_sounds import ensure_sound, generate_r2d2_wav
    sound_path = str(tmp_path / "r2d2.wav")
    monkeypatch.setattr(config, "SOUND_FILE", sound_path)
    generate_r2d2_wav(sound_path)
    mtime_before = os.path.getmtime(sound_path)
    ensure_sound()
    assert os.path.getmtime(sound_path) == mtime_before  # yeniden üretilmemeli


def test_play_r2d2_calls_pygame(tmp_path, monkeypatch):
    from r2d2_sounds import play_r2d2, ensure_sound
    sound_path = str(tmp_path / "r2d2.wav")
    monkeypatch.setattr(config, "SOUND_FILE", sound_path)
    monkeypatch.setattr(config, "SOUND_DIR", str(tmp_path))

    mock_sound = MagicMock()
    mock_pygame = MagicMock()
    mock_pygame.mixer.Sound.return_value = mock_sound

    with patch.dict("sys.modules", {"pygame": mock_pygame, "pygame.mixer": mock_pygame.mixer}):
        ensure_sound()
        play_r2d2()

    mock_sound.play.assert_called_once()
