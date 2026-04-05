
# R2D2 Sesli Asistan Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** "Hey R2" sesini duyunca R2D2 efekti çalan, YouTube/Gemini/Claude/VSCode açan, system tray'de yaşayan Windows masaüstü asistanı inşa etmek.

**Architecture:** Observer pattern tabanlı — `CommandDispatcher` merkezi hub görevi görür, her handler bağımsız kaydedilir ve biri hata verse diğerleri etkilenmez. `MicrophoneListener` ayrı thread'de çalışır, `pystray` ana thread'i bloklar.

**Tech Stack:** Python 3.8+, SpeechRecognition, PyAudio, pygame, pystray, Pillow, numpy, scipy, requests, winreg (stdlib)

---

## Dosya Haritası

| Dosya | Sorumluluk |
|---|---|
| `config.py` | Tüm sabitler ve ayarlar |
| `command_dispatcher.py` | Observer pattern, handler kaydı ve bildirim |
| `r2d2_sounds.py` | Ses üretimi (sentetik) ve oynatma |
| `browser_controller.py` | URL açma handler'ı |
| `vscode_launcher.py` | VSCode başlatma handler'ı |
| `microphone_listener.py` | Sürekli dinleme, "Hey R2" algılama |
| `startup_manager.py` | Windows Registry startup kaydı |
| `tray_app.py` | pystray system tray ikonu ve menüsü |
| `main.py` | Giriş noktası, tüm parçaları birleştirir |
| `assets/generate_icon.py` | Tray ikonu PNG üretir (bir kez çalıştırılır) |
| `tests/test_dispatcher.py` | CommandDispatcher testleri |
| `tests/test_sounds.py` | Ses üretim testleri |
| `tests/test_browser.py` | BrowserHandler testleri |
| `tests/test_vscode.py` | VSCodeHandler testleri |
| `tests/test_startup.py` | StartupManager testleri |
| `tests/test_listener.py` | MicrophoneListener pause/resume testleri |

---

## Task 1: Proje İskeleti

**Files:**
- Create: `requirements.txt`
- Create: `config.py`
- Create: `sounds/.gitkeep`
- Create: `assets/.gitkeep`
- Create: `logs/.gitkeep`
- Create: `tests/__init__.py`

- [ ] **Step 1: Dizin yapısını oluştur**

```bash
cd <proje-dizini>
mkdir -p sounds assets logs tests
touch sounds/.gitkeep assets/.gitkeep logs/.gitkeep tests/__init__.py
```

- [ ] **Step 2: `requirements.txt` yaz**

```
SpeechRecognition==3.10.0
pyaudio==0.2.14
pygame==2.5.2
pystray==0.19.5
Pillow==10.3.0
numpy==1.26.4
scipy==1.13.0
requests==2.31.0
pytest==8.1.1
```

- [ ] **Step 3: `config.py` yaz**

```python
import os

TRIGGER_PHRASE = "hey r2"

# None = sistem varsayılanı. "chrome", "firefox", "edge" yazılabilir.
BROWSER = None

SOUND_DIR = os.path.join(os.path.dirname(__file__), "sounds")
SOUND_FILE = os.path.join(SOUND_DIR, "r2d2.wav")

ASSETS_DIR = os.path.join(os.path.dirname(__file__), "assets")
ICON_FILE = os.path.join(ASSETS_DIR, "r2d2_icon.png")

LOG_FILE = os.path.join(os.path.dirname(__file__), "logs", "r2d2.log")

STARTUP_ENABLED = True
APP_NAME = "R2D2Assistant"

URLS = {
    "youtube": "https://www.youtube.com/results?search_query=Star+Wars+Theme",
    "gemini": "https://gemini.google.com",
    "claude": "https://claude.ai",
}

SAMPLE_RATE = 44100
```

- [ ] **Step 4: Bağımlılıkları kur**

```bash
pip install pipwin
pipwin install pyaudio
pip install -r requirements.txt
```

Beklenen: Tüm paketler hatasız kurulur. PyAudio kurulumu için `pipwin` kullanmak Windows'ta zorunludur.

- [ ] **Step 5: Commit**

```bash
git init
git add requirements.txt config.py sounds/.gitkeep assets/.gitkeep logs/.gitkeep tests/__init__.py
git commit -m "feat: project scaffold and config"
```

---

## Task 2: CommandDispatcher (Observer Pattern)

**Files:**
- Create: `command_dispatcher.py`
- Create: `tests/test_dispatcher.py`

