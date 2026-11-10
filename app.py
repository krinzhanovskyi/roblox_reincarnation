import logging
import sys

from logic.dpi import configure_dpi
from logic.logging_setup import configure_logging, install_exception_hooks
from ui.main_window import SettingsWindow


if __name__ == "__main__":
    configure_logging()
    install_exception_hooks()
    logger = logging.getLogger(__name__)
    logger.info("Application starting")
    try:
        configure_dpi()
        if sys.platform == "win32":
            import ctypes

            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
                "ReincarnationAFK.Desktop"
            )
        SettingsWindow().mainloop()
    finally:
        logger.info("Application exiting")
