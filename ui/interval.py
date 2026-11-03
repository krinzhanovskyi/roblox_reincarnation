import tkinter as tk
from tkinter import ttk

from ui import theme


class IntervalCard(tk.Frame):
    def __init__(self, master):
        super().__init__(
            master,
            bg=theme.CARD,
            padx=20,
            pady=18,
            highlightthickness=1,
            highlightbackground=theme.CARD_BORDER,
        )
        self.interval = tk.DoubleVar(value=5)
        self.interval_text = tk.StringVar(value="5 мин")
        self._build()

    def _build(self):
        row = tk.Frame(self, bg=theme.CARD)
        row.pack(fill="x")

        tk.Label(
            row,
            text="Интервал напоминания",
            bg=theme.CARD,
            fg=theme.TEXT,
            font=("Segoe UI", 11, "bold"),
        ).pack(side="left")

        tk.Label(
            row,
            textvariable=self.interval_text,
            bg=theme.CARD,
            fg=theme.ACCENT,
            font=("Segoe UI", 11, "bold"),
        ).pack(side="right")

        ttk.Scale(
            self,
            from_=1,
            to=60,
            variable=self.interval,
            command=self._update_interval,
            style="Horizontal.TScale",
        ).pack(fill="x", pady=(18, 5))

        limits = tk.Frame(self, bg=theme.CARD)
        limits.pack(fill="x")

        tk.Label(
            limits,
            text="1 мин",
            bg=theme.CARD,
            fg=theme.MUTED,
            font=("Segoe UI", 9),
        ).pack(side="left")

        tk.Label(
            limits,
            text="60 мин",
            bg=theme.CARD,
            fg=theme.MUTED,
            font=("Segoe UI", 9),
        ).pack(side="right")

    def _update_interval(self, _value=None):
        self.interval_text.set(f"{round(self.interval.get())} мин")