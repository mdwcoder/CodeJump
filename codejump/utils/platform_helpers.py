from __future__ import annotations

import platform
from dataclasses import dataclass


@dataclass(slots=True)
class ScreenSize:
    width: int
    height: int


def is_macos() -> bool:
    return platform.system() == "Darwin"


def is_linux() -> bool:
    return platform.system() == "Linux"


def get_screen_size() -> ScreenSize:
    try:
        import tkinter as tk

        root = tk.Tk()
        root.withdraw()
        width = int(root.winfo_screenwidth())
        height = int(root.winfo_screenheight())
        root.destroy()
        return ScreenSize(width=width, height=height)
    except Exception:
        return ScreenSize(width=1440, height=960)

