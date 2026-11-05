# Reincarnation AFK

A Roblox Anti-AFK prototype built with Python and Tkinter.

## Getting started

Requires Python 3.10 or later with Tkinter. Tkinter is included in the standard
Python installation for Windows; no third-party packages are required.

From the project directory, run:

```powershell
python app.py
```

If you use the Python Launcher, you can run `py app.py` instead.

## Features

- Choose an interval from 1 to 20 minutes (default: 10).
- Set a preference to switch to the Roblox window (disabled by default).
- Save settings with `Save & close` and restore them on startup.
- Dark theme with element sizes adjusted for DPI on startup.

# Settings

Saving creates a `settings.json` file next to `app.py`. The project directory
must be writable. Example:

```json
{
  "interval_minutes": 10,
  "switch_to_roblox": false
}
```

If the file is missing, default values are used. An invalid or unreadable file
triggers a warning, and default values are displayed. Invalid types and intervals
outside the allowed range are rejected. If saving fails, the window stays open
and displays an error message. Closing the window with the close button discards
unsaved changes.

## Project structure

```text
├── app.py                     # Application entry point
├── logic/                     # Core application logic
│   ├── __init__.py
│   ├── anti_afk.py            # Repeating timer and jump cycles
│   ├── dpi.py                 # Windows DPI setup
│   ├── settings.py            # Settings, validation, and JSON persistence
│   └── windows_backend.py     # Window discovery, switching, and keyboard input
├── tests/                     # Automated tests
│   ├── test_anti_afk.py
│   ├── test_settings.py
│   └── test_windows_backend.py
├── ui/                        # Tkinter interface
│   ├── __init__.py
│   ├── interval_card.py       # Interval slider
│   ├── main_window.py         # Main window and settings controls
│   ├── theme.py               # Shared colors and fonts
│   └── window_option_card.py  # Window-switching preference
├── .gitignore
└── README.md
```

`settings.json`, temporary files, and Python caches are excluded by `.gitignore`.

## Tests

```powershell
python -B -m unittest discover -s tests -v
```

Tests cover default values, saving and loading, rejection of invalid data,
and preservation of the previous file when writing fails.
