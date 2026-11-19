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


# --- Pain-duration sentence (descriptive column; never used to include / exclude) ---------------

_NUM_WORD = (
    r"(?:\d+(?:\.\d+)?|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|"
    r"fifteen|twenty|twenty-four)"
)
_TIME_EXPR = re.compile(
    rf"\b{_NUM_WORD}\s*(?:-|–|to|or more|\+)?\s*(?:{_NUM_WORD}\s*)?"
    r"(?:days?|weeks?|wks?|months?|mos?|years?|yrs?)\b"
    rf"|\b{_NUM_WORD}\s*(?:or more\s+)?(?:headaches?|attacks?|migraine(?:s)?|days?)\s*(?:per|/|a)\s*month"
    rf"|\b{_NUM_WORD}\s*(?:to|-)\s*{_NUM_WORD}\s*(?:headaches?|attacks?|days?)\s*(?:per|/|a)\s*month",
    re.IGNORECASE,
)
_PAIN_CONTEXT = re.compile(
    r"pain|headache|migraine|ache\b|fibromyalgia|symptoms?|\bLBP\b|\bCLBP\b|\bFM\b|"
    r"attacks?|complaints?|condition|disorder|diagnos|cronic",
    re.IGNORECASE,
)
_DURATION_WORDING = re.compile(
    r"persist|chronic|cronic|duration|lasting|last(?:ed|s)?\b|longer than|more than|greater than|"
    r"at least|≥|>=|>|\bover\b|since|history of|present for|for (?:at least|more than|over|the past)|"
    r"onset|for \d|for (?:one|two|three|four|five|six|twelve)|less than|<|within|"
    r"recurrent|episodes?|per month|/month|a month|frequency|days? (?:per|a|/)|attacks? (?:per|a|/)|of duration|"
    r"months? of |weeks? of ",
    re.IGNORECASE,
)
_NOT_PAIN_DURATION = re.compile(
    # Age alone (reject only when there is no pain/duration cue besides the age phrase).
    r"^(?=.*\b(?:years?|yrs?)\s*(?:old|of age)\b)(?!.*(?:pain|headache|migraine|LBP|CLBP|fibromyalgia|cronic)).*$|"
    r"stable (?:dose|regimen|medication)|medication regimen|"
    r"no (?:new|change)|previous \d|past \d+ (?:days?|weeks?|months?) .{0,40}(?:surgery|injection|treatment|therapy)|"
    r"attend .{0,40}(?:session|week)|willingness .{0,60}(?:week|month)|intervention .{0,20}week|"
    r"medications? for the (?:last|past|next)|on their current .{0,40}medication",
    re.IGNORECASE,
)


def _clean_sentence(text: str) -> str:
    text = re.sub(r"\\([<>])", r"\1", text)  # registry text escapes < and > as \< and \>
    return re.sub(r"\s+", " ", text).strip(" *-•\t")


def _candidate_chunks(block: str) -> list[str]:
    """Bullet lines and sentence-like fragments from one inclusion block."""
    chunks: list[str] = []
    # Numbered / nested criteria often put the time window on its own indented line.
    # Join a short indented continuation onto the previous non-empty line.
    joined_lines: list[str] = []
    for raw in block.splitlines():
        if re.match(r"^\s{2,}|^\t", raw) and joined_lines and len(raw.strip()) < 120:
            joined_lines[-1] = joined_lines[-1].rstrip(",;") + " " + raw.strip()
        else:
            joined_lines.append(raw)
    for line in joined_lines:
        for piece in re.split(r"(?<=[.;])\s+(?=[A-Z0-9(])|\n+", line):
            cleaned = _clean_sentence(piece)
            if cleaned:
                chunks.append(cleaned)
    return chunks


def _trim_to_duration_clause(cleaned: str) -> str:
    """Keep the pain-duration clause when several criteria were jammed into one line."""
    for stop in (
        r"\bAbility to\b",
        r"\bWilling(?:ness)?\b",
        r"\bAble to\b",
        r"\bEnglish\b",
        r"\bConsent\b",
        r"\bAge\b",
        r"\bVeteran\b",
    ):
        m = re.search(stop, cleaned)
        if m and m.start() > 20:
            cleaned = cleaned[: m.start()].rstrip(" ,;")
            break
    return cleaned


