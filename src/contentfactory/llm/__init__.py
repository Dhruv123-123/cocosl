"""LLM access.

`LLM.structured()` returns a validated pydantic object. Two providers:

* `anthropic` uses Claude through the official SDK with structured outputs
  (`output_config.format`) and server-side refusal fallbacks.
* `offline` never calls a network. Each caller passes an `offline` function that
  builds a deterministic placeholder from the inputs, so the whole pipeline runs
  end-to-end in tests and demos without an API key.

`auto` picks anthropic when ANTHROPIC_API_KEY (or an `ant auth` profile) is set.
"""
from __future__ import annotations

import json
import os
from typing import Callable, TypeVar

from pydantic import BaseModel

from ..db import DB, now_iso

T = TypeVar("T", bound=BaseModel)

# Rough $/MTok for cost tracking. Update if prices change.
PRICES = {
    "claude-opus-5-5": (4.00, 20.00),
    "claude-sonnet-5-5": (2.00, 10.00),
    "claude-haiku-5-5": (0.10, 0.50),
    "claude-fable-5-1": (10.00, 50.00),
}


class LLMError(RuntimeError):
    pass


def _strict_schema(model: type[BaseModel]) -> dict:
    """Pydantic JSON schema adjusted for structured outputs: every object gets
    additionalProperties false and all properties required."""
    schema = model.model_json_schema()

    def fix(node):
        if isinstance(node, dict):
            if node.get("type") == "object" and "properties" in node:
                node["additionalProperties"] = False
                node["required"] = list(node["properties"].keys())
            for key in ("default", "title"):
                if key in node and not isinstance(node[key], dict):
                    node.pop(key, None)
            for v in node.values():
                fix(v)
        elif isinstance(node, list):
            for v in node:
                fix(v)

    fix(schema)
    return schema


class LLM:
    def __init__(self, provider: str = "auto", model: str = "claude-opus-5-5",
                 effort: str = "medium", db: DB | None = None):
        self.model = model
        self.effort = effort
        self.db = db
        self._client = None
        if provider == "auto":
            provider = "anthropic" if self._anthropic_available() else "offline"
        self.provider = provider

    @staticmethod
    def _anthropic_available() -> bool:
        if not (os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("ANTHROPIC_AUTH_TOKEN")):
            return False
        try:
            import anthropic  # noqa: F401
        except ImportError:
            return False
        return True

    @property
    def client(self):
        if self._client is None:
            import anthropic
            self._client = anthropic.Anthropic()
        return self._client

    # ------------------------------------------------------------------
    def structured(self, schema: type[T], *, system: str, prompt: str,
                   offline: Callable[[], T], purpose: str = "",
                   max_tokens: int = 16000) -> T:
        if self.provider == "offline":
            result = offline()
            self._record(purpose, 0, 0)
            return result
        if self.provider != "anthropic":
            raise LLMError(f"Unknown LLM provider {self.provider}")
        return self._anthropic_structured(schema, system, prompt, purpose, max_tokens)

    def text(self, *, system: str, prompt: str, offline: Callable[[], str],
             purpose: str = "", max_tokens: int = 8000) -> str:
        if self.provider == "offline":
            self._record(purpose, 0, 0)
            return offline()
        resp = self._create(system=system, messages=[{"role": "user", "content": prompt}],
                            max_tokens=max_tokens)
        self._check(resp)
        self._record(purpose, resp.usage.input_tokens, resp.usage.output_tokens)
        return "".join(b.text for b in resp.content if b.type == "text").strip()

    # ------------------------------------------------------------------
    def _create(self, **kwargs):
        import anthropic
        try:
            return self.client.beta.messages.create(
                model=self.model,
                output_config={"effort": self.effort, **kwargs.pop("output_config", {})},
                betas=["server-side-fallback-2026-07-01"],
                fallbacks="default",
                **kwargs,
            )
        except anthropic.RateLimitError as e:  # retried by SDK already
            raise LLMError(f"Rate limited by Claude API: {e}") from e
        except anthropic.APIStatusError as e:
            raise LLMError(f"Claude API error {e.status_code}: {e.message}") from e
        except anthropic.APIConnectionError as e:
            raise LLMError(f"Could not reach Claude API: {e}") from e

    @staticmethod
    def _check(resp) -> None:
        if resp.stop_reason == "refusal":
            details = getattr(resp, "stop_details", None)
            raise LLMError(f"Model declined this request: {details}")
        if resp.stop_reason == "max_tokens":
            raise LLMError("Response hit max_tokens; raise the limit or shorten the request")

    def _anthropic_structured(self, schema, system, prompt, purpose, max_tokens):
        resp = self._create(
            system=system,
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": prompt}],
            output_config={"format": {"type": "json_schema", "schema": _strict_schema(schema)}},
        )
        self._check(resp)
        self._record(purpose, resp.usage.input_tokens, resp.usage.output_tokens)
        text = next(b.text for b in resp.content if b.type == "text")
        return schema.model_validate(json.loads(text))

    def _record(self, purpose: str, tin: int, tout: int) -> None:
        if not self.db:
            return
        pin, pout = PRICES.get(self.model, (0, 0))
        cost = (tin * pin + tout * pout) / 1_000_000 if self.provider == "anthropic" else 0
        self.db.insert("llm_usage", {
            "ts": now_iso(), "provider": self.provider, "model": self.model if self.provider != "offline" else "offline",
            "purpose": purpose, "input_tokens": tin, "output_tokens": tout, "cost_usd": cost,
        })
