from __future__ import annotations
from typing import cast

import flet as ft

from codejump.app.controllers.app_controller import AppController
from codejump.app.ui import theme
from codejump.app.ui.header import HeaderBar
from codejump.app.ui.preview_panel import PreviewPanel
from codejump.app.ui.project_dialog import ProjectDialog
from codejump.app.ui.results_list import ResultsList
from codejump.app.ui.search_bar import SearchBar
from codejump.app.ui.settings_dialog import SettingsDialog
from codejump.core.enums import ThemeMode
from codejump.core.geometry import MIN_HEIGHT, MIN_WIDTH
from codejump.core.models import Project
from codejump.utils.validators import is_existing_directory, split_config_list


LAYOUT_BREAKPOINT = 920
PROJECT_LABEL_MAX_CHARS = 20
HEADER_COMPACT_BREAKPOINT = 390


class MainView:
    def __init__(self, page: ft.Page, controller: AppController) -> None:
        self.page = page
        self.controller = controller
        self.controller.bind_view(self)
        self.settings_dialog: SettingsDialog | None = None
        self.project_dialog: ProjectDialog | None = None
        theme.apply_page_theme(page)
        self.project_dropdown = ft.Dropdown(
            width=190,
            dense=True,
            text_size=12,
            border_color=ft.Colors.TRANSPARENT,
            content_padding=ft.padding.symmetric(horizontal=8, vertical=4),
            on_select=self._on_project_change,
            menu_width=320,
        )
        self.header = HeaderBar(
            project_dropdown=self.project_dropdown,
            on_reindex=lambda e: self.page.run_task(self._run_reindex),
            on_manage_projects=self._open_project_manager,
            on_settings=self._open_settings_dialog,
            on_toggle_pin=self._toggle_pin,
            on_minimize=self._minimize_window,
        )
        self.search_bar = SearchBar(self._on_search_change)
        self.results_list = ResultsList(self._select_result, self._open_result_by_index)
        self.preview_panel = PreviewPanel(self._open_selected, self._copy_selected_path)
        self.status_text = ft.Text("", size=11, color=theme.MUTED)
        self.body_host = ft.Container(expand=True)
        self.main_column = ft.Column(
            expand=True,
            spacing=0,
            controls=[
                self.header,
                self.search_bar,
                self.body_host,
                ft.Container(
                    padding=ft.padding.only(left=18, top=0, right=18, bottom=14),
                    content=self.status_text,
                ),
            ],
        )

    async def initialize(self) -> None:
        geometry = self.controller.settings_controller.resolve_geometry()
        self._configure_window(geometry)
        self.page.add(self.main_column)
        self.page.on_keyboard_event = self._on_keyboard
        self.page.on_resize = self._on_resize
        if hasattr(self.page.window, "on_event"):
            self.page.window.on_event = self._on_window_event
        self.controller.initialize()
        self.search_bar.input.value = self.controller.search_controller.query
        self.refresh()
        await self.controller.ensure_index_for_current_project()
        self.refresh()

    def refresh(self) -> None:
        self._refresh_projects()
        self.results_list.render(self.controller.search_controller.results, self.controller.search_controller.selected_index)
        project = self.controller.current_project
        self.preview_panel.render(
            self.controller.selected_result,
            project_missing=bool(project and not project.exists),
        )
        self.header.set_pin_state(self.controller.settings.always_on_top)
        self._refresh_status()
        self._refresh_layout()
        self.page.update()

    def show_message(self, message: str) -> None:
        self.page.snack_bar = ft.SnackBar(content=ft.Text(message))
        self.page.snack_bar.open = True
        self.status_text.value = message
        self.page.update()

    def _configure_window(self, geometry) -> None:
        self.page.title = "CodeJump"
        self.page.window.resizable = True
        self.page.window.minimizable = True
        self.page.window.width = geometry.width
        self.page.window.height = geometry.height
        self.page.window.left = geometry.left
        self.page.window.top = geometry.top
        self.page.window.min_width = MIN_WIDTH
        self.page.window.min_height = MIN_HEIGHT
        self.page.window.always_on_top = self.controller.settings.always_on_top

    def _refresh_projects(self) -> None:
        active_project = self.controller.current_project
        self.project_dropdown.options = [
            ft.dropdown.Option(
                key=project.id,
                text=self._project_dropdown_label(project),
            )
            for project in self.controller.project_controller.projects
        ]
        self.project_dropdown.value = self.controller.project_controller.active_project_id
        self.project_dropdown.tooltip = active_project.name if active_project else "Select a project"

    def _project_dropdown_label(self, project: Project) -> str:
        label = project.name if project.exists else f"{project.name} (missing)"
        if len(label) <= PROJECT_LABEL_MAX_CHARS:
            return label
        return f"{label[:PROJECT_LABEL_MAX_CHARS - 1]}…"

    def _refresh_layout(self) -> None:
        page_width = self.page.width or LAYOUT_BREAKPOINT
        self._refresh_header_layout(page_width)
        is_wide = page_width >= LAYOUT_BREAKPOINT
        if is_wide:
            self.body_host.content = ft.Row(
                expand=True,
                controls=[
                    ft.Container(expand=3, content=self.results_list),
                    ft.Container(expand=2, content=self.preview_panel),
                ],
            )
        else:
            self.body_host.content = ft.Column(
                expand=True,
                controls=[
                    ft.Container(expand=3, content=self.results_list),
                    ft.Container(height=240, content=self.preview_panel),
                ],
            )

    def _refresh_header_layout(self, page_width: int) -> None:
        compact = page_width < HEADER_COMPACT_BREAKPOINT
        self.header.set_compact_mode(compact)
        if compact:
            project_width = max(170, page_width - 42)
        else:
            project_width = max(120, min(210, page_width - 250))
        self.header.set_project_width(project_width)

    def _refresh_status(self) -> None:
        project = self.controller.current_project
        if project is None:
            self.status_text.value = "Add a project to start indexing and searching."
            return
        if not project.exists:
            self.status_text.value = "Selected project path is missing."
            return
        item_count = len(self.controller.current_index.items) if self.controller.current_index else 0
        if self.controller.is_reindexing:
            self.status_text.value = f"Indexing {project.name}..."
            return
        if item_count == 0:
            self.status_text.value = "No cached index yet. Reindex the project to populate results."
            return
        self.status_text.value = f"{project.name} · {item_count} indexed items"

    async def _run_reindex(self) -> None:
        await self.controller.reindex_current_project()

    def _on_search_change(self, event: ft.ControlEvent) -> None:
        query = cast(str, getattr(event.control, "value", "") or event.data or "")
        self.controller.set_query(query)
        self.refresh()

    def _on_project_change(self, event: ft.ControlEvent) -> None:
        project_id = cast(str | None, getattr(event.control, "value", None) or event.data)
        self.controller.set_active_project(project_id)
        self.refresh()

    def _select_result(self, index: int) -> None:
        self.controller.select_index(index)

    def _open_result_by_index(self, index: int) -> None:
        self.controller.select_index(index)
        self.controller.open_selected()

    def _open_selected(self, event=None) -> None:
        self.controller.open_selected()

    async def _copy_selected_path(self, event=None) -> None:
        result = self.controller.selected_result
        if not result:
            return
        self.page.clipboard.set(result.item.full_path)
        self.show_message("Path copied to clipboard.")

    def _toggle_pin(self, event=None) -> None:
        new_value = not self.controller.settings.always_on_top
        self.controller.update_settings(always_on_top=new_value)
        self.page.window.always_on_top = new_value
        self.refresh()

    def _minimize_window(self, event=None) -> None:
        self.page.window.minimized = True

    def _open_settings_dialog(self, event=None) -> None:
        dialog = SettingsDialog(self._save_settings, self._save_current_geometry, self._reset_geometry)
        self.settings_dialog = dialog
        dialog.always_on_top.value = self.controller.settings.always_on_top
        dialog.remember_geometry.value = self.controller.settings.remember_window_geometry
        dialog.start_with_last_project.value = self.controller.settings.start_with_last_project
        dialog.start_with_last_query.value = self.controller.settings.start_with_last_query
        dialog.theme_mode.value = self.controller.settings.theme.value
        dialog.default_editor_command.value = self.controller.settings.default_editor_command
        dialog.actions[0].on_click = lambda e: self._close_dialog(dialog)
        dialog.open = True
        self.page.show_dialog(dialog)

    def _save_settings(self, event: ft.ControlEvent) -> None:
        dialog = self.settings_dialog
        if dialog is None:
            return
        self.controller.update_settings(
            always_on_top=bool(dialog.always_on_top.value),
            remember_window_geometry=bool(dialog.remember_geometry.value),
            start_with_last_project=bool(dialog.start_with_last_project.value),
            start_with_last_query=bool(dialog.start_with_last_query.value),
            theme=ThemeMode(dialog.theme_mode.value or "dark"),
            default_editor_command=dialog.default_editor_command.value.strip() or "code",
        )
        self.page.window.always_on_top = self.controller.settings.always_on_top
        self._close_dialog(dialog)
        self.refresh()

    def _save_current_geometry(self, event: ft.ControlEvent) -> None:
        self.controller.update_window_geometry(
            width=int(self.page.window.width),
            height=int(self.page.window.height),
            left=int(self.page.window.left),
            top=int(self.page.window.top),
        )
        self.show_message("Current window size and position saved.")

    def _reset_geometry(self, event: ft.ControlEvent) -> None:
        geometry = self.controller.reset_geometry()
        self._configure_window(geometry)
        if self.settings_dialog:
            self._close_dialog(self.settings_dialog)
        self.show_message("Window geometry reset.")
        self.refresh()

    def _open_project_manager(self, event=None) -> None:
        project = self.controller.current_project
        dialog = ProjectDialog("Project", self._save_project)
        self.project_dialog = dialog
        if project:
            dialog.name.value = project.name
            dialog.root_path.value = project.root_path
            dialog.editor_command.value = project.editor_command
            dialog.priority_extensions.value = ", ".join(project.priority_extensions)
            dialog.ignored_dirs.value = ", ".join(project.ignored_dirs)
            dialog.aliases.value = ", ".join(project.aliases)
            dialog.data = project.id
        dialog.actions.insert(
            1,
            ft.TextButton("New", on_click=lambda e: self._prepare_new_project(dialog)),
        )
        dialog.actions.insert(
            2,
            ft.TextButton(
                "Delete current",
                on_click=lambda e: self._delete_current_project(dialog),
                visible=project is not None,
            ),
        )
        dialog.actions[0].on_click = lambda e: self._close_dialog(dialog)
        dialog.open = True
        self.page.show_dialog(dialog)

    def _save_project(self, event: ft.ControlEvent) -> None:
        dialog = self.project_dialog
        if dialog is None:
            return
        if not dialog.name.value.strip():
            self.show_message("Project name is required.")
            return
        if not is_existing_directory(dialog.root_path.value):
            self.show_message("Root path must be an existing directory.")
            return
        project = Project(
            name=dialog.name.value.strip(),
            root_path=dialog.root_path.value.strip(),
            editor_command=(dialog.editor_command.value or self.controller.settings.default_editor_command).strip() or "code",
            priority_extensions=split_config_list(dialog.priority_extensions.value),
            ignored_dirs=split_config_list(dialog.ignored_dirs.value),
            aliases=split_config_list(dialog.aliases.value),
        )
        if dialog.data:
            project.id = cast(str, dialog.data)
        self.controller.save_project(project)
        self._close_dialog(dialog)
        self.page.run_task(self._run_reindex)
        self.refresh()

    def _delete_current_project(self, dialog: ProjectDialog) -> None:
        project_id = dialog.data
        if not project_id:
            return
        self.controller.delete_project(project_id)
        self._close_dialog(dialog)
        self.show_message("Project deleted.")
        self.refresh()

    def _close_dialog(self, dialog: ft.AlertDialog) -> None:
        dialog.open = False
        if dialog is self.settings_dialog:
            self.settings_dialog = None
        if dialog is self.project_dialog:
            self.project_dialog = None
        self.page.pop_dialog()

    def _prepare_new_project(self, dialog: ProjectDialog) -> None:
        dialog.data = None
        dialog.title = ft.Text("New project", color=theme.TEXT)
        dialog.name.value = ""
        dialog.root_path.value = ""
        dialog.editor_command.value = self.controller.settings.default_editor_command
        dialog.priority_extensions.value = ""
        dialog.ignored_dirs.value = ""
        dialog.aliases.value = ""
        if len(dialog.actions) > 2:
            dialog.actions[2].visible = False
        dialog.update()

    def _on_keyboard(self, event: ft.KeyboardEvent) -> None:
        key = (event.key or "").lower()
        modifier = bool(event.ctrl or event.meta)
        if key == "arrow down":
            self.controller.move_selection(1)
            return
        if key == "arrow up":
            self.controller.move_selection(-1)
            return
        if key == "enter":
            self.controller.open_selected()
            return
        if key == "escape":
            if self.search_bar.input.value:
                self.search_bar.input.value = ""
                self.controller.set_query("")
                self.refresh()
            else:
                self.page.window.minimized = True
            return
        if modifier and key == "c":
            self.page.run_task(self._copy_selected_path)

    def _on_resize(self, event: ft.ControlEvent) -> None:
        self._refresh_layout()
        self.page.update()

    def _on_window_event(self, event) -> None:
        event_type = str(getattr(event, "data", ""))
        if event_type not in {"moved", "resized", "close"}:
            return
        try:
            self.controller.update_window_geometry(
                width=int(self.page.window.width),
                height=int(self.page.window.height),
                left=int(self.page.window.left),
                top=int(self.page.window.top),
            )
        except Exception:
            return
