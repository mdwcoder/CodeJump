from __future__ import annotations

from codejump.core.models import HistoryState, Project, ProjectIndex, SearchResult
from codejump.core.search_engine import SearchEngine


class SearchController:
    def __init__(self, search_engine: SearchEngine) -> None:
        self.search_engine = search_engine
        self.query = ""
        self.results: list[SearchResult] = []
        self.selected_index = 0

    @property
    def selected_result(self) -> SearchResult | None:
        if not self.results:
            return None
        if self.selected_index < 0 or self.selected_index >= len(self.results):
            self.selected_index = 0
        return self.results[self.selected_index]

    def run_search(
        self,
        project: Project | None,
        project_index: ProjectIndex | None,
        history: HistoryState,
        limit: int,
    ) -> list[SearchResult]:
        self.results = self.search_engine.search(
            project=project,
            project_index=project_index,
            query=self.query,
            history=history,
            limit=limit,
        )
        if self.selected_index >= len(self.results):
            self.selected_index = max(0, len(self.results) - 1)
        return self.results

    def set_query(self, query: str) -> None:
        self.query = query
        self.selected_index = 0

    def move_selection(self, delta: int) -> SearchResult | None:
        if not self.results:
            return None
        self.selected_index = max(0, min(len(self.results) - 1, self.selected_index + delta))
        return self.selected_result

    def select_index(self, index: int) -> SearchResult | None:
        if not self.results:
            return None
        self.selected_index = max(0, min(len(self.results) - 1, index))
        return self.selected_result

