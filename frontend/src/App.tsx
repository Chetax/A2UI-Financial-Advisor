import { useState, useRef, useEffect } from 'react';
import { Renderer } from './a2ui/Renderer';
import { sendChatMessage } from './api/chat';
import type { Component, Action } from './a2ui/types';

interface Turn {
  id: string;
  role: 'user' | 'assistant';
  text?: string;
  node?: Component;
}

function App() {
  const [sessionId] = useState(() => crypto.randomUUID());
  const [turns, setTurns] = useState<Turn[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [turns, loading]);

  const pushAssistantTurn = (message: string | undefined, component: Component) => {
    setTurns((prev) => [
      ...prev,
      { id: crypto.randomUUID(), role: 'assistant', text: message, node: component },
    ]);
  };

  const runChat = async (req: Parameters<typeof sendChatMessage>[0]) => {
    setLoading(true);
    setError(null);
    try {
      const res = await sendChatMessage(req);
      pushAssistantTurn(res.message, res.component);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Something went wrong');
    } finally {
      setLoading(false);
    }
  };

  const handleSend = () => {
    if (!input.trim() || loading) return;
    setTurns((prev) => [...prev, { id: crypto.randomUUID(), role: 'user', text: input }]);
    runChat({ session_id: sessionId, message: input });
    setInput('');
  };

  const handleAction = (action: Action) =>
    runChat({ session_id: sessionId, action_id: action.id, action_payload: action.payload });

  const handleSubmit = (action: Action, payload: Record<string, string>) =>
    runChat({ session_id: sessionId, action_id: action.id, action_payload: payload });

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      <header className="border-b border-gray-200 bg-white px-6 py-4">
        <h1 className="text-lg font-semibold text-gray-900">A2UI Financial Advisor</h1>
      </header>

      <main className="flex-1 overflow-y-auto px-6 py-6">
        <div className="max-w-2xl mx-auto flex flex-col gap-6">
          {turns.length === 0 && (
            <p className="text-sm text-gray-400 text-center mt-20">
              Try: "Compare RELIANCE and TCS" or "I want to invest ₹50,000"
            </p>
          )}

          {turns.map((turn) =>
            turn.role === 'user' ? (
              <div key={turn.id} className="self-end bg-blue-600 text-white rounded-2xl rounded-br-sm px-4 py-2.5 max-w-md ml-auto text-sm">
                {turn.text}
              </div>
            ) : (
              <div key={turn.id} className="flex flex-col gap-3">
                {turn.text && <p className="text-sm text-gray-600">{turn.text}</p>}
                {turn.node && (
                  <Renderer node={turn.node} onAction={handleAction} onSubmit={handleSubmit} />
                )}
              </div>
            )
          )}

          {loading && (
            <div className="flex items-center gap-2 text-sm text-gray-400">
              <span className="w-2 h-2 rounded-full bg-gray-300 animate-bounce [animation-delay:-0.3s]" />
              <span className="w-2 h-2 rounded-full bg-gray-300 animate-bounce [animation-delay:-0.15s]" />
              <span className="w-2 h-2 rounded-full bg-gray-300 animate-bounce" />
            </div>
          )}

          {error && <p className="text-sm text-red-600">{error}</p>}
          <div ref={bottomRef} />
        </div>
      </main>

      <footer className="border-t border-gray-200 bg-white px-6 py-4">
        <div className="max-w-2xl mx-auto flex gap-2">
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSend()}
            placeholder="Ask about a stock, or start an investment plan..."
            className="flex-1 border border-gray-300 rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          />
          <button
            onClick={handleSend}
            disabled={loading}
            className="px-5 py-2.5 rounded-lg bg-blue-600 text-white font-medium text-sm hover:bg-blue-700 disabled:opacity-50 transition-colors"
          >
            Send
          </button>
        </div>
      </footer>
    </div>
  );
}

export default App;