- [ ] **Step 1: Failing testi yaz**

`tests/test_dispatcher.py`:
```python
from command_dispatcher import CommandDispatcher


def test_registered_handler_is_called_on_dispatch():
    dispatcher = CommandDispatcher()
    called_with = []

    def handler(event):
        called_with.append(event)

    dispatcher.register("hey_r2", handler)
    dispatcher.dispatch("hey_r2")

    assert called_with == ["hey_r2"]


def test_multiple_handlers_all_called():
    dispatcher = CommandDispatcher()
    results = []

    dispatcher.register("hey_r2", lambda e: results.append("a"))
    dispatcher.register("hey_r2", lambda e: results.append("b"))
    dispatcher.dispatch("hey_r2")

    assert sorted(results) == ["a", "b"]


def test_failing_handler_does_not_stop_others():
    dispatcher = CommandDispatcher()
    results = []

    def bad_handler(event):
        raise RuntimeError("boom")

    dispatcher.register("hey_r2", bad_handler)
    dispatcher.register("hey_r2", lambda e: results.append("ok"))
    dispatcher.dispatch("hey_r2")

    assert results == ["ok"]


def test_unknown_event_does_not_raise():
    dispatcher = CommandDispatcher()
    dispatcher.dispatch("unknown_event")  # hata fırlatmamalı


def test_no_handlers_for_event_does_not_raise():
    dispatcher = CommandDispatcher()
    dispatcher.register("other_event", lambda e: None)
    dispatcher.dispatch("hey_r2")  # hata fırlatmamalı
```

- [ ] **Step 2: Testi çalıştır, FAIL olduğunu doğrula**

```bash
pytest tests/test_dispatcher.py -v
```

Beklenen: `ImportError: No module named 'command_dispatcher'`

- [ ] **Step 3: `command_dispatcher.py` yaz**

```python
import logging
from collections import defaultdict
from typing import Callable, Dict, List

logger = logging.getLogger(__name__)


class CommandDispatcher:
    def __init__(self):
        self._handlers: Dict[str, List[Callable]] = defaultdict(list)

    def register(self, event: str, handler: Callable) -> None:
        self._handlers[event].append(handler)
        logger.debug("Handler registered for event '%s': %s", event, handler.__name__ if hasattr(handler, '__name__') else handler)

    def dispatch(self, event: str) -> None:
        handlers = self._handlers.get(event, [])
        logger.info("Dispatching event '%s' to %d handler(s)", event, len(handlers))
        for handler in handlers:
            try:
                handler(event)
            except Exception:
                logger.exception("Handler '%s' failed for event '%s'", handler, event)
```

- [ ] **Step 4: Testleri çalıştır, PASS olduğunu doğrula**

```bash
pytest tests/test_dispatcher.py -v
```

Beklenen: 5 test PASS

- [ ] **Step 5: Commit**

```bash
git add command_dispatcher.py tests/test_dispatcher.py
git commit -m "feat: add CommandDispatcher with observer pattern"
```

---

## Task 3: R2D2 Ses Üretimi ve Oynatma

**Files:**
- Create: `r2d2_sounds.py`
- Create: `tests/test_sounds.py`

- [ ] **Step 1: Failing testi yaz**

`tests/test_sounds.py`:
```python
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
```

- [ ] **Step 2: Testi çalıştır, FAIL olduğunu doğrula**

```bash
pytest tests/test_sounds.py -v
```

Beklenen: `ImportError: No module named 'r2d2_sounds'`

- [ ] **Step 3: `r2d2_sounds.py` yaz**

