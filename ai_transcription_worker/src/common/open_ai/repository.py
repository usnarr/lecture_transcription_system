import os
import logging
from openai import AsyncOpenAI

logger = logging.getLogger(__name__)

DEFAULT_SYSTEM_MSG = (
    "You are a helpful assistant that summarizes and performs "
    "other operations on lecture transcriptions."
)


class OpenAIRepository:
    """Async wrapper around the OpenAI chat completions API (GPT-5)."""

    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set")

        self._client = AsyncOpenAI(api_key=api_key)
        self.model = os.getenv("OPENAI_MODEL", "gpt-5")
        self.temperature = float(os.getenv("OPENAI_TEMPERATURE", 0.7))
        self.max_tokens = int(os.getenv("OPENAI_MAX_TOKENS", 4096))
        self._messages: list[dict[str, str]] = []

    async def set_messages(self, prompt_msg: str, system_msg: str | None = None):
        """Prepare the message payload for the next completion call."""
        self._messages = [
            {"role": "system", "content": system_msg or DEFAULT_SYSTEM_MSG},
            {"role": "user", "content": prompt_msg},
        ]

    async def generate_summary(self) -> str:
        """Call the OpenAI chat completions endpoint and return the assistant message."""
        if not self._messages:
            raise ValueError("Messages not set. Call set_messages() first.")

        logger.info("Requesting completion from model=%s", self.model)
        response = await self._client.chat.completions.create(
            model=self.model,
            messages=self._messages,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
        )
        content = response.choices[0].message.content
        logger.info(
            "Completion received – tokens used: prompt=%s, completion=%s",
            response.usage.prompt_tokens,
            response.usage.completion_tokens,
        )
        return content

    async def close(self):
        """Gracefully close the underlying HTTP client."""
        await self._client.close()