import json
import logging
from dataclasses import asdict, dataclass
from pathlib import Path

SETTINGS_PATH = Path(__file__).resolve().parent.parent / "settings.json"
logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class Settings:
    interval_minutes: int = 10
    switch_to_roblox: bool = True

    def __post_init__(self):
        if type(self.interval_minutes) is not int or not 1 <= self.interval_minutes <= 20:
            raise ValueError("Interval must be an integer between 1 and 20 minutes.")
        if type(self.switch_to_roblox) is not bool:
            raise ValueError("Window preference must be a boolean.")


def load_settings(path=SETTINGS_PATH):
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
    except FileNotFoundError:
        logger.info("Settings file not found; using defaults")
        return Settings()
    if not isinstance(data, dict):
        raise ValueError("Settings must be a JSON object.")
    settings = Settings(
        interval_minutes=data.get("interval_minutes", 10),
        switch_to_roblox=data.get("switch_to_roblox", True),
    )
    logger.info("Settings loaded: interval=%s minutes, switch_to_roblox=%s",
                settings.interval_minutes, settings.switch_to_roblox)
    return settings


def save_settings(settings, path=SETTINGS_PATH):
    path = Path(path)
    temporary_path = path.with_suffix(path.suffix + ".tmp")
    try:
        temporary_path.write_text(
            json.dumps(asdict(settings), indent=2) + "\n", encoding="utf-8"
        )
        temporary_path.replace(path)
        logger.info("Settings saved: interval=%s minutes, switch_to_roblox=%s",
                    settings.interval_minutes, settings.switch_to_roblox)
    finally:
        temporary_path.unlink(missing_ok=True)