```python
import logging
import os
import time

import numpy as np
from scipy.io import wavfile

import config

logger = logging.getLogger(__name__)


def generate_r2d2_wav(output_path: str) -> None:
    """Sentetik R2D2 chirp sesi üretir ve WAV olarak kaydeder."""
    sr = config.SAMPLE_RATE
    segments = []

    def chirp(duration: float, f_start: float, f_end: float, amplitude: float = 0.6):
        t = np.linspace(0, duration, int(duration * sr), endpoint=False)
        phase = 2 * np.pi * (f_start * t + (f_end - f_start) / (2 * duration) * t ** 2)
        return (amplitude * np.sin(phase)).astype(np.float32)

    def silence(duration: float):
        return np.zeros(int(duration * sr), dtype=np.float32)

    # R2D2 karakteristik chirp dizisi
    segments.append(chirp(0.12, 1000, 2800, 0.65))
    segments.append(silence(0.04))
    segments.append(chirp(0.08, 2500, 900, 0.55))
    segments.append(silence(0.03))
    segments.append(chirp(0.15, 600, 3200, 0.70))
    segments.append(silence(0.05))
    segments.append(chirp(0.07, 2000, 2000, 0.50))  # kısa sabit ton
    segments.append(silence(0.03))
    segments.append(chirp(0.10, 1200, 400, 0.60))

    audio = np.concatenate(segments)
    # int16'ya dönüştür
    audio_int16 = (audio * 32767).astype(np.int16)
    wavfile.write(output_path, sr, audio_int16)
    logger.info("R2D2 ses dosyası üretildi: %s", output_path)


def ensure_sound() -> None:
    """Ses dosyası yoksa üretir."""
    if os.path.exists(config.SOUND_FILE):
        logger.debug("Ses dosyası zaten mevcut: %s", config.SOUND_FILE)
        return
    os.makedirs(config.SOUND_DIR, exist_ok=True)
    logger.info("Ses dosyası bulunamadı, sentetik ses üretiliyor...")
    generate_r2d2_wav(config.SOUND_FILE)


def play_r2d2() -> None:
    """R2D2 ses efektini çalar."""
    import pygame
    try:
        sound = pygame.mixer.Sound(config.SOUND_FILE)
        sound.play()
        logger.info("R2D2 sesi çalındı")
    except Exception:
        logger.exception("Ses çalınamadı")
```

- [ ] **Step 4: Testleri çalıştır, PASS olduğunu doğrula**

```bash
pytest tests/test_sounds.py -v
```

Beklenen: 5 test PASS

- [ ] **Step 5: Commit**

```bash
git add r2d2_sounds.py tests/test_sounds.py
git commit -m "feat: add R2D2 synthetic sound generation and playback"
```

---

## Task 4: BrowserHandler

**Files:**
- Create: `browser_controller.py`
- Create: `tests/test_browser.py`

- [ ] **Step 1: Failing testi yaz**

`tests/test_browser.py`:
```python
from unittest.mock import patch, MagicMock, call
import browser_controller
import config


def test_open_all_urls_calls_webbrowser_for_each():
    mock_browser = MagicMock()
    with patch("webbrowser.get", return_value=mock_browser):
        browser_controller.open_all_urls()

    assert mock_browser.open.call_count == len(config.URLS)


def test_open_all_urls_uses_correct_urls():
    mock_browser = MagicMock()
    opened_urls = []
    mock_browser.open.side_effect = lambda url: opened_urls.append(url)

    with patch("webbrowser.get", return_value=mock_browser):
        browser_controller.open_all_urls()

    for url in config.URLS.values():
        assert url in opened_urls


def test_handle_opens_all_urls():
    mock_browser = MagicMock()
    with patch("webbrowser.get", return_value=mock_browser):
        browser_controller.handle("hey_r2")

    assert mock_browser.open.call_count == len(config.URLS)


def test_browser_error_does_not_raise():
    mock_browser = MagicMock()
    mock_browser.open.side_effect = Exception("browser crashed")

    with patch("webbrowser.get", return_value=mock_browser):
        browser_controller.open_all_urls()  # hata fırlatmamalı
```

- [ ] **Step 2: Testi çalıştır, FAIL olduğunu doğrula**

```bash
pytest tests/test_browser.py -v
```

Beklenen: `ImportError: No module named 'browser_controller'`

- [ ] **Step 3: `browser_controller.py` yaz**

```python
import logging
import time
import webbrowser

import config

logger = logging.getLogger(__name__)

_URL_OPEN_DELAY = 0.5  # saniye — sekmeler arası yarış durumunu önler


def open_all_urls() -> None:
    """config.URLS içindeki tüm URL'leri varsayılan (veya ayarlı) browser'da açar."""
    try:
        browser = webbrowser.get(config.BROWSER)
    except webbrowser.Error:
        logger.warning("Belirtilen browser '%s' bulunamadı, varsayılan kullanılıyor", config.BROWSER)
        browser = webbrowser.get()

    for name, url in config.URLS.items():
        try:
            browser.open(url)
            logger.info("Açıldı: %s → %s", name, url)
            time.sleep(_URL_OPEN_DELAY)
        except Exception:
            logger.exception("URL açılamadı: %s", url)


def handle(event: str) -> None:
    """CommandDispatcher handler arayüzü."""
    open_all_urls()
```

- [ ] **Step 4: Testleri çalıştır, PASS olduğunu doğrula**

```bash
pytest tests/test_browser.py -v
```

