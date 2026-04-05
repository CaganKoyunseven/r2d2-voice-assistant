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
