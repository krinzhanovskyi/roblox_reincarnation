BG = "#111318"
CARD = "#1b1e25"
TEXT = "#f1f3f5"
MUTED = "#9aa3b2"
ACCENT = "#7c5cff"
CARD_BORDER = "#2a2e38"


def configure_styles(root):
    import tkinter.ttk as ttk

    style = ttk.Style(root)
    style.theme_use("clam")
    style.configure(
        "Horizontal.TScale",
        background=CARD,
        troughcolor="#303440",
        sliderthickness=18,
        bordercolor=CARD,
        lightcolor=ACCENT,
        darkcolor=ACCENT,
    )
    style.configure(
        "Demo.TCheckbutton",
        background=CARD,
        foreground=TEXT,
        font=("Segoe UI", 10),
        focuscolor=CARD,
    )
    style.map("Demo.TCheckbutton", background=[("active", CARD)])