Beklenen: 4 test PASS

- [ ] **Step 5: Commit**

```bash
git add browser_controller.py tests/test_browser.py
git commit -m "feat: add BrowserHandler for opening URLs on trigger"
```

---

## Task 5: VSCodeHandler

**Files:**
- Create: `vscode_launcher.py`
- Create: `tests/test_vscode.py`

- [ ] **Step 1: Failing testi yaz**

`tests/test_vscode.py`:
```python
from unittest.mock import patch, MagicMock
import vscode_launcher


def test_launch_vscode_calls_code_command():
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=0)
        vscode_launcher.launch_vscode()
    mock_run.assert_called_once_with(["code", "."], check=False)


def test_launch_vscode_handles_file_not_found():
    with patch("subprocess.run", side_effect=FileNotFoundError):
        vscode_launcher.launch_vscode()  # hata fırlatmamalı


def test_launch_vscode_handles_os_error():
    with patch("subprocess.run", side_effect=OSError("permission denied")):
        vscode_launcher.launch_vscode()  # hata fırlatmamalı


def test_handle_calls_launch():
    with patch("vscode_launcher.launch_vscode") as mock_launch:
        vscode_launcher.handle("hey_r2")
    mock_launch.assert_called_once()
```

- [ ] **Step 2: Testi çalıştır, FAIL olduğunu doğrula**

```bash
pytest tests/test_vscode.py -v
```

Beklenen: `ImportError: No module named 'vscode_launcher'`

- [ ] **Step 3: `vscode_launcher.py` yaz**

```python
import logging
import subprocess

logger = logging.getLogger(__name__)


def launch_vscode() -> None:
    """PATH'teki `code` komutuyla VSCode'u başlatır."""
    try:
        subprocess.run(["code", "."], check=False)
        logger.info("VSCode başlatıldı")
    except FileNotFoundError:
        logger.error(
            "VSCode bulunamadı. 'code' komutu PATH'te mevcut değil. "
            "VSCode kurulu ve PATH'e eklenmiş olduğundan emin olun."
        )
    except OSError:
        logger.exception("VSCode başlatılırken OS hatası oluştu")


def handle(event: str) -> None:
    """CommandDispatcher handler arayüzü."""
    launch_vscode()
```

- [ ] **Step 4: Testleri çalıştır, PASS olduğunu doğrula**

```bash
pytest tests/test_vscode.py -v
```

Beklenen: 4 test PASS

- [ ] **Step 5: Commit**

```bash
git add vscode_launcher.py tests/test_vscode.py
git commit -m "feat: add VSCodeHandler"
```

---

## Task 6: MicrophoneListener

**Files:**
- Create: `microphone_listener.py`
- Create: `tests/test_listener.py`

- [ ] **Step 1: Failing testi yaz**

`tests/test_listener.py`:
```python
import threading
from unittest.mock import patch, MagicMock
from microphone_listener import MicrophoneListener
from command_dispatcher import CommandDispatcher


def test_listener_starts_as_not_paused():
    dispatcher = CommandDispatcher()
    listener = MicrophoneListener(dispatcher)
    assert not listener.is_paused()


def test_pause_sets_paused_state():
    dispatcher = CommandDispatcher()
    listener = MicrophoneListener(dispatcher)
    listener.pause()
    assert listener.is_paused()


def test_resume_clears_paused_state():
    dispatcher = CommandDispatcher()
    listener = MicrophoneListener(dispatcher)
    listener.pause()
    listener.resume()
    assert not listener.is_paused()


def test_stop_sets_stopped():
    dispatcher = CommandDispatcher()
    listener = MicrophoneListener(dispatcher)
    listener.stop()
    assert listener._stopped


def test_trigger_detected_dispatches_event():
    dispatcher = CommandDispatcher()
    received_events = []
    dispatcher.register("hey_r2", lambda e: received_events.append(e))

    listener = MicrophoneListener(dispatcher)
    listener._on_phrase_detected("hey r2")

    assert received_events == ["hey_r2"]


def test_trigger_not_dispatched_when_paused():
    dispatcher = CommandDispatcher()
    received_events = []
    dispatcher.register("hey_r2", lambda e: received_events.append(e))

    listener = MicrophoneListener(dispatcher)
    listener.pause()
    listener._on_phrase_detected("hey r2")

    assert received_events == []


def test_non_trigger_phrase_not_dispatched():
    dispatcher = CommandDispatcher()
    received_events = []
    dispatcher.register("hey_r2", lambda e: received_events.append(e))

    listener = MicrophoneListener(dispatcher)
    listener._on_phrase_detected("hello world")

    assert received_events == []
```

