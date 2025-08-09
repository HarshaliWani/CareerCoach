import { useEffect, useMemo, useRef, useState } from "react";
import { chat as chatApi, streamChat, upsertUser } from "./lib/api";
import "./App.css";

function randomSessionId() {
  return crypto.getRandomValues(new Uint32Array(2)).join("-");
}

type ChatMessage = { role: "user" | "assistant"; content: string };

function App() {
  const [sessionId, setSessionId] = useState<string>(() => randomSessionId());
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [streaming, setStreaming] = useState(false);
  const streamRef = useRef<EventSource | null>(null);

  useEffect(() => {
    // Initialize user traits placeholder
    upsertUser({ session_id: sessionId, traits: { country: "India" } }).catch(
      () => {}
    );
  }, [sessionId]);

  const send = async () => {
    const text = input.trim();
    if (!text || streaming) return;
    setMessages((m) => [...m, { role: "user", content: text }, { role: "assistant", content: "" }]);
    setInput("");
    setStreaming(true);

    let assistantIndex = messages.length + 1; // last pushed assistant
    const es = streamChat(sessionId, text, (token) => {
      setMessages((m) => {
        const copy = [...m];
        copy[assistantIndex] = {
          role: "assistant",
          content: copy[assistantIndex].content + token,
        };
        return copy;
      });
    });
    streamRef.current = es;
    es.onerror = () => {
      es.close();
      setStreaming(false);
    };
    es.onopen = () => {};
    es.addEventListener("end", () => {
      es.close();
      setStreaming(false);
    });
    // Close when stream naturally ends: backend sends completed then stream closes
    es.onmessage = (ev) => {
      setMessages((m) => {
        const copy = [...m];
        copy[assistantIndex] = {
          role: "assistant",
          content: copy[assistantIndex].content + ev.data,
        };
        return copy;
      });
    };
  };

  return (
    <div className="app">
      <header>
        <h1>AI Career Coach</h1>
        <div>
          <label>Session:</label>
          <input
            value={sessionId}
            onChange={(e) => setSessionId(e.target.value)}
            style={{ width: 280 }}
          />
        </div>
      </header>
      <main>
        <div className="chat">
          {messages.map((m, i) => (
            <div key={i} className={`msg ${m.role}`}>
              <div className="role">{m.role === "user" ? "You" : "Coach"}</div>
              <div className="bubble">{m.content}</div>
            </div>
          ))}
        </div>
      </main>
      <footer>
        <input
          placeholder="Ask about careers, colleges, exams, skills..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter") send();
          }}
          disabled={streaming}
        />
        <button onClick={send} disabled={streaming || !input.trim()}>
          {streaming ? "Streaming..." : "Send"}
        </button>
      </footer>
    </div>
  );
}

export default App;
