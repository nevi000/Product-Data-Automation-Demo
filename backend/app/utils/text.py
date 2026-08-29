"""Small text helpers used by adapters and normalization."""

from __future__ import annotations

import re

_SLUG_STRIP = re.compile(r"[^a-z0-9]+")
_WS = re.compile(r"\s+")


def slugify(value: str, sep: str = "_") -> str:
    """Lowercase, collapse non-alphanumerics to `sep`, trim `sep` from the ends."""
    out = _SLUG_STRIP.sub(sep, value.strip().lower())
    return out.strip(sep)


def titleize(value: str) -> str:
    """Title-case but keep short connectors lowercase — good enough for names.

    Capitalizes each hyphen-separated part ("half-zip" -> "Half-Zip").
    """
    small = {"and", "of", "the", "for", "with", "in", "on"}

    def cap(word: str) -> str:
        return "-".join(p[:1].upper() + p[1:].lower() for p in word.split("-"))

    words = _WS.sub(" ", value.strip()).split(" ")
    return " ".join(
        cap(w) if i == 0 or w.lower() not in small else w.lower()
        for i, w in enumerate(words)
    )


def parse_sizes(value: str) -> list[str]:
    """Split a size string like ``"S, M, L"`` or ``"36 38 40"`` into a list."""
    if not value:
        return []
    return [s for s in re.split(r"[\s,;/]+", value.strip()) if s]


def clean_number(value: str) -> str:
    """Normalize a European-formatted number string to a dot-decimal string."""
    v = value.strip().replace(" ", "")
    if "," in v and "." in v:
        v = v.replace(".", "").replace(",", ".")
    elif "," in v:
        v = v.replace(",", ".")
    return v
