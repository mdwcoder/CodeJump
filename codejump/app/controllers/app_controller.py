from __future__ import annotations

import asyncio
from datetime import datetime
from typing import TYPE_CHECKING

from codejump.app.controllers.project_controller import ProjectController
from codejump.app.controllers.search_controller import SearchController
from codejump.app.controllers.settings_controller import SettingsController
from codejump.core.models import HistoryState, Project, QueryHistoryEntry, RecentOpenEntry, SearchResult
from codejump.core.opener import EditorOpener
from codejump.core.project_indexer import ProjectIndexer
from codejump.core.search_engine import SearchEngine
from codejump.storage.history_store import HistoryStore
from codejump.storage.index_store import IndexStore
from codejump.storage.projects_store import ProjectsStore
from codejump.storage.settings_store import SettingsStore

if TYPE_CHECKING:
    from codejump.app.ui.main_view import MainView


class AppController:
    def __init__(self) -> None:
        self.settings_controller = SettingsController(SettingsStore())
        self.project_controller = ProjectController(ProjectsStore())
        self.search_controller = SearchController(SearchEngine())
        self.history_store = HistoryStore()
        self.index_store = IndexStore()
        self.project_indexer = ProjectIndexer()
        self.opener = EditorOpener()
        self.history = self.history_store.load()
        self.current_index = None
        self.view: MainView | None = None
        self.is_reindexing = False

    @property
    def settings(self):
        return self.settings_controller.settings

    @property
    def current_project(self) -> Project | None:
        return self.project_controller.get_active_project()

    @property
    def selected_result(self) -> SearchResult | None:
        return self.search_controller.selected_result

    def bind_view(self, view: MainView) -> None:
        self.view = view

    def initialize(self) -> None:
        selected_project_id = None
        if self.settings.start_with_last_project:
            selected_project_id = self.settings.selected_project_id
        if not selected_project_id and self.project_controller.projects:
            selected_project_id = self.project_controller.projects[0].id
        self.project_controller.set_active(selected_project_id)

        if self.settings.start_with_last_query:
            self.search_controller.set_query(self.settings.last_query)

        self.load_current_index()
        self.refresh_search()

    def load_current_index(self) -> None:
        project = self.current_project
        if not project:
            self.current_index = None
            return
        self.current_index = self.index_store.load(project.id)

    def refresh_search(self) -> None:
        self.search_controller.run_search(
            project=self.current_project,
            project_index=self.current_index,
            history=self.history,
            limit=self.settings.max_visible_results,
        )

    async def ensure_index_for_current_project(self) -> None:
        if self.current_project and self.current_index is None and self.current_project.exists:
            await self.reindex_current_project()

    async def reindex_current_project(self) -> None:
        project = self.current_project
        if not project:
            self.notify("Select a project first.")
            return
        if not project.exists:
            self.notify("Project path is missing.")
            return
        if self.is_reindexing:
            return

        self.is_reindexing = True
        self.notify("Reindexing project...")
        try:
            project_index = await asyncio.to_thread(self.project_indexer.build_index, project)
            self.current_index = project_index
            self.index_store.save(project_index)
            self.refresh_search()
            self.notify(f"Indexed {len(project_index.items)} items.")
        except Exception as exc:  # pragma: no cover - defensive UI guard
            self.notify(f"Indexing failed: {exc}")
        finally:
            self.is_reindexing = False
            self.refresh_view()

    def set_query(self, query: str) -> None:
        self.search_controller.set_query(query)
        self.settings.last_query = query
        self.settings_controller.persist()
        self.refresh_search()

    def set_active_project(self, project_id: str | None) -> None:
        self.project_controller.set_active(project_id)
        self.settings.selected_project_id = project_id
        self.settings_controller.persist()
        self.load_current_index()
        self.refresh_search()
        self.refresh_view()

    def save_project(self, project: Project) -> None:
        self.project_controller.upsert(project)
        self.project_controller.set_active(project.id)
        self.settings.selected_project_id = project.id
        self.settings_controller.persist()
        self.load_current_index()
        self.refresh_search()

    def delete_project(self, project_id: str) -> None:
        self.index_store.delete(project_id)
        active = self.project_controller.delete(project_id)
        self.settings.selected_project_id = active.id if active else None
        self.settings_controller.persist()
        self.load_current_index()
        self.refresh_search()
        self.refresh_view()

    def update_settings(self, **changes) -> None:
        self.settings_controller.update(**changes)
        self.refresh_search()

    def move_selection(self, delta: int) -> None:
        self.search_controller.move_selection(delta)
        self.refresh_view()

    def select_index(self, index: int) -> None:
        self.search_controller.select_index(index)
        self.refresh_view()

    def open_selected(self) -> None:
        result = self.selected_result
        if result:
            self.open_result(result)

    def open_result(self, result: SearchResult) -> None:
        project = self.current_project
        if not project:
            self.notify("No active project selected.")
            return
        open_result = self.opener.open_item(project, result.item)
        if open_result.success:
            self._record_open(result)
            self.notify(open_result.message)
        else:
            self.notify(open_result.message)
        self.refresh_search()
        self.refresh_view()

    def _record_query(self) -> None:
        query = self.search_controller.query.strip()
        if not query:
            return
        for entry in self.history.recent_queries:
            if entry.query == query:
                entry.count += 1
                entry.last_used_at = self._now()
                break
        else:
            self.history.recent_queries.insert(0, QueryHistoryEntry(query=query))
        self.history.recent_queries.sort(key=lambda item: (-item.count, item.query.lower()))
        self.history.recent_queries = self.history.recent_queries[:30]
        self.history_store.save(self.history)

    def _record_open(self, result: SearchResult) -> None:
        self._record_query()
        for entry in self.history.recent_opens:
            if entry.item_key == result.item.item_key:
                entry.count += 1
                entry.opened_at = self._now()
                break
        else:
            self.history.recent_opens.insert(
                0,
                RecentOpenEntry(
                    item_key=result.item.item_key,
                    project_id=result.item.project_id,
                    display_name=result.item.display_name,
                    relative_path=result.item.relative_path,
                    item_type=result.item.item_type,
                    line=result.item.line,
                ),
            )
        self.history.recent_opens.sort(key=lambda item: item.opened_at, reverse=True)
        self.history.recent_opens = self.history.recent_opens[:60]
        self.history_store.save(self.history)

    def update_window_geometry(self, width: int, height: int, left: int, top: int) -> None:
        self.settings_controller.set_geometry(width=width, height=height, left=left, top=top)

    def reset_geometry(self):
        return self.settings_controller.reset_geometry()

    def notify(self, message: str) -> None:
        if self.view:
            self.view.show_message(message)

    def refresh_view(self) -> None:
        if self.view:
            self.view.refresh()

    def _now(self) -> str:
        return datetime.utcnow().replace(microsecond=0).isoformat()

