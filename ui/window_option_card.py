"""Visual window preference control."""

import tkinter as tk

from ui import theme


class WindowOptionCard(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg=theme.SURFACE)

        self.minimize_window = tk.BooleanVar(value=False)
        self._build()

    def _build(self):
        tk.Label(
            self,
            text="Window behavior",
            bg=theme.SURFACE,
            fg=theme.TEXT,
            font=(theme.FONT, 11, "bold"),
        ).pack(anchor="w")

        self.checkbox = tk.Checkbutton(
            self,
            text="Switch to the Roblox window",
            variable=self.minimize_window,
            bg=theme.SURFACE,
            fg=theme.TEXT,
            activebackground=theme.SURFACE,
            activeforeground=theme.TEXT,
            selectcolor=theme.BG,
            font=(theme.FONT, 10),
            cursor="hand2",
            borderwidth=0,
            highlightthickness=0,
        )
        self.checkbox.pack(anchor="w", pady=(12, 0))

        tk.Label(
            self,
            text="Visual setting only; it does not control any application.",
            bg=theme.SURFACE,
            fg=theme.MUTED,
            font=(theme.FONT, 9),
        ).pack(anchor="w", padx=(25, 0), pady=(3, 0))