def find_chronic_inclusion_cue(
    eligibility_criteria: str | None,
    *,
    word_patterns: list[str],
    duration_patterns: list[str],
) -> str:
    """First chronic cue in the INCLUSION criteria, or "" when none.

    - `word_patterns` (e.g. the word "chronic") are searched in the whole inclusion text.
    - `duration_patterns` (e.g. "at least 3 months") must sit in an inclusion sentence that
      also mentions pain/symptoms, so "surgery at least 3 months ago" alone does not count.
    """
    words = [re.compile(p, re.IGNORECASE) for p in word_patterns]
    durations = [re.compile(p, re.IGNORECASE) for p in duration_patterns]
    for block in extract_inclusion_blocks(eligibility_criteria):
        cleaned_block = _clean_sentence(block)
        for pattern in words:
            match = pattern.search(cleaned_block)
            if match:
                return match.group(0)
        for chunk in _candidate_chunks(block):
            if not _PAIN_CONTEXT.search(chunk):
                continue
            for pattern in durations:
                match = pattern.search(chunk)
                if match:
                    return match.group(0)
    return ""


_NUMBER_WORDS = {
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6,
    "seven": 7, "eight": 8, "nine": 9, "ten": 10, "eleven": 11, "twelve": 12,
}
_WEEK_NUM = r"(\d+(?:\.\d+)?|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve)"
_WEEK_PHRASE = re.compile(
    rf"\b{_WEEK_NUM}\s*(?:(?:-|–|to|or|and)\s*{_WEEK_NUM}\s*)?(?:weeks?|wks?)\b",
    re.IGNORECASE,
)


def _week_value(token: str) -> float:
    lowered = token.lower()
    return float(_NUMBER_WORDS[lowered]) if lowered in _NUMBER_WORDS else float(lowered)


def find_short_pain_window(eligibility_criteria: str | None, spec: dict) -> str:
    """First inclusion sentence stating a pain/symptom window of <= `spec["max_weeks"]` weeks, or "".

    The sentence must mention pain/symptoms and a number of weeks (ranges use every bound).
    Sentences about medication stability, surgery, injections etc. are skipped, and so are
    rating look-backs ("pain score >= 4 over the past 2 weeks"). Patterns come from the YAML.
    """
    skip = [re.compile(p, re.IGNORECASE) for p in spec["skip_patterns"]]
    for block in extract_inclusion_blocks(eligibility_criteria):
        for chunk in _candidate_chunks(block):
            if not re.search(spec["pain_pattern"], chunk, re.IGNORECASE) or any(p.search(chunk) for p in skip):
                continue
            is_rating = re.search(spec["rating_pattern"], chunk, re.IGNORECASE)
            for match in _WEEK_PHRASE.finditer(chunk):
                look_back = re.search(
                    spec["lookback_before"], chunk[max(0, match.start() - 12) : match.start()], re.IGNORECASE
                ) or re.match(spec["lookback_after"], chunk[match.end() :], re.IGNORECASE)
                if is_rating and look_back:
                    continue
                if any(_week_value(g) <= spec["max_weeks"] for g in match.groups() if g):
                    return chunk
    return ""


def extract_pain_duration_sentences(eligibility_criteria: str | None, *, max_sentences: int = 2) -> list[str]:
    """Verbatim inclusion-criteria sentences that state how long the pain/condition lasts."""
    found: list[str] = []
    for block in extract_inclusion_blocks(eligibility_criteria):
        for cleaned in _candidate_chunks(block):
            if len(cleaned) > 400:
                continue
            if (
                _TIME_EXPR.search(cleaned)
                and _PAIN_CONTEXT.search(cleaned)
                and _DURATION_WORDING.search(cleaned)
                and not _NOT_PAIN_DURATION.search(cleaned)
            ):
                cleaned = _trim_to_duration_clause(cleaned)
                if cleaned and cleaned not in found:
                    found.append(cleaned)
            if len(found) >= max_sentences:
                return found
    return found
