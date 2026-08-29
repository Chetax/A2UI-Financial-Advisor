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
  const sendPreset = (text: string) => {
  if (loading) return;
  setTurns((prev) => [...prev, { id: crypto.randomUUID(), role: 'user', text }]);
  runChat({ session_id: sessionId, message: text });
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
    <div className="min-h-screen bg-ink flex flex-col">
      <header className="border-b border-hairline px-6 py-4">
        <h1 className="font-serif text-lg text-inkText flex items-center gap-2.5">
          <span className="w-2 h-2 rounded-full bg-gold" />
          A2UI <span className="text-gold">Financial Advisor</span>
        </h1>
      </header>

      <main className="flex-1 overflow-y-auto px-6 py-6">
        <div className="max-w-2xl mx-auto flex flex-col gap-6">
         {turns.length === 0 && (
              <div className="flex flex-col items-center text-center mt-28 gap-7">
                <div className="flex flex-col items-center gap-3">
                  <div className="h-0.5 w-8 bg-gold" />
                  <h2 className="font-serif text-2xl text-inkText">Ask about any listed company</h2>
                  <p className="text-sm text-muted max-w-sm">
                    Compare two names, or plan an allocation. Every answer comes back as a live card, not a wall of text.
                  </p>
                </div>
                <div className="flex flex-wrap gap-3 justify-center">
                  {['Compare RELIANCE and TCS', 'I want to invest ₹50,000'].map((preset) => (
                    <button
                      key={preset}
                      onClick={() => sendPreset(preset)}
                      className="bg-surface border border-hairline rounded-lg px-4 py-2.5 text-sm text-inkText hover:border-gold transition-colors"
                    >
                      {preset}
                    </button>
                  ))}
                </div>
              </div>
            )}

          {turns.map((turn) =>
            turn.role === 'user' ? (
              <div key={turn.id} className="self-end bg-hairline text-inkText rounded-2xl rounded-br-sm px-4 py-2.5 max-w-md ml-auto text-sm">
                {turn.text}
              </div>
            ) : (
              <div key={turn.id} className="flex flex-col gap-3">
                {turn.text && <p className="text-sm text-muted">{turn.text}</p>}
                {turn.node && (
                  <Renderer node={turn.node} onAction={handleAction} onSubmit={handleSubmit} />
                )}
              </div>
            )
          )}

          {loading && (
            <div className="flex items-center gap-2 text-sm text-muted">
              <span className="w-2 h-2 rounded-full bg-gold animate-bounce [animation-delay:-0.3s]" />
              <span className="w-2 h-2 rounded-full bg-gold animate-bounce [animation-delay:-0.15s]" />
              <span className="w-2 h-2 rounded-full bg-gold animate-bounce" />
            </div>
          )}

          {error && <p className="text-sm text-loss">{error}</p>}
          <div ref={bottomRef} />
        </div>
      </main>

      <footer className="border-t border-hairline px-6 py-4">
        <div className="max-w-2xl mx-auto flex gap-2">
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSend()}
            placeholder="Ask about a stock, or start an investment plan..."
            className="flex-1 bg-surface border border-hairline rounded-lg px-4 py-2.5 text-sm text-inkText placeholder:text-muted focus:outline-none focus:ring-2 focus:ring-gold focus:border-gold"
          />
          <button
            onClick={handleSend}
            disabled={loading}
            className="px-5 py-2.5 rounded-lg bg-gold text-ink font-semibold text-sm hover:brightness-95 disabled:opacity-50 transition"
          >
            Send
          </button>
        </div>
      </footer>
    </div>
  );
}

export default App;