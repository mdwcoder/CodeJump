from __future__ import annotations

import flet as ft

from codejump.app.controllers.app_controller import AppController
from codejump.app.ui.main_view import MainView
from codejump.utils.logging_setup import configure_logging
from codejump.utils.paths import ASSETS_DIR, ensure_runtime_dirs


async def app_main(page: ft.Page) -> None:
    controller = AppController()
    view = MainView(page, controller)
    await view.initialize()


def main() -> None:
    configure_logging()
    ensure_runtime_dirs()
    ft.run(app_main, assets_dir=str(ASSETS_DIR))


if __name__ == "__main__":
    main()
