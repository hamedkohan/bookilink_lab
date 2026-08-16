from __future__ import annotations

from openai import OpenAI


class GatewayLLMProvider:
    """OpenAI-compatible provider for the Porsit API Gateway.

    The gateway exposes /v1/chat/completions and /v1/embeddings, so this
    provider deliberately uses those two endpoints rather than the Responses API.
    """

    def __init__(
        self,
        api_key: str,
        *,
        base_url: str = "https://api-gateway.porsit.cloud/v1",
        model: str = "gpt-5.4-mini",
        embedding_model: str = "text-embedding-3-small",
    ):
        if not api_key:
            raise ValueError("A Porsit API Gateway key is required.")

        self.base_url = base_url.rstrip("/") + "/"
        self.client = OpenAI(api_key=api_key, base_url=self.base_url)
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

    def embed(self, texts: list[str], batch_size: int = 64) -> list[list[float]]:
        result: list[list[float]] = []
        for i in range(0, len(texts), batch_size):
            batch = [text if text.strip() else " " for text in texts[i : i + batch_size]]
            response = self.client.embeddings.create(
                model=self.embedding_model,
                input=batch,
            )
            result.extend(item.embedding for item in response.data)
        return result
