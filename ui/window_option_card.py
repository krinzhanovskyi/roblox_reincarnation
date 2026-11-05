"""Visual window preference control."""

import tkinter as tk

from ui import theme


class WindowOptionCard(tk.Frame):
    def __init__(self, master, value=False, scale=1.0):
        super().__init__(master, bg=theme.SURFACE)

        self.scale = scale
        self.switch_to_roblox = tk.BooleanVar(master=self, value=value)
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
            variable=self.switch_to_roblox,
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
        self.checkbox.pack(anchor="w", pady=(round(12 * self.scale), 0))

        tk.Label(
            self,
            text="Preference saved for future use.\nRoblox switching is not implemented yet.",
            justify="left",
            bg=theme.SURFACE,
            fg=theme.MUTED,
            font=(theme.FONT, 9),
        ).pack(anchor="w", padx=(round(25 * self.scale), 0),
               pady=(round(3 * self.scale), 0))
