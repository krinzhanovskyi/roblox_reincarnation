import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
import sys
import threading

LOG_DIRECTORY = Path(__file__).resolve().parent.parent / "logs"
MAX_LOG_BYTES = 1024 * 1024
BACKUP_COUNT = 3


def configure_logging(log_directory=LOG_DIRECTORY):
    root = logging.getLogger()
    if any(getattr(handler, "_anti_afk_handler", False) for handler in root.handlers):
        return
    root.setLevel(logging.INFO)
    formatter = logging.Formatter(
        "%(asctime)s %(levelname)-8s [%(threadName)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    console = logging.StreamHandler()
    console.setFormatter(formatter)
    console._anti_afk_handler = True
    root.addHandler(console)
    try:
        directory = Path(log_directory)
        directory.mkdir(parents=True, exist_ok=True)
        handler = RotatingFileHandler(
            directory / "app.log", maxBytes=MAX_LOG_BYTES,
            backupCount=BACKUP_COUNT, encoding="utf-8",
        )
    except OSError:
        logging.getLogger(__name__).exception(
            "Cannot create the log file; continuing with console logging only"
        )
    else:
        handler.setFormatter(formatter)
        handler._anti_afk_handler = True
        root.addHandler(handler)


def log_uncaught_exception(exc_type, exc_value, traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, traceback)
        return
    logging.getLogger(__name__).critical(
        "Unhandled application exception", exc_info=(exc_type, exc_value, traceback)
    )


def log_thread_exception(args):
    if args.exc_type is not SystemExit:
        logging.getLogger(__name__).critical(
            "Unhandled exception in thread %s", getattr(args.thread, "name", "unknown"),
            exc_info=(args.exc_type, args.exc_value, args.exc_traceback),
        )


def install_exception_hooks():
    sys.excepthook = log_uncaught_exception
    threading.excepthook = log_thread_exception
