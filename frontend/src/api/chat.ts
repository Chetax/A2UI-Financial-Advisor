// src/api/chat.ts
import type { A2UIResponse, ChatRequest } from '../a2ui/types';

const API_BASE = import.meta.env.VITE_API_BASE_URL;

export async function sendChatMessage(
  req: ChatRequest
): Promise<A2UIResponse> {
  const res = await fetch(`${API_BASE}/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(req),
  });

  if (!res.ok || !res.body) {
    throw new Error(`Chat request failed: ${res.status}`);
  }

  // res.body is a ReadableStream of raw bytes (Uint8Array chunks) — not
  // text yet. A TextDecoder turns those bytes into readable string chunks
  // as they arrive, piece by piece, rather than waiting for everything.
  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let buffer = '';

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });

    const lines = buffer.split('\n');
    for (const line of lines) {
      if (line.startsWith('data:')) {
        const jsonStr = line.slice('data:'.length).trim();
        if (jsonStr) {
          return JSON.parse(jsonStr) as A2UIResponse;
        }
      }
    }
  }

  throw new Error('Stream ended without a data event');
}