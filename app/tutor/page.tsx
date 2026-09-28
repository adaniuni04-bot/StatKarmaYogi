"use client";

import React, { useState, useEffect, useRef } from "react";
import { api } from "@/lib/api";
import { Bot, Send, Sparkles, BookOpen, ShieldCheck, User } from "lucide-react";

export default function AITutorPage() {
  const [messages, setMessages] = useState<any[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const suggestedPrompts = [
    "How do I optimize SQL queries with composite indexes?",
    "Explain microservices circuit breakers with an example",
    "What is the difference between Docker Swarm and Kubernetes?",
    "How does RAG architecture improve LLM generation accuracy?",
    "What are the core principles of zero-trust security architecture?",
  ];

  useEffect(() => {
    setMessages([
      {
        id: "init",
        role: "assistant",
        content:
          "Welcome to **StatKarmaYogi AI Career & Tech Mentor**. Connected directly to Groq Cloud AI running **Qwen 3.8**, I provide instant architectural breakdowns, practical code solutions, and personalized career guidance.\n\nWhat technical challenge, architecture question, or skill gap would you like to explore?",
        is_grounded: true,
        confidence: 1.0,
        citations: [],
        created_at: new Date(),
      },
    ]);
  }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  const handleSend = async (textToSend?: string) => {
    const query = textToSend || input;
    if (!query.trim() || loading) return;

    const userMsg = {
      id: "user-" + Date.now(),
      role: "user",
      content: query,
      created_at: new Date(),
    };

    setMessages((prev) => [...prev, userMsg]);
    if (!textToSend) setInput("");
    setLoading(true);

    try {
      const res = await api.chatTutor(query, sessionId || undefined);
      setMessages((prev) => [...prev, res]);
    } catch (err: any) {
      setMessages((prev) => [
        ...prev,
        {
          id: "err-" + Date.now(),
          role: "assistant",
          content: "Encountered an issue reaching Groq Cloud AI tutor: " + err.message,
          is_grounded: false,
          citations: [],
          created_at: new Date(),
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-4 py-4">
      {/* Header */}
      <div className="bg-white border border-slate-300 p-5 space-y-1">
        <div className="flex flex-wrap items-center justify-between gap-2">
          <h1 className="text-xl font-bold text-slate-900 flex items-center space-x-2">
            <Bot className="w-5 h-5 text-blue-600" />
            <span>StatKarmaYogi AI Career & Tech Mentor</span>
          </h1>
          <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 text-xs font-bold bg-emerald-50 text-emerald-800 border border-emerald-300">
            <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
            Groq Cloud AI (Qwen 3.8 Active)
          </span>
        </div>
        <p className="text-xs text-slate-600">
          Powered by Groq Cloud AI running Qwen 3.8. Ultra-low latency responses for system architecture, coding solutions, cybersecurity, and career guidance.
        </p>
      </div>

      {/* Chat Container */}
      <div className="bg-white border border-slate-300 flex flex-col h-[600px]">
        {/* Messages Scroll Area */}
        <div className="flex-1 p-5 overflow-y-auto space-y-4 bg-slate-50">
          {messages.map((m) => {
            const isUser = m.role === "user";
            return (
              <div
                key={m.id}
                className={`flex items-start space-x-2.5 ${isUser ? "flex-row-reverse space-x-reverse" : ""}`}
              >
                <div
                  className={`w-7 h-7 flex items-center justify-center shrink-0 border text-xs font-bold ${
                    isUser
                      ? "bg-slate-900 text-white border-slate-900"
                      : "bg-blue-600 text-white border-blue-700"
                  }`}
                >
                  {isUser ? <User className="w-3.5 h-3.5" /> : <Bot className="w-3.5 h-3.5" />}
                </div>

                <div
                  className={`max-w-2xl p-3.5 text-xs leading-relaxed space-y-2 border ${
                    isUser
                      ? "bg-slate-800 text-white border-slate-900"
                      : "bg-white text-slate-900 border-slate-300"
                  }`}
                >
                  <div className="whitespace-pre-wrap">{m.content}</div>

                  {!isUser && m.citations?.length > 0 && (
                    <div className="pt-2 border-t border-slate-200 space-y-1">
                      <div className="text-[10px] font-bold uppercase tracking-wider text-slate-600 flex items-center space-x-1">
                        <ShieldCheck className="w-3 h-3 text-emerald-600" />
                        <span>Referenced Materials:</span>
                      </div>
                      <div className="flex flex-wrap gap-1">
                        {m.citations.map((c: any, i: number) => (
                          <span
                            key={i}
                            className="inline-flex items-center space-x-1 bg-slate-100 text-slate-700 border border-slate-300 px-2 py-0.5 text-[10px]"
                          >
                            <BookOpen className="w-2.5 h-2.5" />
                            <span>{c.title}</span>
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            );
          })}

          {loading && (
            <div className="flex items-center space-x-2.5">
              <div className="w-7 h-7 bg-blue-600 text-white flex items-center justify-center border border-blue-700 text-xs">
                <Bot className="w-3.5 h-3.5" />
              </div>
              <div className="bg-white p-2.5 border border-slate-300 text-xs text-slate-600 flex items-center space-x-2">
                <div className="w-2 h-2 bg-blue-600 animate-ping" />
                <span>Groq Cloud AI (Qwen) is formulating technical response...</span>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Suggested Prompts */}
        <div className="p-2.5 bg-white border-t border-slate-300 overflow-x-auto flex items-center space-x-2 shrink-0">
          <span className="text-[10px] font-bold text-slate-600 uppercase tracking-wider flex items-center px-1 shrink-0">
            <Sparkles className="w-3 h-3 mr-1 text-blue-600" /> Quick Topics:
          </span>
          {suggestedPrompts.map((p, idx) => (
            <button
              key={idx}
              onClick={() => handleSend(p)}
              disabled={loading}
              className="text-[11px] bg-white hover:bg-slate-100 text-slate-800 px-2.5 py-1 border border-slate-300 shrink-0 transition cursor-pointer"
            >
              {p}
            </button>
          ))}
        </div>

        {/* Input */}
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleSend();
          }}
          className="p-3 bg-white border-t border-slate-300 flex items-center space-x-2"
        >
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Type your technical or career question here..."
            className="flex-1 px-3 py-2 border border-slate-300 text-xs bg-white text-slate-900 focus:outline-none focus:border-blue-600"
          />
          <button
            type="submit"
            disabled={loading || !input.trim()}
            className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white font-bold text-xs border border-blue-700 disabled:bg-slate-300 transition cursor-pointer flex items-center gap-1.5"
          >
            <span>Send</span>
            <Send className="w-3.5 h-3.5" />
          </button>
        </form>
      </div>
    </div>
  );
}