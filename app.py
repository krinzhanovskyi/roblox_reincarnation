import logging

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
        SettingsWindow().mainloop()
    finally:
        logger.info("Application exiting")
