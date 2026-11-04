"""Parse ClinicalTrials.gov eligibility criteria into inclusion / exclusion blocks."""

from __future__ import annotations

import re

_INCLUSION_HEADER = re.compile(
    r"(?:^|\n)\s*"
    r"(?:(?:general|additional|key|patient|provider|subject|participant)\s+)*"
    r"inclusion\s+criteria\s*:?",
    re.IGNORECASE | re.MULTILINE,
)

_EXCLUSION_HEADER = re.compile(
    r"\b"
    r"(?:(?:general|additional|key|patient|provider|subject|participant)\s+)*"
    r"exclusion\s+criteria\b"
    r"\s*:?",
    re.IGNORECASE,
)


def _slice_before_next_header(remainder: str) -> str:
    end = len(remainder)
    for pattern in (_EXCLUSION_HEADER, _INCLUSION_HEADER):
        nxt = pattern.search(remainder)
        if nxt and nxt.start() < end:
            end = nxt.start()
    return remainder[:end].strip()


def extract_inclusion_blocks(eligibility_criteria: str | None) -> list[str]:
    """Text under each Inclusion Criteria header until the next Exclusion/Inclusion header."""
    text = (eligibility_criteria or "").strip()
    if not text:
        return []

    blocks: list[str] = []
    for incl in _INCLUSION_HEADER.finditer(text):
        block = _slice_before_next_header(text[incl.end() :])
        if block:
            blocks.append(block)

    if blocks:
        return blocks

    first_excl = _EXCLUSION_HEADER.search(text)
    if first_excl:
        prefix = text[: first_excl.start()].strip()
        if prefix:
            return [prefix]
    return [text] if text else []


def extract_exclusion_blocks(eligibility_criteria: str | None) -> list[str]:
    """Text under each Exclusion Criteria header until the next Inclusion/Exclusion header."""
    text = (eligibility_criteria or "").strip()
    if not text:
        return []

    blocks: list[str] = []
    for excl in _EXCLUSION_HEADER.finditer(text):
        block = _slice_before_next_header(text[excl.end() :])
        if block:
            blocks.append(block)
    return blocks


def split_inclusion_exclusion_eligibility(eligibility_criteria: str | None) -> tuple[str, str]:
    text = (eligibility_criteria or "").strip()
    if not text:
        return "", ""
    blocks = extract_inclusion_blocks(text)
    inclusion = "\n\n".join(blocks)
    first_excl = _EXCLUSION_HEADER.search(text)
    exclusion = text[first_excl.start() :].strip() if first_excl else ""
    return inclusion, exclusion
