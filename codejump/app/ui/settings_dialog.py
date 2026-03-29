from __future__ import annotations

import flet as ft

from codejump.app.ui import theme


class SettingsDialog(ft.AlertDialog):
    def __init__(self, on_save, on_save_geometry, on_reset_geometry) -> None:
        self.always_on_top = ft.Switch(label="Always on top")
        self.remember_geometry = ft.Switch(label="Remember window geometry")
        self.start_with_last_project = ft.Switch(label="Start with last project")
        self.start_with_last_query = ft.Switch(label="Start with last query")
        self.theme_mode = ft.Dropdown(
            label="Theme",
            options=[ft.dropdown.Option("dark")],
            value="dark",
        )
        self.default_editor_command = ft.TextField(label="Default editor command", hint_text="code")
        content = ft.Column(
            tight=True,
            spacing=12,
            controls=[
                self.always_on_top,
                self.remember_geometry,
                self.start_with_last_project,
                self.start_with_last_query,
                self.theme_mode,
                self.default_editor_command,
                ft.Row(
                    controls=[
                        ft.TextButton("Save current size & position", on_click=on_save_geometry),
                        ft.TextButton("Reset geometry", on_click=on_reset_geometry),
                    ],
                    wrap=True,
                ),
            ],
        )
        super().__init__(
            modal=True,
            bgcolor=theme.PANEL,
            title=ft.Text("Settings", color=theme.TEXT),
            content=ft.Container(width=420, content=content),
            actions=[
                ft.TextButton("Cancel"),
                ft.FilledButton("Save", on_click=on_save),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
