from unittest.mock import patch, MagicMock
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
        browser_controller.open_all_urls()  # must not raise
