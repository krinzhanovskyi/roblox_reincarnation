import tkinter as tk
from tkinter import messagebox
from queue import Empty, Queue
from threading import Event, Thread
import time

from logic.anti_afk import run_session
from logic.settings import Settings, load_settings, save_settings
from logic.windows_backend import AutomationError, WindowsBackend

from ui import theme
from ui.interval_card import IntervalCard
from ui.window_option_card import WindowOptionCard


class SettingsWindow(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Reincarnation AFK — Settings")

        self.scale = self.winfo_fpixels("1i") / 96
        self.configure(bg=theme.BG)
        self._worker = None
        self._stop = Event()
        self._events = Queue()
        self._deadline = None
        self._closing = False
        self.status = tk.StringVar(master=self, value="Stopped")
        self.last_result = tk.StringVar(master=self, value="Open a Roblox game, then press Start.")
        self.protocol("WM_DELETE_WINDOW", self._on_close)

        load_error = None
        try:
            self.settings = load_settings()
        except (OSError, ValueError) as error:
            self.settings = Settings()
            load_error = str(error)
        self._build()
        self.update_idletasks()
        width = max(self.px(520), self.winfo_reqwidth())
        height = max(self.px(460), self.winfo_reqheight())
        self.geometry(f"{width}x{height}")
        self.minsize(self.winfo_reqwidth(), self.winfo_reqheight())
        self.after(100, self._poll_session)
        if load_error:
            self.after_idle(lambda: messagebox.showwarning(
                "Settings could not be loaded",
                f"Default settings are shown.\n\n{load_error}", parent=self,
            ))

    def px(self, value):
        return max(1, round(value * self.scale))

    def _build(self):
        content = tk.Frame(self, bg=theme.BG, padx=self.px(28), pady=self.px(26))
        content.pack(fill="both", expand=True)

        tk.Label(
            content,
            text="REINCARNATION AFK",
            bg=theme.BG,
            fg=theme.ACCENT,
            font=(theme.FONT, 9, "bold"),
        ).pack(anchor="w")

        tk.Label(
            content,
            text="Settings",
            bg=theme.BG,
            fg=theme.TEXT,
            font=(theme.FONT, 24, "bold"),
        ).pack(anchor="w", pady=(self.px(5), self.px(2)))

        tk.Label(
            content,
            text="Choose your interval, then start the session.",
            bg=theme.BG,
            fg=theme.MUTED,
            font=(theme.FONT, 10),
        ).pack(anchor="w")

        self.interval_card = self._add_section(
            content, IntervalCard, top=24, value=self.settings.interval_minutes
        )
        self.window_option_card = self._add_section(
            content, WindowOptionCard, top=12, value=self.settings.switch_to_roblox
        )

        tk.Label(
            content, textvariable=self.status, bg=theme.BG, fg=theme.ACCENT,
            font=(theme.FONT, 11, "bold"),
        ).pack(anchor="w", pady=(self.px(16), self.px(4)))
        tk.Label(
            content, textvariable=self.last_result, bg=theme.BG, fg=theme.MUTED,
            font=(theme.FONT, 9), justify="left", wraplength=self.px(430),
        ).pack(anchor="w")

        footer = tk.Frame(content, bg=theme.BG)
        footer.pack(fill="x", side="bottom", pady=(self.px(20), 0))

        tk.Button(
            footer,
            text="Save settings",
            command=self._save_settings,
            bg=theme.ACCENT_DARK,
            fg="#ffffff",
            activebackground=theme.ACCENT,
            activeforeground="#ffffff",
            relief="flat",
            borderwidth=0,
            padx=self.px(20),
            pady=self.px(9),
            font=(theme.FONT, 10, "bold"),
            cursor="hand2",
        ).pack(side="right")

        self.start_button = tk.Button(
            footer, text="Start", command=self._toggle_session,
            bg=theme.ACCENT_DARK, fg="#ffffff", activebackground=theme.ACCENT,
            activeforeground="#ffffff", relief="flat", borderwidth=0,
            padx=self.px(20), pady=self.px(9),
            font=(theme.FONT, 10, "bold"), cursor="hand2",
        )
        self.start_button.pack(side="left")

    def _save_settings(self):
        settings = Settings(
            interval_minutes=self.interval_card.value.get(),
            switch_to_roblox=self.window_option_card.switch_to_roblox.get(),
        )
        try:
            save_settings(settings)
        except OSError as error:
            messagebox.showerror("Could not save settings", str(error), parent=self)
            return False
        self.settings = settings
        return True

    def _toggle_session(self):
        if self._worker and self._worker.is_alive():
            self._stop.set()
            self.start_button.configure(state="disabled", text="Stopping…")
            self.status.set("Stopping and restoring the previous window…")
            return
        try:
            backend = WindowsBackend()
            backend.find_roblox()
        except (AutomationError, OSError) as error:
            messagebox.showerror("Cannot start Anti-AFK", str(error), parent=self)
            return
        if not self._save_settings():
            return
        self._stop = Event()
        self._worker = Thread(
            target=run_session,
            args=(backend, self.settings, self._stop,
                  lambda kind, value: self._events.put((kind, value))),
            name="AntiAFK",
        )
        self.last_result.set("Running. Setting changes apply to the next session.")
        self.start_button.configure(text="Stop")
        self._worker.start()

    def _poll_session(self):
        try:
            while True:
                kind, value = self._events.get_nowait()
                if kind == "waiting":
                    self._deadline = value
                elif kind == "working":
                    self._deadline = None
                    self.status.set(value)
                elif kind == "result":
                    self.last_result.set(value)
                elif kind == "stopped":
                    self._deadline = None
        except Empty:
            pass
        running = self._worker is not None and self._worker.is_alive()
        if self._closing and not running:
            self.destroy()
            return
        if not running:
            self._deadline = None
            self.status.set("Stopped")
            self.start_button.configure(text="Start", state="normal")
        elif self._stop.is_set():
            self.status.set("Stopping and restoring the previous window…")
        elif self._deadline is not None:
            remaining = max(0, int(self._deadline - time.monotonic() + 0.999))
            self.status.set(f"Next jump in {remaining // 60:02d}:{remaining % 60:02d}")
        self.after(100, self._poll_session)

    def _on_close(self):
        self._closing = True
        self._stop.set()
        self.start_button.configure(state="disabled")
        self.status.set("Stopping and restoring the previous window…")

    def _add_section(self, parent, widget_class, top, value):
        section = tk.Frame(
            parent,
            bg=theme.SURFACE,
            padx=self.px(18),
            pady=self.px(16),
            highlightthickness=self.px(1),
            highlightbackground=theme.BORDER,
        )
        section.pack(fill="x", pady=(self.px(top), 0))

        widget = widget_class(section, value=value, scale=self.scale)
        widget.pack(fill="x")
        return widget
