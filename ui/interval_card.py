"""Reminder interval control."""

import tkinter as tk

from ui import theme


class IntervalCard(tk.Frame):
    def __init__(self, master, value=10, scale=1.0):
        super().__init__(master, bg=theme.SURFACE)

        self.scale = scale
        self.value = tk.IntVar(master=self, value=value)
        self.value_label = tk.StringVar(master=self, value=f"{value} min")

        self._build()

    def px(self, value):
        return max(1, round(value * self.scale))

    def _build(self):
        header = tk.Frame(self, bg=theme.SURFACE)
        header.pack(fill="x")

        tk.Label(
            header,
            text="Reminder interval",
            bg=theme.SURFACE,
            fg=theme.TEXT,
            font=(theme.FONT, 11, "bold"),
        ).pack(side="left")

        tk.Label(
            header,
            textvariable=self.value_label,
            bg=theme.SURFACE,
            fg=theme.ACCENT,
            font=(theme.FONT, 11, "bold"),
        ).pack(side="right")

        self.slider = tk.Canvas(
            self,
            height=self.px(24),
            bg=theme.SURFACE,
            highlightthickness=0,
            cursor="hand2",
        )
        self.slider.pack(fill="x", pady=(self.px(14), self.px(2)))

        self.slider.bind("<Configure>", self._draw_slider)
        self.slider.bind("<Button-1>", self._on_slider_move)
        self.slider.bind("<B1-Motion>", self._on_slider_move)

        limits = tk.Frame(self, bg=theme.SURFACE)
        limits.pack(fill="x")

        tk.Label(
            limits,
            text="1 min",
            bg=theme.SURFACE,
            fg=theme.MUTED,
            font=(theme.FONT, 9),
        ).pack(side="left")

        tk.Label(
            limits,
            text="20 min",
            bg=theme.SURFACE,
            fg=theme.MUTED,
            font=(theme.FONT, 9),
        ).pack(side="right")

    def _draw_slider(self, _event=None):
        canvas = self.slider
        canvas.delete("all")

        width = canvas.winfo_width()
        center_y = canvas.winfo_height() / 2
        padding = self.px(10)
        usable_width = max(width - padding * 2, 1)

        progress = (self.value.get() - 1) / 19
        knob_x = padding + usable_width * progress

        canvas.create_line(
            padding,
            center_y,
            width - padding,
            center_y,
            fill=theme.BORDER,
            width=self.px(6),
            capstyle=tk.ROUND,
        )
        canvas.create_line(
            padding,
            center_y,
            knob_x,
            center_y,
            fill=theme.ACCENT,
            width=self.px(6),
            capstyle=tk.ROUND,
        )
        canvas.create_oval(
            knob_x - self.px(7),
            center_y - self.px(7),
            knob_x + self.px(7),
            center_y + self.px(7),
            fill=theme.ACCENT,
            outline=theme.SURFACE,
            width=self.px(2),
        )

    def _on_slider_move(self, event):
        width = self.slider.winfo_width()
        padding = self.px(10)
        usable_width = max(width - padding * 2, 1)

        position = min(max(event.x - padding, 0), usable_width)
        value = round(1 + (position / usable_width) * 19)

        self.value.set(value)
        self.value_label.set(f"{value} min")
        self._draw_slider()
