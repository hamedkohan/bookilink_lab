from __future__ import annotations

from collections import OrderedDict

from .llm import LLMProvider
from .prompts import (
    debate_instructions,
    debate_prompt,
    dna_instructions,
    dna_prompt,
    talk_instructions,
    talk_prompt,
)
from .store import BookStore


def _format_hits(hits, prefix: str = "S") -> tuple[str, list[dict]]:
    blocks = []
    sources = []
    for i, hit in enumerate(hits, start=1):
        label = f"{prefix}{i}"
        blocks.append(f"[{label}] ({hit.locator})\n{hit.text}")
        sources.append(
            {
                "label": label,
                "locator": hit.locator,
                "score": hit.score,
                "text": hit.text,
            }
        )
    return "\n\n---\n\n".join(blocks), sources


def answer_book_question(
    store: BookStore,
    llm: LLMProvider,
    book_id: str,
    question: str,
    language: str,
    mode: str,
    history: list[dict] | None = None,
):
    qvec = llm.embed([question])[0]
    hits = store.search_by_vector(book_id, qvec, top_k=8)
    context, sources = _format_hits(hits)
    history_text = ""
    if history:
        compact = history[-6:]
        history_text = "\n".join(f"{m['role']}: {m['content']}" for m in compact)
    answer = llm.generate(
        talk_instructions(language, mode),
        talk_prompt(question, context, history_text),
        reasoning_effort="low",
    )
    return answer, sources


def generate_book_dna(store: BookStore, llm: LLMProvider, book_id: str, language: str):
    probes = [
        "the core thesis and central argument of the book",
        "the author's recurring fundamental beliefs and premises",
        "the main problem, enemy, or worldview the book argues against",
        "hidden assumptions required for the argument to work",
        "the strongest evidence, reasoning, or example supporting the thesis",
        "weaknesses limitations overclaims counterexamples and vulnerable arguments",
        "tensions contradictions tradeoffs or unresolved conflicts in the book",
        "repeated concepts motifs ideas and patterns across the book",
        "the most important durable takeaways",
        "open questions and issues the book does not fully resolve",
    ]
    qvecs = llm.embed(probes)

    unique = OrderedDict()
    for vec in qvecs:
        for hit in store.search_by_vector(book_id, vec, top_k=4):
            unique.setdefault(hit.chunk_index, hit)

    all_chunks = store.get_chunks(book_id)
    by_index = {h.chunk_index: h for h in unique.values()}
    if all_chunks:
        from .core import SearchHit
        for raw in (all_chunks[:2] + all_chunks[-2:]):
            if raw["chunk_index"] not in by_index:
                by_index[raw["chunk_index"]] = SearchHit(
                    chunk_index=raw["chunk_index"],
                    text=raw["text"],
                    locator=raw["locator"],
                    score=0.0,
                )

    retrieved = list(unique.values())[:30]
    selected_map = OrderedDict((h.chunk_index, h) for h in retrieved)
    if all_chunks:
        from .core import SearchHit
        for raw in (all_chunks[:2] + all_chunks[-2:]):
            selected_map.setdefault(
                raw["chunk_index"],
                SearchHit(
                    chunk_index=raw["chunk_index"],
                    text=raw["text"],
                    locator=raw["locator"],
                    score=0.0,
                ),
            )
    selected = list(selected_map.values())[:34]
    context, sources = _format_hits(selected)
    answer = llm.generate(
        dna_instructions(language),
        dna_prompt(context),
        reasoning_effort="medium",
    )
    return answer, sources


def debate_books(
    store: BookStore,
    llm: LLMProvider,
    book_a_id: str,
    book_b_id: str,
    question: str,
    language: str,
):
    qvec = llm.embed([question])[0]
    hits_a = store.search_by_vector(book_a_id, qvec, top_k=7)
    hits_b = store.search_by_vector(book_b_id, qvec, top_k=7)
    context_a, sources_a = _format_hits(hits_a, prefix="A")
    context_b, sources_b = _format_hits(hits_b, prefix="B")
    book_a = store.get_book(book_a_id)
    book_b = store.get_book(book_b_id)
    answer = llm.generate(
        debate_instructions(language),
        debate_prompt(
            question,
            book_a["title"] if book_a else "Book A",
            context_a,
            book_b["title"] if book_b else "Book B",
            context_b,
        ),
        reasoning_effort="medium",
    )
    return answer, sources_a + sources_b
