import ctypes
import unittest
from unittest.mock import Mock, call, patch

from logic.anti_afk import perform_cycle, run_session
from logic.settings import Settings
from logic.windows_backend import AutomationError, INPUT


class CycleTests(unittest.TestCase):
    def setUp(self):
        self.backend = Mock()
        self.backend.find_roblox.return_value = 200
        self.backend.foreground.return_value = 100
        self.backend.minimized.return_value = False
        self.backend.exists.return_value = True
        self.backend.jump.return_value = True
        self.stop = Mock()
        self.stop.is_set.return_value = False
        self.stop.wait.return_value = False

    def test_switch_jump_and_return(self):
        result = perform_cycle(self.backend, True, self.stop)
        self.assertEqual(result, "Space sent to Roblox")
        self.assertEqual(self.backend.activate.call_args_list, [call(200), call(100)])
        self.backend.jump.assert_called_once_with(200, self.stop)
        calls = self.backend.mock_calls
        self.assertLess(calls.index(call.activate(200)), calls.index(call.jump(200, self.stop)))
        self.assertLess(calls.index(call.jump(200, self.stop)), calls.index(call.activate(100)))

    def test_failure_still_restores_previous_window(self):
        self.backend.jump.side_effect = AutomationError("Input blocked")
        with self.assertRaisesRegex(AutomationError, "Input blocked"):
            perform_cycle(self.backend, True, self.stop)
        self.assertEqual(self.backend.activate.call_args_list, [call(200), call(100)])

    def test_activation_failure_does_not_send_space(self):
        self.backend.activate.side_effect = [AutomationError("Focus blocked"), None]
        with self.assertRaisesRegex(AutomationError, "Focus blocked"):
            perform_cycle(self.backend, True, self.stop)
        self.backend.jump.assert_not_called()
        self.assertEqual(self.backend.activate.call_args_list, [call(200), call(100)])

    def test_cancel_after_switch_restores_without_jump(self):
        self.stop.wait.return_value = True
        self.assertEqual(perform_cycle(self.backend, True, self.stop), "Cancelled")
        self.backend.jump.assert_not_called()
        self.assertEqual(self.backend.activate.call_args_list, [call(200), call(100)])

    def test_minimized_roblox_is_minimized_again(self):
        self.backend.minimized.return_value = True
        perform_cycle(self.backend, True, self.stop)
        self.backend.minimize.assert_called_once_with(200)

    def test_switching_disabled_skips_background_roblox(self):
        self.assertIn("Skipped", perform_cycle(self.backend, False, self.stop))
        self.backend.activate.assert_not_called()
        self.backend.jump.assert_not_called()

    def test_foreground_roblox_does_not_switch_windows(self):
        self.backend.foreground.return_value = 200
        perform_cycle(self.backend, False, self.stop)
        self.backend.activate.assert_not_called()
        self.backend.jump.assert_called_once()

    def test_missing_roblox_does_not_switch_or_type(self):
        self.backend.find_roblox.side_effect = AutomationError("Not found")
        with self.assertRaises(AutomationError):
            perform_cycle(self.backend, True, self.stop)
        self.backend.activate.assert_not_called()
        self.backend.jump.assert_not_called()

    def test_closed_previous_window_is_reported(self):
        self.backend.exists.return_value = False
        self.backend.minimized.return_value = True
        with self.assertRaisesRegex(AutomationError, "previous application was closed"):
            perform_cycle(self.backend, True, self.stop)
        self.backend.minimize.assert_called_once_with(200)

    def test_cancel_before_cycle_does_nothing(self):
        self.stop.is_set.return_value = True
        self.assertEqual(perform_cycle(self.backend, True, self.stop), "Cancelled")
        self.assertEqual(self.backend.mock_calls, [])


class TimerTests(unittest.TestCase):
    @patch("logic.anti_afk.perform_cycle")
    def test_first_cycle_waits_full_interval_and_stop_cancels_wait(self, cycle):
        stop = Mock()
        stop.is_set.return_value = False
        stop.wait.return_value = True
        report = Mock()
        run_session(Mock(), Settings(2), stop, report, clock=lambda: 100)
        stop.wait.assert_called_once_with(120)
        cycle.assert_not_called()
        self.assertEqual(report.call_args_list, [call("waiting", 220), call("stopped", None)])

    @patch("logic.anti_afk.perform_cycle")
    def test_error_is_reported_and_next_interval_is_scheduled(self, cycle):
        cycle.side_effect = AutomationError("Roblox closed")
        stop = Mock()
        stop.is_set.return_value = False
        stop.wait.side_effect = [False, True]
        report = Mock()
        run_session(Mock(), Settings(1), stop, report, clock=lambda: 0)
        cycle.assert_called_once()
        self.assertEqual(stop.wait.call_args_list, [call(60), call(60)])
        report.assert_any_call("result", "Roblox closed")
        self.assertEqual(report.call_args_list[-1], call("stopped", None))

    def test_input_structure_has_native_windows_size(self):
        self.assertEqual(ctypes.sizeof(INPUT), 40 if ctypes.sizeof(ctypes.c_void_p) == 8 else 28)


if __name__ == "__main__":
    unittest.main()
