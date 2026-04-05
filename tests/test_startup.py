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
        startup_manager.unregister()  # must not raise


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
