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
