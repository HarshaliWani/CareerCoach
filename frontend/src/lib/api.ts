export const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000";

export type ChatRequest = {
  session_id: string;
  message: string;
  user_profile?: Record<string, unknown>;
};

export type ChatResponse = {
  session_id: string;
  message: string;
};

export async function chat(req: ChatRequest): Promise<ChatResponse> {
  const res = await fetch(`${API_BASE}/api/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(req),
  });
  if (!res.ok) throw new Error(`Chat failed: ${res.status}`);
  return res.json();
}

export function streamChat(sessionId: string, message: string, onToken: (t: string) => void): EventSource {
  const url = `${API_BASE}/api/chat/stream?session_id=${encodeURIComponent(sessionId)}&message=${encodeURIComponent(message)}`;
  const es = new EventSource(url);
  es.onmessage = (ev) => onToken(ev.data);
  return es;
}

export type UserProfile = {
  session_id: string;
  name?: string;
  email?: string;
  traits?: Record<string, unknown>;
};

export async function upsertUser(profile: UserProfile) {
  const res = await fetch(`${API_BASE}/api/user`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(profile),
  });
  if (!res.ok) throw new Error(`User upsert failed: ${res.status}`);
  return res.json();
}