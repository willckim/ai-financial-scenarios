from __future__ import annotations
import os
from typing import Literal

from anthropic import Anthropic
from openai import OpenAI

Provider = Literal["anthropic", "openai", "azure"]

SYSTEM_FALLBACK = (
    "You are a CFO-level analyst. Explain projections clearly and conservatively. "
    "Use only numbers from the provided tables."
)

class LLM:
    def __init__(self):
        # Anthropic
        self.anthropic = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        self.anthropic_model = os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-latest")

        # OpenAI (public)
        self.openai = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.openai_model = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")

        # Azure OpenAI: same OpenAI SDK, different base_url & headers
        az_base = os.getenv("AZURE_OPENAI_ENDPOINT", "").rstrip("/")
        if az_base:
            self.azure = OpenAI(
                api_key=os.getenv("AZURE_OPENAI_API_KEY"),
                base_url=f"{az_base}/openai",
                default_headers={"api-key": os.getenv("AZURE_OPENAI_API_KEY")},
            )
        else:
            self.azure = None
        self.azure_deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT")
        self.azure_api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-08-01-preview")

    def generate(
        self,
        provider: Provider,
        system: str,
        user: str,
        max_tokens: int = 800,
        temperature: float = 0.2,
        model: str | None = None
    ) -> str:
        system = system or SYSTEM_FALLBACK

        if provider == "anthropic":
            m = model or self.anthropic_model
            msg = self.anthropic.messages.create(
                model=m,
                max_tokens=max_tokens,
                temperature=temperature,
                system=system,
                messages=[{"role":"user","content":user}]
            )
            return "".join(b.text for b in msg.content)

        if provider == "openai":
            m = model or self.openai_model
            chat = self.openai.chat.completions.create(
                model=m,
                temperature=temperature,
                messages=[{"role":"system","content":system},{"role":"user","content":user}],
                max_tokens=max_tokens,
            )
            return chat.choices[0].message.content

        if provider == "azure":
            if not self.azure or not self.azure_deployment:
                raise RuntimeError("Azure OpenAI not configured.")
            chat = self.azure.chat.completions.create(
                model=self.azure_deployment,  # deployment name
                temperature=temperature,
                messages=[{"role":"system","content":system},{"role":"user","content":user}],
                max_tokens=max_tokens,
                extra_headers={"api-key": os.getenv("AZURE_OPENAI_API_KEY")},
                extra_query={"api-version": self.azure_api_version},
            )
            return chat.choices[0].message.content

        raise ValueError(f"Unknown provider: {provider}")
