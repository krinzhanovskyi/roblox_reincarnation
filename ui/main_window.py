"""Main settings window."""

import tkinter as tk
from tkinter import messagebox

from settings import Settings, load_settings, save_settings

from ui import theme
from ui.interval_card import IntervalCard
from ui.window_option_card import WindowOptionCard

class SettingsWindow(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Reincarnation AFK — Settings")

        self.scale = self.winfo_fpixels("1i") / 96
        self.configure(bg=theme.BG)

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
            text="Choose your preferred session settings.",
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

        footer = tk.Frame(content, bg=theme.BG)
        footer.pack(fill="x", side="bottom", pady=(self.px(20), 0))

        tk.Label(
            footer,
            text="Settings only",
            bg=theme.BG,
            fg=theme.MUTED,
            font=(theme.FONT, 9),
        ).pack(side="left")

        tk.Button(
            footer,
            text="Save & close",
            command=self._save_and_close,
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

    def _save_and_close(self):
        settings = Settings(
            interval_minutes=self.interval_card.value.get(),
            switch_to_roblox=self.window_option_card.switch_to_roblox.get(),
        )
        try:
            save_settings(settings)
        except OSError as error:
            messagebox.showerror("Could not save settings", str(error), parent=self)
            return
        self.settings = settings
        self.destroy()

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
