from __future__ import annotations

from openai import OpenAI


class LLMProvider:
    def __init__(
        self,
        api_key: str,
        model: str = "gpt-5.6-terra",
        embedding_model: str = "text-embedding-3-small",
    ):
        if not api_key:
            raise ValueError("An OpenAI API key is required.")
        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.embedding_model = embedding_model

    def generate(self, instructions: str, prompt: str, reasoning_effort: str = "low") -> str:
        response = self.client.responses.create(
            model=self.model,
            reasoning={"effort": reasoning_effort},
            instructions=instructions,
            input=prompt,
        )
        return response.output_text.strip()

    def embed(self, texts: list[str], batch_size: int = 64) -> list[list[float]]:
        result: list[list[float]] = []
        for i in range(0, len(texts), batch_size):
            batch = [t if t.strip() else " " for t in texts[i : i + batch_size]]
            response = self.client.embeddings.create(
                model=self.embedding_model,
                input=batch,
                encoding_format="float",
            )
            result.extend(item.embedding for item in response.data)
        return result
