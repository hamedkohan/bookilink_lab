from __future__ import annotations

import hashlib
from io import BytesIO
from typing import Any

from supabase import Client, create_client

from .core import Chunk, SearchHit


class SupabaseBookStore:
    """Persistent Bookilink store backed by Supabase Postgres + Storage."""

    def __init__(self, url: str, key: str, bucket: str = "book-files"):
        self.client: Client = create_client(url, key)
        self.bucket = bucket

    @staticmethod
    def make_book_id(file_bytes: bytes) -> tuple[str, str]:
        digest = hashlib.sha256(file_bytes).hexdigest()
        return digest[:20], digest

    def has_book(self, book_id: str) -> bool:
        response = (
            self.client.table("books")
            .select("id,chunk_count")
            .eq("id", book_id)
            .limit(1)
            .execute()
        )
        return bool(response.data and response.data[0].get("chunk_count", 0) > 0)

    def upload_source_file(self, *, book_id: str, filename: str, file_bytes: bytes, content_type: str) -> str:
        safe_name = filename.replace("/", "_").replace("\\", "_")
        path = f"{book_id}/{safe_name}"
        self.client.storage.from_(self.bucket).upload(
            path=path,
            file=BytesIO(file_bytes),
            file_options={"content-type": content_type, "upsert": "true"},
        )
        return path

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
        storage_path: str | None = None,
    ) -> None:
        if len(chunks) != len(embeddings):
            raise ValueError("Chunks and embeddings length mismatch")

        self.client.table("chunks").delete().eq("book_id", book_id).execute()
        self.client.table("books").upsert(
            {
                "id": book_id,
                "title": title,
                "author": author,
                "filename": filename,
                "file_type": file_type,
                "file_hash": file_hash,
                "chunk_count": len(chunks),
                "metadata_json": metadata or {},
                "storage_path": storage_path,
            },
            on_conflict="id",
        ).execute()

        rows: list[dict[str, Any]] = []
        for chunk, embedding in zip(chunks, embeddings):
            rows.append(
                {
                    "book_id": book_id,
                    "chunk_index": chunk.chunk_index,
                    "locator": chunk.locator,
                    "text": chunk.text,
                    "embedding": embedding,
                }
            )

        batch_size = 100
        for start in range(0, len(rows), batch_size):
            self.client.table("chunks").insert(rows[start : start + batch_size]).execute()

    def list_books(self) -> list[dict]:
        response = (
            self.client.table("books")
            .select("id,title,author,filename,file_type,chunk_count,storage_path,created_at")
            .order("created_at", desc=True)
            .execute()
        )
        return list(response.data or [])

    def get_book(self, book_id: str) -> dict | None:
        response = self.client.table("books").select("*").eq("id", book_id).limit(1).execute()
        return response.data[0] if response.data else None

    def get_chunks(self, book_id: str) -> list[dict]:
        response = (
            self.client.table("chunks")
            .select("chunk_index,locator,text")
            .eq("book_id", book_id)
            .order("chunk_index")
            .execute()
        )
        return list(response.data or [])

    def search_by_vector(self, book_id: str, query_embedding: list[float], top_k: int = 7) -> list[SearchHit]:
        response = self.client.rpc(
            "match_book_chunks",
            {
                "query_embedding": query_embedding,
                "target_book_id": book_id,
                "match_count": top_k,
            },
        ).execute()
        hits: list[SearchHit] = []
        for row in response.data or []:
            hits.append(
                SearchHit(
                    chunk_index=row["chunk_index"],
                    text=row["text"],
                    locator=row["locator"],
                    score=float(row["similarity"]),
                )
            )
        return hits
