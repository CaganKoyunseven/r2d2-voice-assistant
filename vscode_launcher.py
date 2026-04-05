"""
VSCode launcher — opens VSCode via the `code` PATH command on trigger event.
"""
import logging
import subprocess

logger = logging.getLogger(__name__)


def launch_vscode() -> None:
    """Launches VSCode using the `code` command from PATH."""
    try:
        subprocess.run("code", shell=True, check=False)
        logger.info("VSCode launched")
    except FileNotFoundError:
        logger.error(
            "VSCode not found. The 'code' command is not in PATH. "
            "Ensure VSCode is installed and added to PATH."
        )
    except OSError:
        logger.exception("OS error while launching VSCode")


def handle(event: str) -> None:
    """CommandDispatcher handler interface."""
    launch_vscode()
