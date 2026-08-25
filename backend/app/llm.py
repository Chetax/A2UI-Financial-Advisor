"""
Bedrock streaming client.

Single responsibility: given the {system, messages} payload from prompts.py,
call Bedrock's Converse *streaming* API and yield text tokens as they arrive.

"""
from __future__ import annotations

import logging
from typing import Any, Dict, Iterator, List

import boto3
from botocore.config import Config as BotoConfig
from botocore.exceptions import ClientError

from app.config import get_settings

logger = logging.getLogger(__name__)


class BedrockError(RuntimeError):
    """Raised when the Bedrock call fails (auth, throttling, bad model id, etc.)."""

_settings = get_settings()
_client = boto3.client(
    "bedrock-runtime",
    region_name=_settings.aws_region,
    config=BotoConfig(retries={"max_attempts": 2, "mode": "standard"}),
)


def stream_completion(
    system: List[Dict[str, Any]],
    messages: List[Dict[str, Any]],
) -> Iterator[str]:
    """
    Stream a completion from Bedrock, yielding text chunks in order.

    Args:
        system:   Converse `system` blocks, e.g. [{"text": SYSTEM_PROMPT}].
        messages: Converse `messages`, alternating user/assistant, ending on user.

    Yields:
        Text fragments as the model produces them.

    Raises:
        BedrockError: if the request fails at the API level.
    """
    try:
        response = _client.converse_stream(
            modelId=_settings.bedrock_model_id,
            system=system,
            messages=messages,
            inferenceConfig={
                "maxTokens": _settings.bedrock_max_tokens,
                "temperature": _settings.bedrock_temperature,
            },
        )
    except ClientError as exc:
        code = exc.response.get("Error", {}).get("Code", "Unknown")
        logger.error("Bedrock converse_stream failed: %s", code)
        raise BedrockError(f"Bedrock request failed: {code}") from exc


    for event in response["stream"]:
        if "contentBlockDelta" in event:
            delta = event["contentBlockDelta"]["delta"]
            text = delta.get("text")
            if text:
                yield text


def collect_completion(
    system: List[Dict[str, Any]],
    messages: List[Dict[str, Any]],
) -> str:
    """Convenience: drain the stream into a single string (non-streaming callers)."""
    return "".join(stream_completion(system, messages))