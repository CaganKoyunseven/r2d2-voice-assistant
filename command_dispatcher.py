"""
Central observer-pattern dispatcher for the R2D2 assistant.

Handlers register for named events via `register()`. When `dispatch()`
is called with an event name, all registered handlers are invoked in
registration order. A failing handler is logged and skipped; it does
not prevent subsequent handlers from running.
"""

import logging
from typing import Callable, Dict, List

logger = logging.getLogger(__name__)


class CommandDispatcher:
    def __init__(self):
        self._handlers: Dict[str, List[Callable]] = {}

    def register(self, event: str, handler: Callable) -> None:
        self._handlers.setdefault(event, []).append(handler)
        logger.debug("Handler registered for event '%s': %s", event, handler.__name__ if hasattr(handler, '__name__') else handler)

    def dispatch(self, event: str) -> None:
        handlers = self._handlers.get(event, [])
        logger.info("Dispatching event '%s' to %d handler(s)", event, len(handlers))
        for handler in handlers:
            try:
                handler(event)
            except Exception:
                logger.exception("Handler '%s' failed for event '%s'", handler, event)
