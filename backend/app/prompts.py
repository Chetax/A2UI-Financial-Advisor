"""
Prompt design
"""
from __future__ import annotations

import json
from typing import Any, Dict, List


# --------------------------------------------------------------------------- #
# 1. The A2UI contract, described for the model.
#    Kept in sync with schema.py — this is the human/LLM-readable mirror of it.
# --------------------------------------------------------------------------- #
A2UI_SCHEMA_SPEC = """\
You return ONE JSON object with this shape:

{
  "message": string | null,     // short conversational lead-in shown above the UI
  "component": <Component>       // the root UI node
}

A <Component> is one of these six types. Every node is { "type", "props", "children"? }.

1. "container"  — layout wrapper. Has children.
   props: { "direction": "row"|"column" (default "column"),
            "gap": number (default 12),
            "align": "start"|"center"|"end"|"stretch" (optional) }
   children: Component[]

2. "card"       — titled surface. Has children.
   props: { "title": string (optional), "subtitle": string (optional) }
   children: Component[]

3. "text"       — a piece of text.
   props: { "content": string,
            "variant": "heading"|"subheading"|"body"|"caption"|"metric"|"label" (default "body") }

4. "button"     — triggers an action sent back to the agent.
   props: { "label": string,
            "action": { "id": string, "payload": object|null },
            "variant": "primary"|"secondary"|"ghost" (default "primary") }

5. "text-field" — a controlled input that contributes to a form's submit payload.
   props: { "name": string,        // key this field adds to the submit payload
            "label": string,
            "placeholder": string (optional),
            "value": string (optional),
            "inputType": "text"|"number"|"email" (default "text") }

6. "form"       — groups fields; emits a typed payload on submit. Has children.
   props: { "submitLabel": string (default "Submit"),
            "action": { "id": string, "payload": object|null } }
   children: Component[]   // typically text-field and text nodes

Rules:
- Compose freely: containers and cards nest other components via "children".
- Use ONLY the six types and the exact prop names / enum values above.
- Output MUST be a single JSON object. No markdown, no code fences, no text
  before or after the JSON. Your entire reply must start with { and end with }.
"""


# --------------------------------------------------------------------------- #
# 2. System prompt — role, task, the "you decide the UI" framing, hard rules.
# --------------------------------------------------------------------------- #
SYSTEM_PROMPT = f"""\
You are the UI-generating agent for a financial advisory assistant. Instead of
replying with prose, you reply with a user interface described as JSON. The
frontend renders your JSON as real, interactive components.

Your job is to CHOOSE THE RIGHT INTERFACE for each request and return it:
- The user wants to compare things or see data  -> a "card" laying it out clearly.
- You need information from the user             -> a "form" of "text-field"s.
- The user just submitted data / you have their
  numbers and can give a result                 -> a "card" summarising it.

Design for clarity: give cards titles, group related items in containers, use
"metric" text for numbers and "heading"/"subheading" for structure. Keep it
clean and readable — this should feel like a real product, not a debug dump.

For financial figures use Indian Rupees (₹) and NSE tickers (e.g. RELIANCE, TCS).
If real market data is provided to you in brackets like "[Real market data: ...]",
you MUST use those exact figures in your response instead of inventing your own.
If no real data is provided, use your own knowledge as a reasonable estimate.

{A2UI_SCHEMA_SPEC}
"""


# --------------------------------------------------------------------------- #
# 3. Few-shot examples — one per flow. Each is a (user, assistant-JSON) pair.
#    The assistant content is the exact JSON the model should learn to emit.
# --------------------------------------------------------------------------- #

# Flow 1 — Data display: comparison card.
_EX1_USER = "Compare RELIANCE and TCS"
_EX1_ASSISTANT = {
    "message": "Here's how RELIANCE and TCS compare on key metrics.",
    "component": {
        "type": "card",
        "props": {"title": "RELIANCE vs TCS", "subtitle": "Key metrics at a glance"},
        "children": [
            {
                "type": "container",
                "props": {"direction": "row", "gap": 24},
                "children": [
                    {
                        "type": "container",
                        "props": {"direction": "column", "gap": 6},
                        "children": [
                            {"type": "text", "props": {"content": "RELIANCE", "variant": "subheading"}},
                            {"type": "text", "props": {"content": "Sector: Energy / Conglomerate", "variant": "caption"}},
                            {"type": "text", "props": {"content": "Market cap", "variant": "label"}},
                            {"type": "text", "props": {"content": "₹19.2L Cr", "variant": "metric"}},
                            {"type": "text", "props": {"content": "P/E", "variant": "label"}},
                            {"type": "text", "props": {"content": "28.5", "variant": "metric"}},
                        ],
                    },
                    {
                        "type": "container",
                        "props": {"direction": "column", "gap": 6},
                        "children": [
                            {"type": "text", "props": {"content": "TCS", "variant": "subheading"}},
                            {"type": "text", "props": {"content": "Sector: IT Services", "variant": "caption"}},
                            {"type": "text", "props": {"content": "Market cap", "variant": "label"}},
                            {"type": "text", "props": {"content": "₹14.1L Cr", "variant": "metric"}},
                            {"type": "text", "props": {"content": "P/E", "variant": "label"}},
                            {"type": "text", "props": {"content": "30.1", "variant": "metric"}},
                        ],
                    },
                ],
            }
        ],
    },
}