- [ ] **Step 2: Testi çalıştır, FAIL olduğunu doğrula**

```bash
pytest tests/test_listener.py -v
```

Beklenen: `ImportError: No module named 'microphone_listener'`

- [ ] **Step 3: `microphone_listener.py` yaz**

```python
import logging
import threading

import speech_recognition as sr

import config
from command_dispatcher import CommandDispatcher

logger = logging.getLogger(__name__)


class MicrophoneListener:
    def __init__(self, dispatcher: CommandDispatcher):
        self._dispatcher = dispatcher
        self._paused = False
        self._stopped = False
        self._thread: "threading.Thread | None" = None
        self._recognizer = sr.Recognizer()

    def is_paused(self) -> bool:
        return self._paused

    def pause(self) -> None:
        self._paused = True
        logger.info("Dinleme duraklatıldı")

    def resume(self) -> None:
        self._paused = False
        logger.info("Dinleme devam ettiriliyor")

    def stop(self) -> None:
        self._stopped = True
        logger.info("Dinleme durduruluyor")

    def start(self) -> None:
        """Arka plan thread'inde dinlemeyi başlatır."""
        self._thread = threading.Thread(target=self._listen_loop, daemon=True, name="MicListener")
        self._thread.start()
        logger.info("Mikrofon dinleme thread'i başlatıldı")

    def _on_phrase_detected(self, phrase: str) -> None:
        """Algılanan cümleyi işler, tetikleyici ise dispatch eder."""
        if self._paused:
            return
        if config.TRIGGER_PHRASE in phrase.lower():
            logger.info("Tetikleyici algılandı: '%s'", phrase)
            self._dispatcher.dispatch("hey_r2")

    def _listen_loop(self) -> None:
        with sr.Microphone() as source:
            logger.info("Ortam gürültüsüne göre ayarlanıyor...")
            self._recognizer.adjust_for_ambient_noise(source, duration=1)
            logger.info("Dinlemeye hazır. Trigger: '%s'", config.TRIGGER_PHRASE)

            while not self._stopped:
                try:
                    audio = self._recognizer.listen(source, timeout=5, phrase_time_limit=3)
                    if self._paused:
                        continue
                    text = self._recognizer.recognize_google(audio, language="tr-TR")
                    logger.debug("Duyulan: '%s'", text)
                    self._on_phrase_detected(text)
                except sr.WaitTimeoutError:
                    pass  # normal — sessizlik, devam et
                except sr.UnknownValueError:
                    pass  # anlaşılamadı, devam et
                except sr.RequestError:
                    logger.error("Google STT servisine erişilemiyor, internet bağlantısını kontrol edin")
                except Exception:
                    logger.exception("Dinleme döngüsünde beklenmeyen hata")
```

- [ ] **Step 4: Testleri çalıştır, PASS olduğunu doğrula**

```bash
pytest tests/test_listener.py -v
```

Beklenen: 7 test PASS

- [ ] **Step 5: Commit**

```bash
git add microphone_listener.py tests/test_listener.py
git commit -m "feat: add MicrophoneListener with pause/resume and trigger detection"
```

---

## Task 7: StartupManager

**Files:**
- Create: `startup_manager.py`
- Create: `tests/test_startup.py`

- [ ] **Step 1: Failing testi yaz**

`tests/test_startup.py`:
```python
from unittest.mock import patch, MagicMock, call
import startup_manager
import config


def test_register_writes_registry_key():
    mock_key = MagicMock()
    with patch("winreg.OpenKey", return_value=mock_key), \
         patch("winreg.SetValueEx") as mock_set, \
         patch("winreg.CloseKey"):
        startup_manager.register("C:\\path\\to\\main.py")

    mock_set.assert_called_once()
    args = mock_set.call_args[0]
    assert args[1] == config.APP_NAME
    assert "main.py" in args[4]


def test_unregister_deletes_registry_key():
    mock_key = MagicMock()
    with patch("winreg.OpenKey", return_value=mock_key), \
         patch("winreg.DeleteValue") as mock_del, \
         patch("winreg.CloseKey"):
        startup_manager.unregister()

    mock_del.assert_called_once_with(mock_key, config.APP_NAME)


def test_unregister_handles_missing_key():
    with patch("winreg.OpenKey", side_effect=FileNotFoundError):
        startup_manager.unregister()  # hata fırlatmamalı


def test_setup_registers_when_enabled(monkeypatch):
    monkeypatch.setattr(config, "STARTUP_ENABLED", True)
    with patch("startup_manager.register") as mock_reg:
        startup_manager.setup()
    mock_reg.assert_called_once()


def test_setup_unregisters_when_disabled(monkeypatch):
    monkeypatch.setattr(config, "STARTUP_ENABLED", False)
    with patch("startup_manager.unregister") as mock_unreg:
        startup_manager.setup()
    mock_unreg.assert_called_once()
```

