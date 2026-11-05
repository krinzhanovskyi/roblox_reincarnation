import unittest
from unittest.mock import Mock, call

from logic.windows_backend import AutomationError, WindowsBackend


class KeyboardTests(unittest.TestCase):
    def setUp(self):
        self.backend = WindowsBackend.__new__(WindowsBackend)
        self.backend.user32 = Mock()
        self.backend.user32.GetAsyncKeyState.return_value = 0
        self.backend.foreground = Mock(return_value=200)
        self.backend._is_player = Mock(return_value=True)
        self.backend._key = Mock()
        self.stop = Mock()
        self.stop.is_set.return_value = False

    def test_lost_focus_sends_no_key(self):
        self.backend.foreground.return_value = 100
        with self.assertRaisesRegex(AutomationError, "lost focus"):
            self.backend.jump(200, self.stop)
        self.backend._key.assert_not_called()

    def test_space_is_released_even_if_interrupted(self):
        self.stop.wait.side_effect = RuntimeError("Interrupted")
        with self.assertRaises(RuntimeError):
            self.backend.jump(200, self.stop)
        self.assertEqual(self.backend._key.call_args_list, [
            call(0x20, scan_code=0x39), call(0x20, up=True, scan_code=0x39),
        ])

    def test_held_modifier_skips_jump(self):
        self.backend.user32.GetAsyncKeyState.return_value = -32768
        with self.assertRaisesRegex(AutomationError, "modifier"):
            self.backend.jump(200, self.stop)
        self.backend._key.assert_not_called()

    def test_single_press_and_release(self):
        self.assertTrue(self.backend.jump(200, self.stop))
        self.assertEqual(self.backend._key.call_args_list, [
            call(0x20, scan_code=0x39), call(0x20, up=True, scan_code=0x39),
        ])


if __name__ == "__main__":
    unittest.main()
