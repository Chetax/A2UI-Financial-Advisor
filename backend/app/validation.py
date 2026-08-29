"""
validation.py — the trust boundary.

Untrusted model text in, trusted A2UIResponse out. This is the ONE place where
the LLM's raw output becomes something the rest of the app can rely on.

Contract: parse_a2ui() is TOTAL. It never raises. On any failure — junk around
the JSON, unparseable JSON, or JSON that doesn't match the A2UI schema — it
returns a valid fallback A2UIResponse. Downstream code can call it with no
try/except and simply trust the result.
"""
from __future__ import annotations

import json
import logging

from pydantic import ValidationError

from app.schema import A2UIResponse, TextComponent, TextProps

logger = logging.getLogger(__name__)

_FALLBACK_MESSAGE = "Sorry, I couldn't put that together just now. Mind rephrasing?"


def _try_parse(raw: str) -> A2UIResponse:
    """
    Same three steps as parse_a2ui — extract, json.loads, validate — but NOT
    total: on failure it lets the original exception (ValueError from
    _extract_json, json.JSONDecodeError, or pydantic.ValidationError)
    propagate as-is, instead of falling back.

    main.py's retry loop calls this directly when it needs to know *why*
    something failed (str(exc)), not just that it failed.
    """
    extracted = _extract_json(raw)
    data = json.loads(extracted)
    return A2UIResponse.model_validate(data)


def _fallback(message: str = _FALLBACK_MESSAGE) -> A2UIResponse:
    """
    Build a guaranteed-valid A2UIResponse to return when parsing/validation fails.
    This function must NOT itself be able to fail — no model output touches it,
    it only uses values you control.
    """
    return A2UIResponse(
        message=message,
        component=TextComponent(
            type="text",
            props=TextProps(content=message),
        ),
    )


def _extract_json(raw: str) -> str:
    """
    Pull the JSON object out of whatever the model actually returned.

    The 'Nova tax': the model is told to emit bare JSON, but may wrap it in
    ```json ... ``` fences or add a stray sentence before/after. Return just the
    JSON substring, ready for json.loads.

    Extract defensively — but do NOT try to repair malformed JSON. If it's
    broken, let the later json.loads fail and fall back honestly.

    Raises: ValueError if no plausible JSON object can be located at all.
    """
    start = raw.find("{")
    end = raw.rfind("}")

    if start == -1 or end == -1 or end < start:
        raise ValueError("no JSON object found")

    return raw[start : end + 1]


def parse_a2ui(raw: str) -> A2UIResponse:
    """
    The public entry point. Total function: never raises.
    Any step in _try_parse failing -> log the raw output at warning level,
    return _fallback().
    """
    try:
        return _try_parse(raw)
    except (ValueError, ValidationError) as exc:
        logger.warning("A2UI parse failed, using fallback. raw=%r  err=%s", raw, exc)
        return _fallback()
