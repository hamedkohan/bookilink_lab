from __future__ import annotations

import time

from openai import (
    APIConnectionError,
    APIStatusError,
    APITimeoutError,
    InternalServerError,
    OpenAI,
    RateLimitError,
)


class GatewayLLMProvider:
    """OpenAI-compatible provider for the Porsit API Gateway.

    The gateway exposes /v1/chat/completions and /v1/embeddings, so this
    provider deliberately uses those two endpoints rather than the Responses API.

    Embedding requests are intentionally sent in small batches. Some intermediary
    gateways/proxies time out on large embedding payloads even when the upstream
    provider would otherwise accept them.
    """

    def __init__(
        self,
        api_key: str,
        *,
        base_url: str = "https://api-gateway.porsit.cloud/v1",
        model: str = "gpt-5.4-mini",
        embedding_model: str = "text-embedding-3-small",
        timeout_seconds: float = 120.0,
        max_retries: int = 2,
    ):
        if not api_key:
            raise ValueError("A Porsit API Gateway key is required.")

        self.base_url = base_url.rstrip("/") + "/"
        self.client = OpenAI(
            api_key=api_key,
            base_url=self.base_url,
            timeout=timeout_seconds,
            max_retries=max_retries,
        )
        self.model = model
        self.embedding_model = embedding_model

    def generate(self, instructions: str, prompt: str, reasoning_effort: str = "low") -> str:
        # reasoning_effort is accepted for interface compatibility with the
        # existing Bookilink services, but is intentionally not forwarded.
        # This keeps the request compatible with a standard chat-completions gateway.
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": instructions},
                {"role": "user", "content": prompt},
            ],
        )
        content = response.choices[0].message.content
        if content is None:
            return ""
        if isinstance(content, str):
            return content.strip()
        return str(content).strip()

    @staticmethod
    def _retryable(exc: Exception) -> bool:
        if isinstance(
            exc,
            (APITimeoutError, APIConnectionError, RateLimitError, InternalServerError),
        ):
            return True
        if isinstance(exc, APIStatusError):
            return exc.status_code == 429 or exc.status_code >= 500
        return False

    def _embed_batch(self, batch: list[str], attempts: int = 3) -> list[list[float]]:
        last_error: Exception | None = None
        for attempt in range(attempts):
            try:
                response = self.client.embeddings.create(
                    model=self.embedding_model,
                    input=batch,
                )
                return [item.embedding for item in response.data]
            except Exception as exc:  # preserve non-OpenAI-compatible gateway errors too
                last_error = exc
                if not self._retryable(exc) or attempt == attempts - 1:
                    break
                time.sleep(1.5 * (2**attempt))

        # A large payload can time out at the gateway even though smaller ones work.
        # Recursively split only retryable failures, preserving order.
        if last_error is not None and self._retryable(last_error) and len(batch) > 1:
            midpoint = max(1, len(batch) // 2)
            return self._embed_batch(batch[:midpoint], attempts=2) + self._embed_batch(
                batch[midpoint:], attempts=2
            )

        if last_error is not None:
            raise last_error
        raise RuntimeError("Embedding request failed without an error object.")

    def embed(self, texts: list[str], batch_size: int = 8) -> list[list[float]]:
        result: list[list[float]] = []
        for i in range(0, len(texts), batch_size):
            batch = [text if text.strip() else " " for text in texts[i : i + batch_size]]
            result.extend(self._embed_batch(batch))
        return result
