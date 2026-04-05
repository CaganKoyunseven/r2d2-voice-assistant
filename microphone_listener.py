"""
Microphone listener — continuously listens for the trigger phrase
and dispatches events to the CommandDispatcher when detected.
"""
import logging
import threading
from typing import Optional

import speech_recognition as sr

import config
from command_dispatcher import CommandDispatcher

logger = logging.getLogger(__name__)


class MicrophoneListener:
    def __init__(self, dispatcher: CommandDispatcher):
        self._dispatcher = dispatcher
        self._paused = False
        self._stopped = False
        self._thread: Optional[threading.Thread] = None
        self._recognizer = sr.Recognizer()

    def is_paused(self) -> bool:
        return self._paused

    def pause(self) -> None:
        self._paused = True
        logger.info("Listening paused")

    def resume(self) -> None:
        self._paused = False
        logger.info("Listening resumed")

    def stop(self) -> None:
        self._stopped = True
        logger.info("Listening stopped")

    def start(self) -> None:
        """Starts listening in a background thread."""
        self._thread = threading.Thread(target=self._listen_loop, daemon=True, name="MicListener")
        self._thread.start()
        logger.info("Microphone listener thread started")

    def _on_phrase_detected(self, phrase: str) -> None:
        """Processes detected phrase; dispatches if trigger matches and not paused."""
        if self._paused:
            return
        phrase_lower = phrase.lower()
        if any(t in phrase_lower for t in config.EXIT_PHRASES):
            logger.info("Exit command detected: '%s'", phrase)
            self._dispatcher.dispatch("exit_app")
        elif any(t in phrase_lower for t in config.TRIGGER_PHRASES):
            logger.info("Trigger detected: '%s'", phrase)
            self._dispatcher.dispatch("hey_r2")

    def _listen_loop(self) -> None:
        with sr.Microphone() as source:
            logger.info("Adjusting for ambient noise...")
            self._recognizer.adjust_for_ambient_noise(source, duration=1)
            logger.info("Ready. Listening for triggers: %s", config.TRIGGER_PHRASES)

            while not self._stopped:
                try:
                    audio = self._recognizer.listen(source, timeout=5, phrase_time_limit=3)
                    if self._paused:
                        continue
                    text = self._recognizer.recognize_google(audio, language="en-US")
                    logger.info("Heard: '%s'", text)
                    self._on_phrase_detected(text)
                except sr.WaitTimeoutError:
                    pass  # silence — continue
                except sr.UnknownValueError:
                    pass  # unintelligible — continue
                except sr.RequestError:
                    logger.error("Cannot reach Google STT — check internet connection")
                except Exception:
                    logger.exception("Unexpected error in listen loop")
