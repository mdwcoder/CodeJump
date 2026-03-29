from __future__ import annotations

import flet as ft

from codejump.app.ui import theme


class HeaderBar(ft.Container):
    def __init__(
        self,
        project_dropdown: ft.Dropdown,
        on_reindex,
        on_manage_projects,
        on_settings,
        on_toggle_pin,
        on_minimize,
    ) -> None:
        self.project_dropdown = project_dropdown
        self.compact_mode = False
        self.pin_button = ft.IconButton(
            icon=ft.Icons.PUSH_PIN_ROUNDED,
            icon_color=theme.ACCENT,
            tooltip="Always on top",
            on_click=on_toggle_pin,
        )
        self.reindex_button = ft.IconButton(
            icon=ft.Icons.REFRESH_ROUNDED,
            tooltip="Reindex current project",
            on_click=on_reindex,
        )
        self.projects_button = ft.IconButton(
            icon=ft.Icons.FOLDER_OPEN_ROUNDED,
            tooltip="Manage projects",
            on_click=on_manage_projects,
        )
        self.settings_button = ft.IconButton(
            icon=ft.Icons.SETTINGS_ROUNDED,
            tooltip="Settings",
            on_click=on_settings,
        )
        self.minimize_button = ft.IconButton(
            icon=ft.Icons.REMOVE_ROUNDED,
            tooltip="Minimize",
            on_click=on_minimize,
        )
        self.brand = ft.Text("CODEJUMP", size=17, weight=ft.FontWeight.W_700, color=theme.TEXT)
        self.project_shell = ft.Container(
            bgcolor="#121820",
            border_radius=10,
            padding=ft.padding.symmetric(horizontal=8, vertical=3),
            content=project_dropdown,
            width=180,
        )
        self.leading_row = ft.Row(
            controls=[
                self.brand,
                self.project_shell,
            ],
            spacing=10,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            expand=True,
        )
        self.actions = ft.Row(
            controls=[
                self.reindex_button,
                self.projects_button,
                self.settings_button,
                self.pin_button,
                self.minimize_button,
            ],
            spacing=2,
        )
        super().__init__(
            padding=ft.padding.only(left=18, top=14, right=14, bottom=10),
            content=ft.Column(spacing=8),
        )
        self._apply_layout()

    def set_pin_state(self, pinned: bool) -> None:
        self.pin_button.icon_color = theme.ACCENT if pinned else theme.MUTED
        self.pin_button.selected = pinned

    def set_project_width(self, width: int) -> None:
        self.project_shell.width = width
        self.project_dropdown.width = max(72, width - 16)

    def set_compact_mode(self, compact: bool) -> None:
        self.compact_mode = compact
        self._apply_layout()

    def _apply_layout(self) -> None:
        if self.compact_mode:
            self.content.controls = [
                ft.Row(
                    controls=[self.brand, self.actions],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                self.project_shell,
            ]
            self.project_shell.expand = False
            return

        self.content.controls = [
            ft.Row(
                controls=[self.leading_row, self.actions],
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            )
        ]
        self.project_shell.expand = False
