from __future__ import annotations

import re

from .core import Chunk, Segment


def _split_long_paragraph(text: str, max_chars: int) -> list[str]:
    if len(text) <= max_chars:
        return [text]
    sentences = re.split(r"(?<=[.!?؟])\s+", text)
    parts: list[str] = []
    current = ""
    for sentence in sentences:
        if not sentence:
            continue
        if len(current) + len(sentence) + 1 <= max_chars:
            current = f"{current} {sentence}".strip()
        else:
            if current:
                parts.append(current)
            if len(sentence) <= max_chars:
                current = sentence
            else:
                for i in range(0, len(sentence), max_chars):
                    parts.append(sentence[i : i + max_chars])
                current = ""
    if current:
        parts.append(current)
    return parts


def chunk_segments(
    segments: list[Segment],
    target_chars: int = 1800,
    overlap_chars: int = 220,
) -> list[Chunk]:
    chunks: list[Chunk] = []
    idx = 0

    for segment in segments:
        paragraphs = [p.strip() for p in re.split(r"\n\s*\n|\n", segment.text) if p.strip()]
        units: list[str] = []
        for p in paragraphs:
            units.extend(_split_long_paragraph(p, target_chars))

        current = ""
        for unit in units:
            candidate = f"{current}\n\n{unit}".strip() if current else unit
            if len(candidate) <= target_chars:
                current = candidate
                continue

            if current:
                chunks.append(Chunk(chunk_index=idx, text=current, locator=segment.locator))
                idx += 1
                tail = current[-overlap_chars:].strip() if overlap_chars else ""
                current = f"{tail}\n\n{unit}".strip() if tail else unit
            else:
                chunks.append(Chunk(chunk_index=idx, text=unit, locator=segment.locator))
                idx += 1
                current = ""

        if current:
            chunks.append(Chunk(chunk_index=idx, text=current, locator=segment.locator))
            idx += 1

    return chunks
