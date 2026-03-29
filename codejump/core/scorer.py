from __future__ import annotations

from dataclasses import dataclass, field
from difflib import SequenceMatcher

from codejump.core.enums import ItemType
from codejump.core.models import HistoryState, IndexItem, MatchExplanation
from codejump.core.tokenizer import normalize_text, ordered_token_match


TYPE_BOOSTS = {
    ItemType.SYMBOL: 14.0,
    ItemType.FILE: 10.0,
    ItemType.FOLDER: 6.0,
}


@dataclass(slots=True)
class ScoreDetail:
    total: float = 0.0
    matched_tokens: list[str] = field(default_factory=list)
    reasons: list[str] = field(default_factory=list)

    def add(self, value: float, reason: str | None = None, token: str | None = None) -> None:
        self.total += value
        if reason:
            self.reasons.append(reason)
        if token and token not in self.matched_tokens:
            self.matched_tokens.append(token)

    def explanation(self) -> MatchExplanation:
        return MatchExplanation(
            matched_tokens=self.matched_tokens,
            reasons=self.reasons,
            score=round(self.total, 2),
        )


def score_item(
    query: str,
    query_tokens: list[str],
    item: IndexItem,
    history: HistoryState,
    preferred_extensions: list[str] | None = None,
) -> MatchExplanation | None:
    if not query_tokens:
        return None

    preferred_extensions = preferred_extensions or []
    detail = ScoreDetail()
    normalized_query = normalize_text(query)
    normalized_name = normalize_text(item.display_name)
    normalized_path = normalize_text(item.relative_path)
    name_matches = _score_token_group(query_tokens, item.name_tokens, 22.0, 16.0, detail, "name")
    path_matches = _score_token_group(query_tokens, item.path_tokens, 10.0, 7.0, detail, "path")
    preview_matches = _score_token_group(query_tokens, item.preview_tokens, 6.0, 4.0, detail, "preview")

    if normalized_query == normalized_name:
        detail.add(240.0 if item.item_type == ItemType.FILE else 220.0, "exact name match")
    elif normalized_query and normalized_query in normalized_name:
        detail.add(38.0, "query phrase in name")

    if normalized_query and normalized_query in normalized_path:
        detail.add(28.0, "query phrase in path")

    if name_matches == len(query_tokens):
        detail.add(48.0, "all query tokens in name")
    elif name_matches + path_matches == len(query_tokens):
        detail.add(26.0, "all query tokens covered")

    combined_tokens = item.name_tokens + item.path_tokens
    has_ordered_match = ordered_token_match(query_tokens, combined_tokens)
    if has_ordered_match:
        detail.add(18.0, "ordered token match")

    recency_boost = _recency_boost(item, history)
    short_path_bonus = _short_path_bonus(item.relative_path)
    query_history_boost = _query_history_boost(query, history)
    detail.add(TYPE_BOOSTS[item.item_type], f"{item.item_type.value} boost")
    detail.add(recency_boost, "recently opened" if recency_boost else None)
    detail.add(short_path_bonus, "short path" if short_path_bonus else None)
    if has_ordered_match or name_matches == len(query_tokens):
        detail.add(query_history_boost, "frequent query" if query_history_boost else None)

    if item.extension and item.extension in preferred_extensions:
        detail.add(14.0, "preferred extension")

    coverage = len(detail.matched_tokens) / max(1, len(query_tokens))
    if coverage < 0.5:
        detail.add(-24.0, "weak coverage penalty")
    elif preview_matches == 0 and name_matches == 0 and path_matches <= 1:
        detail.add(-12.0, "no strong lexical anchor")

    if detail.total < 20 or not detail.matched_tokens:
        return None
    return detail.explanation()


def _score_token_group(
    query_tokens: list[str],
    candidate_tokens: list[str],
    exact_weight: float,
    fuzzy_weight: float,
    detail: ScoreDetail,
    label: str,
) -> int:
    if not candidate_tokens:
        return 0
    matches = 0
    for query_token in query_tokens:
        strength = _best_token_strength(query_token, candidate_tokens)
        if strength <= 0:
            continue
        matches += 1
        weight = exact_weight if strength >= 1.0 else fuzzy_weight * strength
        detail.add(weight, f"{label} token match", query_token)
    return matches


def _best_token_strength(query_token: str, candidate_tokens: list[str]) -> float:
    best = 0.0
    for candidate in candidate_tokens:
        if candidate == query_token:
            return 1.0
        if candidate.startswith(query_token) or query_token.startswith(candidate):
            best = max(best, 0.82)
            continue
        if query_token in candidate or candidate in query_token:
            best = max(best, 0.7)
            continue
        ratio = SequenceMatcher(a=query_token, b=candidate).ratio()
        if ratio >= 0.86:
            best = max(best, 0.58)
    return best


def _recency_boost(item: IndexItem, history: HistoryState) -> float:
    for entry in history.recent_opens:
        if entry.item_key == item.item_key:
            return min(12.0, 3.0 * entry.count)
    return 0.0


def _short_path_bonus(relative_path: str) -> float:
    depth = relative_path.count("/")
    return max(0.0, 6.0 - (depth * 1.2))


def _query_history_boost(query: str, history: HistoryState) -> float:
    normalized_query = query.strip().lower()
    for entry in history.recent_queries:
        if entry.query.strip().lower() == normalized_query:
            return min(4.0, 0.5 * entry.count)
    return 0.0
