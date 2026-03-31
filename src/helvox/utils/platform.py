import platform
from pathlib import Path

from platformdirs import user_data_path


def app_font(size: int, *, bold: bool = False) -> tuple[str, int] | tuple[str, int, str]:
    system = platform.system()

    if system == "Windows":
        family = "Segoe UI"
    elif system == "Darwin":
        family = "Helvetica"
    else:
        family = "Arial"

    if bold:
        return (family, size, "bold")

    return (family, size)


def default_recordings_dir() -> Path:
    return user_data_path(appname="helvox", appauthor="noxenum") / "recordings"
