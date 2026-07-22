from __future__ import annotations
from dataclasses import dataclass
from typing import Protocol

class ModelProvider(Protocol):
    name: str
    def generate(self, *, system: str, user: str, context: str) -> str: ...

@dataclass(frozen=True)
class ProviderConfig:
    provider: str = "deterministic"
    model: str = "rules-and-templates-v1"
    timeout_seconds: int = 30
    max_output_tokens: int = 900

class DeterministicDemoProvider:
    """No-key provider used by the public demo and CI.

    The production boundary is explicit: OpenAI, Mistral or an open-source model
    can implement the same protocol without changing workflow or API contracts.
    """
    name = "deterministic"

    def generate(self, *, system: str, user: str, context: str) -> str:
        return context

class ProviderRegistry:
    def __init__(self, config: ProviderConfig | None = None) -> None:
        self.config = config or ProviderConfig()
        self._providers = {"deterministic": DeterministicDemoProvider()}

    def get(self) -> ModelProvider:
        try:
            return self._providers[self.config.provider]
        except KeyError as exc:
            raise ValueError(
                f"Provider '{self.config.provider}' is not configured in the public demo. "
                "Add a private adapter and credentials for production use."
            ) from exc
