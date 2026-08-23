"""Exploratory feature extraction from primary outcome text."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

# Tokens that look like acronyms but are not instruments.
ACRONYM_STOPWORDS = {
    "OR",
    "AND",
    "THE",
    "WITH",
    "FROM",
    "BASELINE",
    "POST",
    "WEEK",
    "WEEKS",
    "T1",
    "T2",
    "T3",
    "T4",
    "USA",
    "MRI",
    "EEG",
    "HRV",
    "RMSSD",
    "PGI",
}


@dataclass
class OutcomeFeatures:
    instruments_detected: list[str]
    acronyms_detected: list[str]
    keywords_matched: list[str]
    phrases_matched: list[str]
    action_verbs_matched: list[str]


def _dedupe(items: list[str]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for item in items:
        key = item.lower()
        if key not in seen:
            seen.add(key)
            ordered.append(item)
    return ordered


def _combined_text(measure: str | None, description: str | None, time_frame: str | None) -> str:
    parts = [measure or "", description or "", time_frame or ""]
    return "\n".join(part for part in parts if part)


def _alias_match_pattern(alias: str) -> re.Pattern[str]:
    """Build a controlled matcher for an instrument alias.

    Short acronyms require word boundaries to avoid substring false positives
    (e.g. 'isi' inside 'visible'). Multi-word names require exact phrase match.
    """
    alias = alias.strip().lower()
    escaped = re.escape(alias)
    if re.search(r"\s", alias):
        return re.compile(rf"(?<![a-z0-9]){escaped}(?![a-z0-9])", re.IGNORECASE)
    if re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)?", alias):
        return re.compile(rf"\b{escaped}\b", re.IGNORECASE)
    return re.compile(rf"(?<![a-z0-9]){escaped}(?![a-z0-9])", re.IGNORECASE)


def extract_acronyms(text: str) -> list[str]:
    found: list[str] = []
    for match in re.finditer(r"\(([A-Z][A-Z0-9-]{1,15})\)", text):
        found.append(match.group(1))
    for match in re.finditer(r"\b([A-Z]{2,}(?:-[0-9]{1,3})?)\b", text):
        token = match.group(1)
        if token in ACRONYM_STOPWORDS:
            continue
        found.append(token)
    return _dedupe(found)


def extract_instruments(text: str, lexicon: dict[str, Any]) -> list[str]:
    found: list[str] = []
    for item in lexicon.get("instruments", []):
        aliases = [item["name"], *item.get("aliases", [])]
        patterns = [_alias_match_pattern(alias) for alias in aliases]
        if any(pattern.search(text) for pattern in patterns):
            found.append(item["name"])
    return _dedupe(found)


def extract_terms(text: str, terms: list[str]) -> list[str]:
    lowered = text.lower()
    matched: list[str] = []
    for term in terms:
        if re.search(rf"\b{re.escape(term.lower())}\b", lowered):
            matched.append(term)
    return matched


def extract_phrases(text: str, phrases: list[str]) -> list[str]:
    lowered = text.lower()
    matched: list[str] = []
    for phrase in phrases:
        if phrase.lower() in lowered:
            matched.append(phrase)
    return matched


def extract_outcome_features(
    measure: str | None,
    description: str | None,
    time_frame: str | None,
    lexicon: dict[str, Any],
) -> OutcomeFeatures:
    text = _combined_text(measure, description, time_frame)
    return OutcomeFeatures(
        instruments_detected=extract_instruments(text, lexicon),
        acronyms_detected=extract_acronyms(text),
        keywords_matched=extract_terms(text, lexicon.get("keywords", [])),
        phrases_matched=extract_phrases(text, lexicon.get("phrases", [])),
        action_verbs_matched=extract_terms(text, lexicon.get("action_verbs", [])),
    )
