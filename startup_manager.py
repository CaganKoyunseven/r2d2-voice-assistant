"""
Startup manager — registers/unregisters the app in Windows Registry
so it launches automatically on Windows startup.
"""
import logging
import os
import sys
import winreg

import config

logger = logging.getLogger(__name__)

_RUN_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"


def register(script_path=None) -> None:  # str | None
    """Adds the app to Windows startup via Registry."""
    if script_path is None:
        script_path = os.path.abspath(sys.argv[0])

    command = f'"{sys.executable}" "{script_path}"'
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, _RUN_KEY, 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, config.APP_NAME, 0, winreg.REG_SZ, command)
        winreg.CloseKey(key)
        logger.info("Startup entry added: %s", command)
    except Exception:
        logger.exception("Failed to add startup entry")


def unregister() -> None:
    """Removes the app from Windows startup."""
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, _RUN_KEY, 0, winreg.KEY_SET_VALUE)
        winreg.DeleteValue(key, config.APP_NAME)
        winreg.CloseKey(key)
        logger.info("Startup entry removed")
    except FileNotFoundError:
        logger.debug("Startup entry not present — nothing to remove")
    except Exception:
        logger.exception("Failed to remove startup entry")


def setup() -> None:
    """Registers or unregisters based on config.STARTUP_ENABLED."""
    if config.STARTUP_ENABLED:
        register()
    else:
        unregister()
