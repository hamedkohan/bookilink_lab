from dataclasses import dataclass
from typing import Optional


@dataclass
class Segment:
    text: str
    locator: str
    order_index: int


@dataclass
class ParsedBook:
    title: str
    author: Optional[str]
    file_type: str
    segments: list[Segment]


@dataclass
class Chunk:
    chunk_index: int
    text: str
    locator: str


@dataclass
class SearchHit:
    chunk_index: int
    text: str
    locator: str
    score: float
