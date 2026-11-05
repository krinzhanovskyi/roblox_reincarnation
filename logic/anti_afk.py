import time

from .windows_backend import AutomationError


def perform_cycle(backend, switch_to_roblox, stop):
    if stop.is_set():
        return "Cancelled"
    target = backend.find_roblox()
    previous = backend.foreground()
    if previous != target and not switch_to_roblox:
        return "Skipped: Roblox is not the active window"
    if not previous:
        raise AutomationError("No active window to return to. Cycle skipped.")
    was_minimized = backend.minimized(target)
    try:
        if previous != target:
            backend.activate(target)
        if stop.wait(0.35):
            return "Cancelled"
        return "Space sent to Roblox" if backend.jump(target, stop) else "Cancelled"
    finally:
        if previous != target:
            try:
                if not backend.exists(previous):
                    raise AutomationError("The previous application was closed; cannot return to it.")
                backend.activate(previous)
            finally:
                if was_minimized:
                    backend.minimize(target)


def run_session(backend, settings, stop, report, clock=time.monotonic):
    try:
        while not stop.is_set():
            deadline = clock() + settings.interval_minutes * 60
            report("waiting", deadline)
            if stop.wait(max(0, deadline - clock())):
                break
            report("working", "Switching to Roblox…")
            try:
                result = perform_cycle(backend, settings.switch_to_roblox, stop)
            except (AutomationError, OSError) as error:
                report("result", str(error))
            else:
                report("result", result)
    except Exception as error:
        report("result", f"Session stopped: {error}")
    finally:
        report("stopped", None)
