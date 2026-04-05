"""
System tray application — shows R2D2 icon in Windows tray with
pause/resume/quit menu. Blocking: must run on the main thread.
"""
import logging
import os

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
        # Fallback: simple red square if icon file missing
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
        logger.info("Quitting...")
        self._listener.stop()
        icon.stop()
        os._exit(0)

    def run(self) -> None:
        """Starts the blocking tray loop. Must be called from the main thread."""
        image = self._load_icon()
        self._icon = pystray.Icon(
            config.APP_NAME,
            image,
            config.APP_NAME,
            menu=self._build_menu(),
        )
        logger.info("System tray started")
        self._icon.run()