# Flow 2 — Form interaction: preference form.
_EX2_USER = "I want to invest ₹50,000 — suggest an allocation"
_EX2_ASSISTANT = {
    "message": "Tell me a bit about your preferences and I'll suggest an allocation.",
    "component": {
        "type": "form",
        "props": {"submitLabel": "Get my allocation", "action": {"id": "submit_allocation_prefs", "payload": None}},
        "children": [
            {"type": "text", "props": {"content": "Investment preferences", "variant": "heading"}},
            {"type": "text-field", "props": {"name": "amount", "label": "Amount to invest (₹)", "value": "50000", "inputType": "number"}},
            {"type": "text-field", "props": {"name": "risk", "label": "Risk tolerance (low / medium / high)", "placeholder": "medium", "inputType": "text"}},
            {"type": "text-field", "props": {"name": "horizon_years", "label": "Time horizon (years)", "placeholder": "5", "inputType": "number"}},
        ],
    },
}

# Flow 3 — Summary: personalised allocation card (after the form is submitted).
_EX3_USER = 'The user submitted the allocation form with: {"amount": "50000", "risk": "medium", "horizon_years": "5"}'
_EX3_ASSISTANT = {
    "message": "Based on a medium risk profile over 5 years, here's a suggested split of your ₹50,000.",
    "component": {
        "type": "card",
        "props": {"title": "Suggested allocation", "subtitle": "₹50,000 · medium risk · 5-year horizon"},
        "children": [
            {
                "type": "container",
                "props": {"direction": "column", "gap": 10},
                "children": [
                    {
                        "type": "container",
                        "props": {"direction": "row", "gap": 12},
                        "children": [
                            {"type": "text", "props": {"content": "Equity funds (60%)", "variant": "label"}},
                            {"type": "text", "props": {"content": "₹30,000", "variant": "metric"}},
                        ],
                    },
                    {
                        "type": "container",
                        "props": {"direction": "row", "gap": 12},
                        "children": [
                            {"type": "text", "props": {"content": "Debt funds (30%)", "variant": "label"}},
                            {"type": "text", "props": {"content": "₹15,000", "variant": "metric"}},
                        ],
                    },
                    {
                        "type": "container",
                        "props": {"direction": "row", "gap": 12},
                        "children": [
                            {"type": "text", "props": {"content": "Gold / cash (10%)", "variant": "label"}},
                            {"type": "text", "props": {"content": "₹5,000", "variant": "metric"}},
                        ],
                    },
                    {"type": "text", "props": {"content": "Diversified to balance growth and stability for a medium-risk, 5-year goal.", "variant": "caption"}},
                ],
            }
        ],
    },
}

# Each example becomes a user turn followed by an assistant turn whose content is
# the raw JSON string (no fences) — teaching the exact output format.
FEW_SHOT_EXAMPLES: List[Dict[str, Any]] = [
    {"role": "user", "content": [{"text": _EX1_USER}]},
    {"role": "assistant", "content": [{"text": json.dumps(_EX1_ASSISTANT, ensure_ascii=False)}]},
    {"role": "user", "content": [{"text": _EX2_USER}]},
    {"role": "assistant", "content": [{"text": json.dumps(_EX2_ASSISTANT, ensure_ascii=False)}]},
    {"role": "user", "content": [{"text": _EX3_USER}]},
    {"role": "assistant", "content": [{"text": json.dumps(_EX3_ASSISTANT, ensure_ascii=False)}]},
]


# --------------------------------------------------------------------------- #
# 4. Message builder for Bedrock's Converse API.
#    Converse wants `system` separate from `messages`; messages must alternate
#    user/assistant and end on a user turn.
# --------------------------------------------------------------------------- #
def build_messages(
    history: List[Dict[str, Any]],
    user_message: str,
) -> Dict[str, Any]:
    """
    Assemble the Converse payload pieces.

    Args:
        history: prior turns for this session, already in Converse shape
                 ([{"role": "user"|"assistant", "content": [{"text": ...}]}]).
        user_message: the new user message for this turn.

    Returns:
        {"system": [...], "messages": [...]} ready to spread into converse_stream.
    """
    messages: List[Dict[str, Any]] = []
    messages.extend(FEW_SHOT_EXAMPLES)
    messages.extend(history)
    messages.append({"role": "user", "content": [{"text": user_message}]})

    return {
        "system": [{"text": SYSTEM_PROMPT}],
        "messages": messages,
    }