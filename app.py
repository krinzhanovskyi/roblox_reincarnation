from logic.dpi import configure_dpi
from ui.main_window import SettingsWindow


if __name__ == "__main__":
    configure_dpi()
    SettingsWindow().mainloop()
