import { useState, useRef, useEffect } from "react";
import client from "../api/client";
import { useToast } from "../context/ToastContext";

export default function Chatbot() {
  const { showToast } = useToast();
  const [messages, setMessages] = useState([
    { role: "assistant", content: "Namaste! Ask me about crop care, weather-driven decisions, or which government schemes you qualify for." },
  ]);
  const [input, setInput] = useState("");
  const [sending, setSending] = useState(false);
  const [error, setError] = useState(null);
  const [matchedSchemes, setMatchedSchemes] = useState([]);
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSend = async (e) => {
    e.preventDefault();
    const text = input.trim();
    if (!text) return;

    setMessages((m) => [...m, { role: "user", content: text }]);
    setInput("");
    setSending(true);
    setError(null);

    try {
      const { data } = await client.post("/chatbot/ask", { message: text });
      setMessages((m) => [...m, { role: "assistant", content: data.response }]);
      setMatchedSchemes(data.matched_schemes || []);
    } catch (err) {
      const msg = err.response?.data?.error || "The assistant didn't respond — please try again.";
      setError(msg);
      showToast(msg, "error");
    } finally {
      setSending(false);
    }
  };

  return (
    <div className="max-w-3xl mx-auto px-6 py-14 flex flex-col h-[calc(100vh-6rem)]">
      <h1 className="font-display text-3xl mb-1">Ask KrishiMitra</h1>
      <p className="text-wheat-dim mb-6">Answers are grounded to schemes you actually qualify for.</p>

      <div className="flex-1 overflow-y-auto space-y-4 pr-1">
        {messages.map((m, i) => (
          <div key={i} className={`flex ${m.role === "user" ? "justify-end" : "justify-start"}`}>
            <div
              className={`max-w-[80%] px-4 py-2.5 rounded-lg text-sm leading-relaxed ${
                m.role === "user"
                  ? "bg-turmeric text-field"
                  : "bg-field-light border border-wheat/10"
              }`}
            >
              {m.content}
            </div>
          </div>
        ))}
        <div ref={bottomRef} />
      </div>

      {matchedSchemes.length > 0 && (
        <div className="my-4 grid sm:grid-cols-2 gap-3">
          {matchedSchemes.map((s) => (
            <div key={s.id} className="p-3 rounded-md bg-field-light border border-monsoon/30 text-sm">
              <p className="font-semibold text-monsoon">{s.name}</p>
              <p className="text-wheat-dim text-xs mt-1">{s.matched_reason}</p>
            </div>
          ))}
        </div>
      )}

      {error && <p className="text-sm text-red-400 mt-2">{error}</p>}

      <form onSubmit={handleSend} className="flex gap-3 mt-4">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="e.g. My wheat leaves have yellow stripes, what should I do?"
          className="flex-1 px-4 py-2.5 rounded-md bg-field-light border border-wheat/20 focus:border-turmeric outline-none text-sm"
        />
        <button
          type="submit"
          disabled={sending}
          className="px-5 py-2.5 rounded-md bg-turmeric text-field font-semibold hover:bg-turmeric-dark transition-colors disabled:opacity-60"
        >
          {sending ? "…" : "Send"}
        </button>
      </form>
    </div>
  );
}