- [ ] **Step 2: Testi çalıştır, FAIL olduğunu doğrula**

```bash
pytest tests/test_startup.py -v
```

Beklenen: `ImportError: No module named 'startup_manager'`

- [ ] **Step 3: `startup_manager.py` yaz**

```python
import logging
import os
import sys
import winreg

import config

logger = logging.getLogger(__name__)

_RUN_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"


def register(script_path=None) -> None:  # str | None
    """Uygulamayı Windows startup'ına ekler."""
    if script_path is None:
        script_path = os.path.abspath(sys.argv[0])

    command = f'"{sys.executable}" "{script_path}"'
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, _RUN_KEY, 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, config.APP_NAME, 0, winreg.REG_SZ, command)
        winreg.CloseKey(key)
        logger.info("Startup kaydı eklendi: %s", command)
    except Exception:
        logger.exception("Startup kaydı eklenemedi")


def unregister() -> None:
    """Uygulamayı Windows startup'ından kaldırır."""
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, _RUN_KEY, 0, winreg.KEY_SET_VALUE)
        winreg.DeleteValue(key, config.APP_NAME)
        winreg.CloseKey(key)
        logger.info("Startup kaydı kaldırıldı")
    except FileNotFoundError:
        logger.debug("Startup kaydı zaten mevcut değil")
    except Exception:
        logger.exception("Startup kaydı kaldırılamadı")


def setup() -> None:
    """config.STARTUP_ENABLED'a göre kaydeder veya kaldırır."""
    if config.STARTUP_ENABLED:
        register()
    else:
        unregister()
```

- [ ] **Step 4: Testleri çalıştır, PASS olduğunu doğrula**

```bash
pytest tests/test_startup.py -v
```

Beklenen: 5 test PASS

- [ ] **Step 5: Commit**

```bash
git add startup_manager.py tests/test_startup.py
git commit -m "feat: add StartupManager for Windows Registry startup registration"
```

---

## Task 8: Tray İkonu Oluştur

**Files:**
- Create: `assets/generate_icon.py`

- [ ] **Step 1: `assets/generate_icon.py` yaz**

Bu script bir kez çalıştırılır ve `assets/r2d2_icon.png` üretir.

```python
"""
Çalıştır: python assets/generate_icon.py
assets/r2d2_icon.png dosyasını üretir.
"""
import os
from PIL import Image, ImageDraw

SIZE = 64
OUT_PATH = os.path.join(os.path.dirname(__file__), "r2d2_icon.png")


def generate():
    img = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Gövde (mavi-gri daire)
    draw.ellipse([4, 4, SIZE - 4, SIZE - 4], fill=(100, 140, 200, 255))

    # Kafa şeridi (koyu mavi)
    draw.rectangle([4, 4, SIZE - 4, 22], fill=(40, 80, 160, 255))

    # Göz (beyaz daire + siyah nokta)
    draw.ellipse([22, 8, 42, 20], fill=(255, 255, 255, 255))
    draw.ellipse([28, 10, 36, 18], fill=(20, 20, 20, 255))

    # Gövde detayları (yatay çizgiler)
    draw.line([12, 30, SIZE - 12, 30], fill=(200, 220, 255, 200), width=2)
    draw.line([12, 38, SIZE - 12, 38], fill=(200, 220, 255, 200), width=2)

    img.save(OUT_PATH)
    print(f"İkon üretildi: {OUT_PATH}")


if __name__ == "__main__":
    generate()
```

- [ ] **Step 2: İkonu üret**

```bash
python assets/generate_icon.py
```

Beklenen: `İkon üretildi: .../assets/r2d2_icon.png`

- [ ] **Step 3: Commit**

```bash
git add assets/generate_icon.py assets/r2d2_icon.png
git commit -m "feat: add R2D2 tray icon generator and icon asset"
```

---

## Task 9: TrayApp

**Files:**
- Create: `tray_app.py`

> Not: pystray GUI testi zordur; bu modülün manuel testi yapılır.

