from __future__ import annotations

import flet as ft

from codejump.app.ui import theme
from codejump.core.models import SearchResult


class PreviewPanel(ft.Container):
    def __init__(self, on_open, on_copy_path) -> None:
        self.on_open = on_open
        self.on_copy_path = on_copy_path
        self.body = ft.Column(spacing=10, expand=True)
        super().__init__(
            expand=True,
            padding=ft.padding.only(left=8, top=0, right=18, bottom=16),
            content=ft.Container(
                expand=True,
                padding=18,
                **theme.panel_style(),
                content=self.body,
            ),
        )

    def render(self, result: SearchResult | None, project_missing: bool = False) -> None:
        self.body.controls.clear()
        if result is None:
            message = "Select a result to inspect its preview." if not project_missing else "The selected project path is no longer available."
            self.body.controls.extend(
                [
                    ft.Text("Preview", size=14, weight=ft.FontWeight.W_600, color=theme.TEXT),
                    ft.Text(message, size=12, color=theme.MUTED),
                ]
            )
            return

        item = result.item
        meta_text = [item.item_type.value]
        if item.symbol_kind:
            meta_text.append(item.symbol_kind.value)
        if item.line:
            meta_text.append(f"line {item.line}")

        self.body.controls.extend(
            [
                ft.Text(item.display_name, size=18, weight=ft.FontWeight.W_700, color=theme.TEXT),
                ft.Text(item.full_path, size=11, color=theme.MUTED),
                ft.Row(
                    controls=[
                        ft.Container(
                            bgcolor="#18202B",
                            border_radius=999,
                            padding=ft.padding.symmetric(horizontal=9, vertical=5),
                            content=ft.Text(" · ".join(meta_text).upper(), size=10, color=theme.ACCENT),
                        )
                    ]
                ),
                ft.Text(result.explanation.summary() or "Fast jump target", size=12, color="#B4C0D4"),
                ft.Container(
                    expand=True,
                    bgcolor="#090B0F",
                    border_radius=14,
                    padding=14,
                    content=ft.Text(
                        item.preview or "No preview available for this item.",
                        size=12,
                        color="#D7DDEA",
                        selectable=True,
                    ),
                ),
                ft.Row(
                    controls=[
                        ft.FilledButton("Open", icon=ft.Icons.OPEN_IN_NEW_ROUNDED, on_click=self.on_open),
                        ft.OutlinedButton("Copy path", icon=ft.Icons.CONTENT_COPY_ROUNDED, on_click=self.on_copy_path),
                    ],
                    spacing=10,
                ),
            ]
        )
