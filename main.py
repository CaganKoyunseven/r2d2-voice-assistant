"""
R2D2 Voice Assistant — entry point.
Wires all components together and starts the system tray application.
"""
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
    logger.info("R2D2 Assistant starting...")

    # Initialize pygame audio
    pygame.mixer.init()

    # Ensure sound file exists (generate if missing)
    ensure_sound()

    # Set up observer dispatcher
    dispatcher = CommandDispatcher()

    # Register handlers
    dispatcher.register("hey_r2", lambda e: play_r2d2())
    dispatcher.register("hey_r2", browser_handle)
    dispatcher.register("hey_r2", vscode_handle)
    dispatcher.register("exit_app", lambda e: os._exit(0))

    # Start microphone listener (background thread)
    listener = MicrophoneListener(dispatcher)
    listener.start()

    # Register Windows startup entry
    startup_manager.setup()

    # Start system tray (blocking — main thread)
    tray = TrayApp(listener)
    tray.run()

    logger.info("R2D2 Assistant stopped")


if __name__ == "__main__":
    main()
