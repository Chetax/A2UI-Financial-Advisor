"""
memory.py — per-session conversation memory.

Holds the running history for each session so the agent can personalise later
turns from earlier ones (README promise: "later turns are personalised to
earlier ones"). This is the piece that feeds build_messages(history, ...).

Storage shape: history is a list of Converse-ready messages
    {"role": "user"|"assistant", "content": [{"text": <string>}]}
so it can be replayed straight into Bedrock with no translation. Assistant turns
are stored as the JSON string of the A2UIResponse — the same language the
few-shot examples speak — so the model keeps emitting JSON across turns.

In-memory by default (a dict). DynamoDB / Redis are documented production swaps,
not build requirements — do not gold-plate this.
"""
from __future__ import annotations
from typing import Any, Dict, List

class MemoryStore:
    """
    In-memory conversation store, keyed by session id.

    Not thread/async safe and not persistent — fine for a single-process demo,
    and the interface is small enough to swap for a real backend later.
    """

    def __init__(self) -> None:
        """
        Set up the empty backing store: session_id -> list of Converse messages.
        Nothing else to configure.
        """
        self._store: Dict[str, List[Dict[str, Any]]] = {}

    def get_history(self, session_id: str) -> List[Dict[str, Any]]:
        """
        Return the messages stored for this session, oldest first.

        A session that's never been seen is NOT an error — it's just an empty
        conversation. Return an empty list, don't raise. (Think: which dict
        method gives you 'value, or a default if the key is missing'?)
        """
        return self._store.get(session_id, [])

    def append(self, session_id: str, message: Dict[str, Any]) -> None:
        """
        Append ONE Converse-shaped message to this session's history.

        message looks like {"role": ..., "content": [{"text": ...}]}. The caller
        builds that shape; this method just stores it.

        First message for a new session must work too — make sure the list
        exists before you append to it. (setdefault is your friend.)
        """
        
        self._store.setdefault(session_id, []).append(message)
