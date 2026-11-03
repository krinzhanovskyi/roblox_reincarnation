"""Main settings window."""

import tkinter as tk

from ui import theme
from ui.interval_card import IntervalCard
from ui.window_option_card import WindowOptionCard
import ctypes

class SettingsWindow(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Reincarnation AFK — Settings")

        scale = ctypes.windll.user32.GetDpiForSystem() / 96
        self.geometry(f"{round(520 * scale)}x{round(460 * scale)}")
        self.minsize(round(460 * scale), round(400 * scale))
        self.configure(bg=theme.BG)

        self._build()

    def _build(self):
        content = tk.Frame(self, bg=theme.BG, padx=28, pady=26)
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
        ).pack(anchor="w", pady=(5, 2))

        tk.Label(
            content,
            text="Choose your preferred session settings.",
            bg=theme.BG,
            fg=theme.MUTED,
            font=(theme.FONT, 10),
        ).pack(anchor="w")

        self._add_section(content, IntervalCard, top=24)
        self._add_section(content, WindowOptionCard, top=12)

        footer = tk.Frame(content, bg=theme.BG)
        footer.pack(fill="x", side="bottom", pady=(20, 0))

        tk.Label(
            footer,
            text="Interface preview",
            bg=theme.BG,
            fg=theme.MUTED,
            font=(theme.FONT, 9),
        ).pack(side="left")

        tk.Button(
            footer,
            text="Done",
            command=self.destroy,
            bg=theme.ACCENT_DARK,
            fg="#ffffff",
            activebackground=theme.ACCENT,
            activeforeground="#ffffff",
            relief="flat",
            borderwidth=0,
            padx=20,
            pady=9,
            font=(theme.FONT, 10, "bold"),
            cursor="hand2",
        ).pack(side="right")

    @staticmethod
    def _add_section(parent, widget_class, top):
        section = tk.Frame(
            parent,
            bg=theme.SURFACE,
            padx=18,
            pady=16,
            highlightthickness=1,
            highlightbackground=theme.BORDER,
        )
        section.pack(fill="x", pady=(top, 0))

        widget = widget_class(section)
        widget.pack(fill="x")