- [ ] **Step 1: `tray_app.py` yaz**

```python
import logging
import os
import sys

import pystray
from PIL import Image

import config
from microphone_listener import MicrophoneListener

logger = logging.getLogger(__name__)


class TrayApp:
    def __init__(self, listener: MicrophoneListener):
        self._listener = listener
        self._icon = None  # pystray.Icon | None

    def _load_icon(self) -> Image.Image:
        if os.path.exists(config.ICON_FILE):
            return Image.open(config.ICON_FILE)
        # Fallback: basit kırmızı kare
        img = Image.new("RGB", (64, 64), color=(180, 50, 50))
        return img

    def _status_text(self) -> str:
        return "Duraklatıldı" if self._listener.is_paused() else "Dinleniyor..."

    def _toggle_pause(self, icon, item) -> None:
        if self._listener.is_paused():
            self._listener.resume()
        else:
            self._listener.pause()
        self._update_menu()

    def _update_menu(self) -> None:
        if self._icon:
            self._icon.menu = self._build_menu()

    def _build_menu(self) -> pystray.Menu:
        return pystray.Menu(
            pystray.MenuItem(self._status_text(), None, enabled=False),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem(
                "Devam Et" if self._listener.is_paused() else "Duraklat",
                self._toggle_pause,
            ),
            pystray.MenuItem("Çıkış", self._quit),
        )

    def _quit(self, icon, item) -> None:
        logger.info("Çıkış yapılıyor...")
        self._listener.stop()
        icon.stop()

    def run(self) -> None:
        """Bloklayan tray döngüsünü başlatır. Ana thread'de çalıştırılmalı."""
        image = self._load_icon()
        self._icon = pystray.Icon(
            config.APP_NAME,
            image,
            config.APP_NAME,
            menu=self._build_menu(),
        )
        logger.info("System tray başlatıldı")
        self._icon.run()
```

- [ ] **Step 2: Manuel test**

```bash
python -c "
import logging
logging.basicConfig(level=logging.DEBUG)
from command_dispatcher import CommandDispatcher
from microphone_listener import MicrophoneListener
from tray_app import TrayApp
d = CommandDispatcher()
l = MicrophoneListener(d)
app = TrayApp(l)
app.run()
"
```

Beklenen: System tray'de R2D2 ikonu görünür, sağ tık menüsünde "Dinleniyor...", "Duraklat", "Çıkış" seçenekleri bulunur.

- [ ] **Step 3: Commit**

```bash
git add tray_app.py
git commit -m "feat: add TrayApp with pause/resume/quit menu"
```

---

## Task 10: Main — Tüm Parçaları Birleştir

**Files:**
- Create: `main.py`

- [ ] **Step 1: `main.py` yaz**

```python
import logging
import os
import sys

import pygame

import config
import startup_manager
from browser_controller import handle as browser_handle
from command_dispatcher import CommandDispatcher
from microphone_listener import MicrophoneListener
from r2d2_sounds import ensure_sound, play_r2d2
from tray_app import TrayApp
from vscode_launcher import handle as vscode_handle


def setup_logging() -> None:
    os.makedirs(os.path.dirname(config.LOG_FILE), exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[
            logging.FileHandler(config.LOG_FILE, encoding="utf-8"),
            logging.StreamHandler(sys.stdout),
        ],
    )


def main() -> None:
    setup_logging()
    logger = logging.getLogger(__name__)
    logger.info("R2D2 Asistan başlatılıyor...")

    # pygame ses sistemi
    pygame.mixer.init()

    # Ses dosyasını hazırla (yoksa üret)
    ensure_sound()

    # Observer dispatcher
    dispatcher = CommandDispatcher()

    # Handler'ları kaydet
    dispatcher.register("hey_r2", lambda e: play_r2d2())
    dispatcher.register("hey_r2", browser_handle)
    dispatcher.register("hey_r2", vscode_handle)

    # Mikrofon dinleyici
    listener = MicrophoneListener(dispatcher)
    listener.start()

    # Windows startup kaydı
    startup_manager.setup()

    # System tray (bloklayan)
    tray = TrayApp(listener)
    tray.run()

    logger.info("R2D2 Asistan kapatıldı")


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Tüm testleri çalıştır**

```bash
pytest tests/ -v
```

Beklenen: Tüm testler PASS

- [ ] **Step 3: Uygulamayı başlat ve uçtan uca test et**

```bash
python main.py
```

Beklenen:
- System tray'de R2D2 ikonu görünür
- `logs/r2d2.log` dosyası oluşur
- `sounds/r2d2.wav` dosyası oluşur
- "Hey R2" söylenince: ses çalar, 3 browser sekmesi açılır, VSCode başlar

- [ ] **Step 4: Commit**

```bash
git add main.py
git commit -m "feat: add main entry point, wire all components together"
```

---

## Task 11: README

**Files:**
- Create: `README.md`

- [ ] **Step 1: `README.md` yaz**

```markdown
# R2D2 Sesli Asistan

