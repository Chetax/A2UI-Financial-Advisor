"""
main.py — the conductor.

FastAPI app exposing one SSE endpoint, POST /chat. It does not play any
instrument itself; it calls the pieces you already built, in order, for one
conversation turn:

    get_history -> build_messages -> stream from Bedrock -> parse_a2ui
    -> append both turns to memory -> emit one SSE event

Design choice (v1): we COLLECT the full model stream server-side, validate it,
then send ONE clean 'data:' event with the finished, guaranteed-valid component.
Bedrock still streams to us and the endpoint is real SSE, but the browser never
sees partial/broken JSON. Partial-JSON streaming to the client is a documented
roadmap item, not this version.
"""
from __future__ import annotations

import json
import logging
from typing import Any, Dict, Iterator, List
from app.validation import _fallback, parse_a2ui

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.llm import BedrockError, stream_completion
from app.memory import MemoryStore
from app.prompts import build_messages
from app.validation import parse_a2ui

logger = logging.getLogger(__name__)


app = FastAPI(title="A2UI Financial Advisor")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

memory = MemoryStore()


class ChatRequest(BaseModel):
    """
    The POST /chat body.

    session_id: which conversation this turn belongs to (memory key).
    message:    the user's new message for this turn.
    """
    session_id: str
    message: str


def _sse(data: str) -> str:
    """
    Format one string as a single SSE event.

    Wire format is literally:  'data: <payload>\\n\\n'
    The trailing blank line is how the browser knows the event ended.
    """
    return f"data: {data}\n\n"



def _run_turn(session_id: str, user_message: str) -> Iterator[str]:
    """
    Run a single conversation turn and yield SSE event(s).

    Steps (you built all the pieces — this is orchestration):
      1. history  = memory.get_history(session_id)
      2. payload  = build_messages(history, user_message)
      3. collect the model stream:
            raw = "".join(stream_completion(payload["system"], payload["messages"]))
         wrap this in try/except BedrockError -> on failure, yield an SSE event
         carrying a safe fallback and RETURN (don't let the request 500).
      4. response = parse_a2ui(raw)            # trusted A2UIResponse, never raises
      5. persist BOTH turns to memory, in Converse shape:
            - user:      {"role": "user",      "content": [{"text": user_message}]}
            - assistant: {"role": "assistant", "content": [{"text": response.model_dump_json()}]}
         (store the assistant turn as JSON — same language the few-shot uses.)
      6. yield _sse(response.model_dump_json())

    Yielding (not returning) is what makes this a stream. For v1 you emit a single
    event, but the generator shape means you *could* emit many later.
    """
    history = memory.get_history(session_id)
    payload = build_messages(history, user_message)
    try:
        raw = "".join(stream_completion(payload["system"], payload["messages"]))
    except BedrockError as exc:
        logger.warning("Bedrock failed: %s", exc)
        yield _sse(_fallback().model_dump_json())
        return

    response = parse_a2ui(raw)
    memory.append(session_id, {"role": "user", "content": [{"text": user_message}]})
    memory.append(session_id, {"role": "assistant", "content": [{"text": response.model_dump_json()}]})
    yield _sse(response.model_dump_json())


@app.post("/chat")
def chat(req: ChatRequest) -> StreamingResponse:
    """
    SSE endpoint. Hands the browser a text/event-stream fed by _run_turn.

    Return a StreamingResponse whose first arg is the _run_turn(...) generator
    and whose media_type is "text/event-stream".
    """
    return StreamingResponse(
    _run_turn(req.session_id, req.message),
    media_type="text/event-stream",
)