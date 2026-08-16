from __future__ import annotations

import hashlib
import json
import sqlite3
from pathlib import Path

import numpy as np

from .core import Chunk, SearchHit


class BookStore:
    def __init__(self, db_path: str):
        self.db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _connect(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        with self._connect() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS books (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    author TEXT,
                    filename TEXT NOT NULL,
                    file_type TEXT NOT NULL,
                    file_hash TEXT NOT NULL,
                    chunk_count INTEGER NOT NULL DEFAULT 0,
                    metadata_json TEXT NOT NULL DEFAULT '{}',
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                );
                CREATE TABLE IF NOT EXISTS chunks (
                    book_id TEXT NOT NULL,
                    chunk_index INTEGER NOT NULL,
                    locator TEXT NOT NULL,
                    text TEXT NOT NULL,
                    embedding BLOB NOT NULL,
                    embedding_dim INTEGER NOT NULL,
                    PRIMARY KEY (book_id, chunk_index),
                    FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE
                );
                CREATE INDEX IF NOT EXISTS idx_chunks_book ON chunks(book_id);
                """
            )

    @staticmethod
    def make_book_id(file_bytes: bytes) -> tuple[str, str]:
        digest = hashlib.sha256(file_bytes).hexdigest()
        return digest[:20], digest

    def has_book(self, book_id: str) -> bool:
        with self._connect() as conn:
            row = conn.execute("SELECT chunk_count FROM books WHERE id=?", (book_id,)).fetchone()
            return bool(row and row["chunk_count"] > 0)

    def save_book(
        self,
        *,
        book_id: str,
        title: str,
        author: str | None,
        filename: str,
        file_type: str,
        file_hash: str,
        chunks: list[Chunk],
        embeddings: list[list[float]],
        metadata: dict | None = None,
    ) -> None:
        if len(chunks) != len(embeddings):
            raise ValueError("Chunks and embeddings length mismatch")

        with self._connect() as conn:
            conn.execute("DELETE FROM chunks WHERE book_id=?", (book_id,))
            conn.execute(
                """
                INSERT INTO books(id,title,author,filename,file_type,file_hash,chunk_count,metadata_json)
                VALUES(?,?,?,?,?,?,?,?)
                ON CONFLICT(id) DO UPDATE SET
                  title=excluded.title,
                  author=excluded.author,
                  filename=excluded.filename,
                  file_type=excluded.file_type,
                  file_hash=excluded.file_hash,
                  chunk_count=excluded.chunk_count,
                  metadata_json=excluded.metadata_json
                """,
                (
                    book_id,
                    title,
                    author,
                    filename,
                    file_type,
                    file_hash,
                    len(chunks),
                    json.dumps(metadata or {}, ensure_ascii=False),
                ),
            )
            for chunk, emb in zip(chunks, embeddings):
                arr = np.asarray(emb, dtype=np.float32)
                conn.execute(
                    """INSERT INTO chunks(book_id,chunk_index,locator,text,embedding,embedding_dim)
                       VALUES(?,?,?,?,?,?)""",
                    (book_id, chunk.chunk_index, chunk.locator, chunk.text, arr.tobytes(), arr.size),
                )

    def list_books(self) -> list[dict]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT id,title,author,filename,file_type,chunk_count,created_at FROM books ORDER BY created_at DESC"
            ).fetchall()
        return [dict(r) for r in rows]

    def get_book(self, book_id: str) -> dict | None:
        with self._connect() as conn:
            row = conn.execute("SELECT * FROM books WHERE id=?", (book_id,)).fetchone()
        return dict(row) if row else None

    def get_chunks(self, book_id: str) -> list[dict]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT chunk_index,locator,text FROM chunks WHERE book_id=? ORDER BY chunk_index",
                (book_id,),
            ).fetchall()
        return [dict(r) for r in rows]

    def search_by_vector(self, book_id: str, query_embedding: list[float], top_k: int = 7) -> list[SearchHit]:
        q = np.asarray(query_embedding, dtype=np.float32)
        q_norm = np.linalg.norm(q)
        if q_norm == 0:
            return []
        q = q / q_norm

        with self._connect() as conn:
            rows = conn.execute(
                "SELECT chunk_index,locator,text,embedding,embedding_dim FROM chunks WHERE book_id=?",
                (book_id,),
            ).fetchall()

        scored: list[SearchHit] = []
        for row in rows:
            v = np.frombuffer(row["embedding"], dtype=np.float32, count=row["embedding_dim"])
            if v.size != q.size:
                continue
            norm = np.linalg.norm(v)
            score = float(np.dot(q, v / norm)) if norm else 0.0
            scored.append(
                SearchHit(
                    chunk_index=row["chunk_index"],
                    text=row["text"],
                    locator=row["locator"],
                    score=score,
                )
            )
        scored.sort(key=lambda x: x.score, reverse=True)
        return scored[:top_k]
