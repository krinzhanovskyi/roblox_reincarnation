import tkinter as tk

from ui import theme
from ui.interval_card import IntervalCard
from ui.window_option_card import WindowOptionCard


class SettingsDemo(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Session Helper — макет")
        self.geometry("520x440")
        self.minsize(480, 420)
        self.configure(bg=theme.BG)

        theme.configure_styles(self)
        self._build()

    def _build(self):
        root = tk.Frame(self, bg=theme.BG, padx=30, pady=26)
        root.pack(fill="both", expand=True)

        tk.Label(
            root,
            text="SESSION HELPER",
            bg=theme.BG,
            fg=theme.ACCENT,
            font=("Segoe UI", 9, "bold"),
        ).pack(anchor="w")

        tk.Label(
            root,
            text="Настройки сессии",
            bg=theme.BG,
            fg=theme.TEXT,
            font=("Segoe UI", 23, "bold"),
        ).pack(anchor="w", pady=(5, 4))

        tk.Label(
            root,
            text="Демонстрационный интерфейс · без управления игрой",
            bg=theme.BG,
            fg=theme.MUTED,
            font=("Segoe UI", 10),
        ).pack(anchor="w")

        IntervalCard(root).pack(fill="x", pady=(26, 14))
        WindowOptionCard(root).pack(fill="x")

        footer = tk.Frame(root, bg=theme.BG)
        footer.pack(fill="x", pady=(20, 0))

        tk.Label(
            footer,
            text="Макет интерфейса",
            bg=theme.BG,
            fg=theme.MUTED,
            font=("Segoe UI", 9),
        ).pack(side="left")

        tk.Button(
            footer,
            text="Готово",
            command=self.destroy,
            bg=theme.ACCENT,
            fg="white",
            activebackground="#6c4df0",
            activeforeground="white",
            relief="flat",
            bd=0,
            padx=22,
            pady=9,
            font=("Segoe UI", 10, "bold"),
            cursor="hand2",
        ).pack(side="right")