from __future__ import annotations

import re


CAMEL_CASE_PATTERN = re.compile(r"([a-z0-9])([A-Z])")
TOKEN_SPLIT_PATTERN = re.compile(r"[^a-z0-9]+")


def _normalize_separators(value: str) -> str:
    value = CAMEL_CASE_PATTERN.sub(r"\1 \2", value)
    value = value.replace("\\", "/")
    value = value.replace("/", " ")
    value = value.replace("_", " ")
    value = value.replace("-", " ")
    value = value.replace(".", " ")
    return value.lower()


def tokenize(value: str) -> list[str]:
    normalized = _normalize_separators(value)
    tokens = [token for token in TOKEN_SPLIT_PATTERN.split(normalized) if token]
    return tokens


def normalize_text(value: str) -> str:
    return " ".join(tokenize(value))


def unique_tokens(value: str) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for token in tokenize(value):
        if token not in seen:
            seen.add(token)
            ordered.append(token)
    return ordered


def ordered_token_match(query_tokens: list[str], candidate_tokens: list[str]) -> bool:
    if not query_tokens or not candidate_tokens:
        return False
    current_index = 0
    for token in candidate_tokens:
        if token == query_tokens[current_index]:
            current_index += 1
            if current_index == len(query_tokens):
                return True
    return False