"Hey R2" diyince harekete geçen Windows masaüstü asistanı.

## Ne Yapar?

"Hey R2" sesini duyunca:
1. R2D2 ses efekti çalar
2. YouTube'da "Star Wars Theme" açar
3. Google Gemini'yi açar
4. Claude'u açar
5. VSCode'u başlatır

## Kurulum

### 1. Python 3.8+ kurulu olduğundan emin olun

### 2. PyAudio kurulumu (Windows)
```bash
pip install pipwin
pipwin install pyaudio
```

### 3. Diğer bağımlılıkları kur
```bash
pip install -r requirements.txt
```

### 4. Tray ikonunu üret (bir kez)
```bash
python assets/generate_icon.py
```

### 5. Çalıştır
```bash
python main.py
```

## Ayarlar

`config.py` dosyasından değiştirilebilir:

| Ayar | Açıklama | Varsayılan |
|---|---|---|
| `TRIGGER_PHRASE` | Tetikleyici kelime | `"hey r2"` |
| `BROWSER` | Browser seçimi (`None` = varsayılan) | `None` |
| `STARTUP_ENABLED` | Windows başlangıcında aç | `True` |
| `URLS` | Açılacak URL'ler | YouTube, Gemini, Claude |

## Testler

```bash
pytest tests/ -v
```
```

- [ ] **Step 2: Commit**

```bash
git add README.md
git commit -m "docs: add README with setup and usage instructions"
```

---

## Tüm Testler — Final Kontrol

- [ ] **Tüm test paketini çalıştır**

```bash
pytest tests/ -v --tb=short
```

Beklenen çıktı:
```
tests/test_dispatcher.py::test_registered_handler_is_called_on_dispatch PASSED
tests/test_dispatcher.py::test_multiple_handlers_all_called PASSED
tests/test_dispatcher.py::test_failing_handler_does_not_stop_others PASSED
tests/test_dispatcher.py::test_unknown_event_does_not_raise PASSED
tests/test_dispatcher.py::test_no_handlers_for_event_does_not_raise PASSED
tests/test_sounds.py::test_generate_r2d2_wav_creates_file PASSED
tests/test_sounds.py::test_generate_r2d2_wav_produces_valid_audio PASSED
tests/test_sounds.py::test_ensure_sound_generates_when_missing PASSED
tests/test_sounds.py::test_ensure_sound_skips_when_exists PASSED
tests/test_sounds.py::test_play_r2d2_calls_pygame PASSED
tests/test_browser.py::test_open_all_urls_calls_webbrowser_for_each PASSED
tests/test_browser.py::test_open_all_urls_uses_correct_urls PASSED
tests/test_browser.py::test_handle_opens_all_urls PASSED
tests/test_browser.py::test_browser_error_does_not_raise PASSED
tests/test_vscode.py::test_launch_vscode_calls_code_command PASSED
tests/test_vscode.py::test_launch_vscode_handles_file_not_found PASSED
tests/test_vscode.py::test_launch_vscode_handles_os_error PASSED
tests/test_vscode.py::test_handle_calls_launch PASSED
tests/test_listener.py::test_listener_starts_as_not_paused PASSED
tests/test_listener.py::test_pause_sets_paused_state PASSED
tests/test_listener.py::test_resume_clears_paused_state PASSED
tests/test_listener.py::test_stop_sets_stopped PASSED
tests/test_listener.py::test_trigger_detected_dispatches_event PASSED
tests/test_listener.py::test_trigger_not_dispatched_when_paused PASSED
tests/test_listener.py::test_non_trigger_phrase_not_dispatched PASSED
tests/test_startup.py::test_register_writes_registry_key PASSED
tests/test_startup.py::test_unregister_deletes_registry_key PASSED
tests/test_startup.py::test_unregister_handles_missing_key PASSED
tests/test_startup.py::test_setup_registers_when_enabled PASSED
tests/test_startup.py::test_setup_unregisters_when_disabled PASSED

30 passed in X.XXs
```
