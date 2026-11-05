import logging
import time

from .windows_backend import AutomationError

logger = logging.getLogger(__name__)


def perform_cycle(backend, switch_to_roblox, stop):
    if stop.is_set():
        logger.info("Cycle cancelled before starting")
        return "Cancelled"
    target = backend.find_roblox()
    previous = backend.foreground()
    logger.info("Cycle started: Roblox HWND=%s, previous HWND=%s", target, previous)
    if previous != target and not switch_to_roblox:
        logger.info("Cycle skipped: Roblox is not active and switching is disabled")
        return "Skipped: Roblox is not the active window"
    if not previous:
        raise AutomationError("No active window to return to. Cycle skipped.")
    was_minimized = backend.minimized(target)
    try:
        if previous != target:
            logger.info("Switching to Roblox")
            backend.activate(target)
        if stop.wait(0.35):
            logger.info("Cycle cancelled before jump")
            return "Cancelled"
        result = "Space sent to Roblox" if backend.jump(target, stop) else "Cancelled"
        logger.info("Cycle input result: %s", result)
        return result
    finally:
        if previous != target:
            try:
                if not backend.exists(previous):
                    raise AutomationError("The previous application was closed; cannot return to it.")
                logger.info("Restoring previous window HWND=%s", previous)
                backend.activate(previous)
                logger.info("Previous window restored")
            finally:
                if was_minimized:
                    logger.info("Restoring Roblox to its minimized state")
                    backend.minimize(target)


def run_session(backend, settings, stop, report, clock=time.monotonic):
    logger.info("Session started: interval=%s minutes, switch_to_roblox=%s",
                settings.interval_minutes, settings.switch_to_roblox)
    try:
        while not stop.is_set():
            deadline = clock() + settings.interval_minutes * 60
            logger.info("Timer scheduled: next cycle in %s seconds", settings.interval_minutes * 60)
            report("waiting", deadline)
            if stop.wait(max(0, deadline - clock())):
                break
            report("working", "Switching to Roblox…")
            try:
                result = perform_cycle(backend, settings.switch_to_roblox, stop)
            except (AutomationError, OSError) as error:
                logger.exception("Anti-AFK cycle failed; retrying after the next interval")
                report("result", str(error))
            else:
                report("result", result)
    except Exception as error:
        logger.exception("Session stopped due to an unexpected error")
        report("result", f"Session stopped: {error}")
    finally:
        logger.info("Session stopped")
        report("stopped", None)
