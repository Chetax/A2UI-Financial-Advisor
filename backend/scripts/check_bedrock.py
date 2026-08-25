"""
Bedrock check -- is the model actually running?

Run this before building anything on top of the LLM layer. It exercises the real
path end to end: build_messages -> Bedrock converse_stream -> collect text ->
validate against the A2UI schema. If this passes, the whole prompt+model+schema
spine works and any later bug is above this layer.

Usage (from backend/):
    python -m scripts.check_bedrock
    python -m scripts.check_bedrock "Compare INFY and WIPRO"

Requires: valid AWS credentials + Bedrock model access for BEDROCK_MODEL_ID
in AWS_REGION (see .env).
"""
from __future__ import annotations

import json
import sys
import time

from app.config import get_settings
from app.llm import BedrockError, stream_completion
from app.prompts import build_messages
from app.schema import A2UIResponse


def main() -> int:
    user_message = sys.argv[1] if len(sys.argv) > 1 else "Compare RELIANCE and TCS"
    settings = get_settings()

    print("=" * 60)
    print("A2UI Bedrock check")
    print(f"  region : {settings.aws_region}")
    print(f"  model  : {settings.bedrock_model_id}")
    print(f"  prompt : {user_message!r}")
    print("=" * 60)

    payload = build_messages(history=[], user_message=user_message)

    # 1. Stream from the model, printing tokens live so we can see it working.
    print("\n[1/3] Streaming from Bedrock...\n")
    chunks: list[str] = []
    started = time.time()
    try:
        for token in stream_completion(payload["system"], payload["messages"]):
            chunks.append(token)
            print(token, end="", flush=True)
    except BedrockError as exc:
        print(f"\n\n[FAIL] Bedrock call failed: {exc}")
        print("   Common causes:")
        print("   - Model access not enabled for this model in this region")
        print("     (Bedrock console -> Model access)")
        print("   - AWS credentials not configured (run `aws configure`)")
        print("   - Wrong region / model id in .env")
        return 1

    raw = "".join(chunks)
    elapsed = time.time() - started
    print(f"\n\n[1/3] [OK] Streamed {len(raw)} chars in {elapsed:.1f}s")

    # 2. Parse the text as JSON.
    print("\n[2/3] Parsing JSON...")
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        print(f"[2/3] [FAIL] Model output was not valid JSON: {exc}")
        print("      (This is exactly what validation.py + fallback will handle.)")
        return 1
    print("[2/3] [OK] Valid JSON")

    # 3. Validate against the A2UI schema.
    print("\n[3/3] Validating against A2UI schema...")
    try:
        parsed = A2UIResponse.model_validate(data)
    except Exception as exc:  # pydantic ValidationError
        print(f"[3/3] [FAIL] JSON did not match the A2UI schema:\n{exc}")
        return 1
    print(f"[3/3] [OK] Valid A2UI -- root component type: {parsed.component.type!r}")

    print("\n" + "=" * 60)
    print("[PASS] Model is running and returns valid A2UI.")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())