"""Карточка с визуальной настройкой сворачивания окна."""

import tkinter as tk
from tkinter import ttk

from ui import theme


class WindowOptionCard(tk.Frame):
    def __init__(self, master):
        super().__init__(
            master,
            bg=theme.CARD,
            padx=20,
            pady=16,
            highlightthickness=1,
            highlightbackground=theme.CARD_BORDER,
        )
        self.minimize = tk.BooleanVar(value=False)
        self._build()

    def _build(self):
        tk.Label(
            self,
            text="Поведение окна",
            bg=theme.CARD,
            fg=theme.TEXT,
            font=("Segoe UI", 11, "bold"),
        ).pack(anchor="w")

        ttk.Checkbutton(
            self,
            text="Сворачивать выбранное приложение Roblox",
            variable=self.minimize,
            style="Demo.TCheckbutton",
        ).pack(anchor="w", pady=(12, 2))

        tk.Label(
            self,
            text="Настройка показана для макета и пока ничего не сворачивает.",
            bg=theme.CARD,
            fg=theme.MUTED,
            font=("Segoe UI", 9),
        ).pack(anchor="w", padx=(24, 0))