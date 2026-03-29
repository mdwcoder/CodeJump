from __future__ import annotations

import flet as ft

from codejump.app.ui import theme


class ProjectDialog(ft.AlertDialog):
    def __init__(self, title_text: str, on_save) -> None:
        self.name = ft.TextField(label="Project name")
        self.root_path = ft.TextField(label="Root path")
        self.editor_command = ft.TextField(label="Editor command", hint_text="code")
        self.priority_extensions = ft.TextField(label="Priority extensions", hint_text=".ts, .tsx, .dart")
        self.ignored_dirs = ft.TextField(label="Ignored dirs", hint_text="tmp, generated")
        self.aliases = ft.TextField(label="Aliases", hint_text="optional")
        content = ft.Column(
            tight=True,
            spacing=10,
            controls=[
                self.name,
                self.root_path,
                self.editor_command,
                self.priority_extensions,
                self.ignored_dirs,
                self.aliases,
            ],
        )
        super().__init__(
            modal=True,
            bgcolor=theme.PANEL,
            title=ft.Text(title_text, color=theme.TEXT),
            content=ft.Container(width=480, content=content),
            actions=[
                ft.TextButton("Cancel"),
                ft.FilledButton("Save", on_click=on_save),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

