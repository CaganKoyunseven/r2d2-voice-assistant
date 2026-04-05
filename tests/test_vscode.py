from unittest.mock import patch, MagicMock
import vscode_launcher


def test_launch_vscode_calls_code_command():
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=0)
        vscode_launcher.launch_vscode()
    mock_run.assert_called_once_with(["code", "."], check=False)


def test_launch_vscode_handles_file_not_found():
    with patch("subprocess.run", side_effect=FileNotFoundError):
        vscode_launcher.launch_vscode()  # must not raise


def test_launch_vscode_handles_os_error():
    with patch("subprocess.run", side_effect=OSError("permission denied")):
        vscode_launcher.launch_vscode()  # must not raise


def test_handle_calls_launch():
    with patch("vscode_launcher.launch_vscode") as mock_launch:
        vscode_launcher.handle("hey_r2")
    mock_launch.assert_called_once()
