import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from logic.settings import Settings, load_settings, save_settings


class SettingsTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.path = Path(self.directory.name) / "settings.json"

    def test_missing_file_uses_defaults(self):
        self.assertEqual(load_settings(self.path), Settings())

    def test_round_trip_and_replace(self):
        for interval in (1, 10, 20):
            with self.subTest(interval=interval):
                expected = Settings(interval, True)
                save_settings(expected, self.path)
                self.assertEqual(load_settings(self.path), expected)
                self.assertFalse(self.path.with_suffix(".json.tmp").exists())

    def test_invalid_files_are_reported(self):
        for content in ('{', '[]', 'null', '{"interval_minutes": 0}',
                        '{"interval_minutes": 21}', '{"interval_minutes": true}',
                        '{"interval_minutes": 1.5}', '{"interval_minutes": "10"}',
                        '{"switch_to_roblox": "false"}'):
            with self.subTest(content=content):
                self.path.write_text(content, encoding="utf-8")
                with self.assertRaises(ValueError):
                    load_settings(self.path)

    def test_missing_fields_use_defaults(self):
        self.path.write_text('{}', encoding="utf-8")
        self.assertEqual(load_settings(self.path), Settings())

    def test_failed_replacement_preserves_previous_file(self):
        save_settings(Settings(5), self.path)
        with patch.object(Path, "replace", side_effect=PermissionError("Access denied")):
            with self.assertRaises(PermissionError):
                save_settings(Settings(20, True), self.path)
        self.assertEqual(load_settings(self.path), Settings(5))
        self.assertFalse(self.path.with_suffix(".json.tmp").exists())


if __name__ == "__main__":
    unittest.main()
