from __future__ import annotations

import hashlib
import json
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen

from .core import Chunk, SearchHit


class SupabaseRestError(RuntimeError):
    pass


class SupabaseRestBookStore:
    """Persistent Bookilink store using Supabase Data + Storage REST APIs.

    This intentionally avoids an extra Python dependency. It supports both the
    modern `sb_secret_...` backend key and the legacy JWT service_role key.
    """

    def __init__(self, url: str, secret_key: str, bucket: str = "book-files", timeout: int = 60):
        if not url:
            raise ValueError("SUPABASE_URL is required")
        if not secret_key:
            raise ValueError("SUPABASE_SECRET_KEY (or legacy service role key) is required")

        self.url = url.rstrip("/")
        self.secret_key = secret_key.strip()
        self.bucket = bucket
        self.timeout = timeout

    @staticmethod
    def make_book_id(file_bytes: bytes) -> tuple[str, str]:
        digest = hashlib.sha256(file_bytes).hexdigest()
        return digest[:20], digest

    def _base_headers(self, *, json_body: bool = True) -> dict[str, str]:
        headers = {
            "apikey": self.secret_key,
            "User-Agent": "Bookilink-Lab/0.3 Python",
        }
        # Modern sb_secret keys must be sent as apikey, not as a Bearer JWT.
        # Legacy service_role keys are JWTs and can also be sent as Authorization.
        if not self.secret_key.startswith("sb_secret_"):
            headers["Authorization"] = f"Bearer {self.secret_key}"
        if json_body:
            headers["Content-Type"] = "application/json"
        return headers

    def _request(
        self,
        method: str,
        path: str,
        *,
        payload: Any | None = None,
        headers: dict[str, str] | None = None,
        raw_body: bytes | None = None,
    ) -> Any:
        url = f"{self.url}{path}"
        request_headers = self._base_headers(json_body=raw_body is None)
        if headers:
            request_headers.update(headers)

        data = raw_body
        if raw_body is None and payload is not None:
            data = json.dumps(payload, ensure_ascii=False).encode("utf-8")

        request = Request(url, data=data, headers=request_headers, method=method)
        try:
            with urlopen(request, timeout=self.timeout) as response:
                body = response.read()
                if not body:
                    return None
                content_type = response.headers.get("Content-Type", "")
                if "application/json" in content_type:
                    return json.loads(body.decode("utf-8"))
                return body
        except HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise SupabaseRestError(f"Supabase HTTP {exc.code}: {detail[:1200]}") from exc
        except URLError as exc:
            raise SupabaseRestError(f"Supabase connection failed: {exc.reason}") from exc

    def ping(self) -> bool:
        rows = self._request("GET", "/rest/v1/books?select=id&limit=1")
        return isinstance(rows, list)

    def has_book(self, book_id: str) -> bool:
        query = urlencode({"select": "id,chunk_count", "id": f"eq.{book_id}", "limit": "1"})
        rows = self._request("GET", f"/rest/v1/books?{query}") or []
        return bool(rows and int(rows[0].get("chunk_count") or 0) > 0)

    def upload_source_file(
        self,
        *,
        book_id: str,
        filename: str,
        file_bytes: bytes,
        content_type: str,
    ) -> str:
        safe_name = filename.replace("/", "_").replace("\\", "_")
        storage_path = f"{book_id}/{safe_name}"
        encoded_path = "/".join(quote(part, safe="") for part in storage_path.split("/"))
        self._request(
            "POST",
            f"/storage/v1/object/{quote(self.bucket, safe='')}/{encoded_path}",
            raw_body=file_bytes,
            headers={
                "Content-Type": content_type,
                "x-upsert": "true",
            },
        )
        return storage_path

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

        # Remove old chunks first so a re-index cannot leave stale rows behind.
        delete_query = urlencode({"book_id": f"eq.{book_id}"})
        self._request("DELETE", f"/rest/v1/chunks?{delete_query}")

        book_row = {
            "id": book_id,
            "title": title,
            "author": author,
            "filename": filename,
            "file_type": file_type,
            "file_hash": file_hash,
            "chunk_count": len(chunks),
            "metadata_json": metadata or {},
            "storage_path": storage_path,
        }
        self._request(
            "POST",
            "/rest/v1/books?on_conflict=id",
            payload=book_row,
            headers={"Prefer": "resolution=merge-duplicates,return=minimal"},
        )

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

        # Vectors are large JSON payloads. Smaller batches are safer on free-tier infra.
        batch_size = 24
        for start in range(0, len(rows), batch_size):
            self._request(
                "POST",
                "/rest/v1/chunks",
                payload=rows[start : start + batch_size],
                headers={"Prefer": "return=minimal"},
            )

    def list_books(self) -> list[dict]:
        query = urlencode(
            {
                "select": "id,title,author,filename,file_type,chunk_count,storage_path,created_at",
                "order": "created_at.desc",
            }
        )
        rows = self._request("GET", f"/rest/v1/books?{query}") or []
        return list(rows)

    def get_book(self, book_id: str) -> dict | None:
        query = urlencode({"select": "*", "id": f"eq.{book_id}", "limit": "1"})
        rows = self._request("GET", f"/rest/v1/books?{query}") or []
        return rows[0] if rows else None

    def get_chunks(self, book_id: str) -> list[dict]:
        query = urlencode(
            {
                "select": "chunk_index,locator,text",
                "book_id": f"eq.{book_id}",
                "order": "chunk_index.asc",
            }
        )
        rows = self._request("GET", f"/rest/v1/chunks?{query}") or []
        return list(rows)

    def search_by_vector(self, book_id: str, query_embedding: list[float], top_k: int = 7) -> list[SearchHit]:
        rows = self._request(
            "POST",
            "/rest/v1/rpc/match_book_chunks",
            payload={
                "query_embedding": query_embedding,
                "target_book_id": book_id,
                "match_count": top_k,
            },
        ) or []
        return [
            SearchHit(
                chunk_index=int(row["chunk_index"]),
                text=row["text"],
                locator=row["locator"],
                score=float(row["similarity"]),
            )
            for row in rows
        ]
