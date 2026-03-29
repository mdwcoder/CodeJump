from __future__ import annotations

from codejump.core.models import HistoryState, MatchExplanation, Project, ProjectIndex, SearchResult
from codejump.core.scorer import score_item
from codejump.core.tokenizer import tokenize


class SearchEngine:
    def search(
        self,
        project: Project | None,
        project_index: ProjectIndex | None,
        query: str,
        history: HistoryState,
        limit: int,
    ) -> list[SearchResult]:
        if not project or not project_index:
            return []

        normalized_query = query.strip()
        if not normalized_query:
            return self._recent_results(project_index, history, limit)

        query_tokens = tokenize(normalized_query)
        if not query_tokens:
            return []

        results: list[SearchResult] = []
        for item in project_index.items:
            explanation = score_item(
                query=normalized_query,
                query_tokens=query_tokens,
                item=item,
                history=history,
                preferred_extensions=project.priority_extensions,
            )
            if explanation is None:
                continue
            results.append(SearchResult(item=item, score=explanation.score, explanation=explanation))

        results.sort(
            key=lambda result: (
                -result.score,
                len(result.item.relative_path),
                result.item.display_name.lower(),
            )
        )
        return results[:limit]

    def _recent_results(
        self,
        project_index: ProjectIndex,
        history: HistoryState,
        limit: int,
    ) -> list[SearchResult]:
        by_key = {item.item_key: item for item in project_index.items}
        results: list[SearchResult] = []
        for recent in history.recent_opens:
            item = by_key.get(recent.item_key)
            if not item:
                continue
            results.append(
                SearchResult(
                    item=item,
                    score=10.0 + recent.count,
                    explanation=MatchExplanation(
                        matched_tokens=[],
                        reasons=[f"recent open x{recent.count}", item.item_type.value],
                        score=10.0 + recent.count,
                    ),
                )
            )
            if len(results) >= limit:
                break
        return results
