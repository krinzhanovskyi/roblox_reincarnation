import io
import logging
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from logic.logging_setup import configure_logging, log_uncaught_exception


class LoggingTests(unittest.TestCase):
    def setUp(self):
        self.root = logging.getLogger()
        self.previous_handlers = self.root.handlers[:]
        self.previous_level = self.root.level
        self.root.handlers.clear()
        self.directory = tempfile.TemporaryDirectory()
        self.console = io.StringIO()
        self.stderr_patch = patch("sys.stderr", self.console)
        self.stderr_patch.start()

    def tearDown(self):
        for handler in self.root.handlers[:]:
            self.root.removeHandler(handler)
            handler.close()
        self.root.handlers[:] = self.previous_handlers
        self.root.setLevel(self.previous_level)
        self.stderr_patch.stop()
        self.directory.cleanup()

    def test_utf8_file_and_exception_traceback(self):
        configure_logging(self.directory.name)
        logging.getLogger("logic.anti_afk").info("Проверка логирования")
        try:
            raise ValueError("Example failure")
        except ValueError as error:
            log_uncaught_exception(type(error), error, error.__traceback__)
        content = (Path(self.directory.name) / "app.log").read_text(encoding="utf-8")
        self.assertIn("Проверка логирования", content)
        self.assertIn("logic.anti_afk", content)
        self.assertIn("MainThread", content)
        self.assertIn("Traceback", content)
        self.assertIn("ValueError: Example failure", content)

    def test_repeated_setup_does_not_duplicate_messages(self):
        configure_logging(self.directory.name)
        configure_logging(self.directory.name)
        logging.getLogger("test").info("Only once")
        content = (Path(self.directory.name) / "app.log").read_text(encoding="utf-8")
        self.assertEqual(content.count("Only once"), 1)
        self.assertEqual(len(self.root.handlers), 2)

    def test_rotation_keeps_three_backups(self):
        with patch("logic.logging_setup.MAX_LOG_BYTES", 180):
            configure_logging(self.directory.name)
        for index in range(20):
            logging.getLogger("test").info("Message %s: %s", index, "x" * 60)
        self.assertEqual(
            {path.name for path in Path(self.directory.name).iterdir()},
            {"app.log", "app.log.1", "app.log.2", "app.log.3"},
        )
        self.assertIn("Message 19", (Path(self.directory.name) / "app.log").read_text())

    def test_unwritable_directory_falls_back_to_console(self):
        with patch("logic.logging_setup.Path.mkdir", side_effect=PermissionError("Denied")):
            configure_logging(self.directory.name)
        logging.getLogger("test").info("Application still running")
        self.assertIn("continuing with console logging only", self.console.getvalue())
        self.assertIn("Application still running", self.console.getvalue())
        self.assertFalse((Path(self.directory.name) / "app.log").exists())


if __name__ == "__main__":
    unittest.main()
