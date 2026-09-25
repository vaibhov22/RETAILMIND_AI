"use client";

import { useEffect, useRef, useState } from "react";
import { supabase } from "@/lib/supabase";

const API_URL = "https://retailmind-ai-7h7v.onrender.com";

type ChatMessage = {
  question: string;
  answer: any;
};

export default function Copilot() {
  const [chatHistory, setChatHistory] = useState<ChatMessage[]>([]);
  const [question, setQuestion] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({
      behavior: "smooth",
    });
  }, [chatHistory, loading]);

  async function askCopilot() {
    const trimmedQuestion = question.trim();

    if (!trimmedQuestion || loading) return;

    setLoading(true);
    setError("");
    setQuestion("");

    try {
      const {
        data: { session },
      } = await supabase.auth.getSession();

      const token = session?.access_token;

      if (!token) {
        setError("Your session has expired. Please login again.");
        setLoading(false);
        return;
      }

      const response = await fetch(`${API_URL}/copilot`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          question: trimmedQuestion,
          history: chatHistory,
        }),
      });

      const result = await response.json();

      console.log("COPILOT RESPONSE:", result);

      if (!response.ok) {
        throw new Error(
          result?.detail ||
          result?.error ||
          `Request failed: ${response.status}`
        );
      }

      setChatHistory((previous) => [
        ...previous,
        {
          question: trimmedQuestion,
          answer: result,
        },
      ]);
    } catch (err) {
      console.error("COPILOT ERROR:", err);

      setError(
        err instanceof Error
          ? err.message
          : "Something went wrong. Try again."
      );
    } finally {
      setLoading(false);
    }
  }

  function displayAnswer(answer: any) {
    if (typeof answer === "string") {
      return answer;
    }

    if (answer?.answer) {
      return answer.answer;
    }

    if (answer?.response) {
      return answer.response;
    }

    return JSON.stringify(answer);
  }

  function clearConversation() {
    setChatHistory([]);
    setError("");
  }

  return (
    <main className="min-h-screen bg-[#f7f9fc] px-6 py-8 text-gray-900">
      <div className="mx-auto flex max-w-5xl flex-col">

        <div className="mb-6">
          <p className="text-sm font-medium text-blue-600">
            AI Business Assistant
          </p>

          <div className="mt-1 flex items-center justify-between gap-4">
            <div>
              <h1 className="text-3xl font-bold tracking-tight">
                Retailer Copilot
              </h1>

              <p className="mt-2 text-sm text-gray-500">
                Ask any question about your business in plain English.
              </p>
            </div>

            {chatHistory.length > 0 && (
              <button
                onClick={clearConversation}
                className="rounded-lg border border-gray-200 bg-white px-4 py-2 text-sm font-medium text-gray-600 shadow-sm hover:bg-gray-50"
              >
                Clear conversation
              </button>
            )}
          </div>
        </div>

        <div className="flex min-h-[650px] flex-col overflow-hidden rounded-2xl border border-gray-200 bg-white shadow-sm">

          <div className="flex-1 space-y-6 overflow-y-auto p-6">

            {chatHistory.length === 0 && !loading ? (
              <div className="flex min-h-[500px] items-center justify-center">
                <div className="max-w-md text-center">

                  <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-2xl bg-blue-50 text-3xl">
                    💬
                  </div>

                  <h2 className="mt-5 text-xl font-semibold text-gray-900">
                    How can I help?
                  </h2>

                  <p className="mt-2 text-sm leading-6 text-gray-500">
                    Ask about your sales, customers, products, credit,
                    inventory, or other business data.
                  </p>

                </div>
              </div>
            ) : (
              chatHistory.map((entry, index) => (
                <div key={index} className="space-y-4">

                  <div className="flex justify-end">
                    <div className="max-w-[80%] rounded-2xl rounded-br-md bg-blue-600 px-5 py-3 text-sm leading-6 text-white">
                      {entry.question}
                    </div>
                  </div>

                  <div className="flex items-start gap-3">
                    <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-blue-50 text-lg">
                      🤖
                    </div>

                    <div className="max-w-[80%] rounded-2xl rounded-bl-md bg-gray-50 px-5 py-4 text-sm leading-6 text-gray-800">
                      {displayAnswer(entry.answer)}
                    </div>
                  </div>

                </div>
              ))
            )}

            {loading && (
              <div className="flex items-start gap-3">
                <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-blue-50 text-lg">
                  🤖
                </div>

                <div className="rounded-2xl rounded-bl-md bg-gray-50 px-5 py-4">
                  <div className="flex gap-1.5">
                    <span className="h-2 w-2 animate-bounce rounded-full bg-gray-400" />
                    <span className="h-2 w-2 animate-bounce rounded-full bg-gray-400 [animation-delay:150ms]" />
                    <span className="h-2 w-2 animate-bounce rounded-full bg-gray-400 [animation-delay:300ms]" />
                  </div>
                </div>
              </div>
            )}

            {error && (
              <div className="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
                {error}
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          <div className="border-t border-gray-100 bg-white p-4">
            <form
              onSubmit={(e) => {
                e.preventDefault();
                askCopilot();
              }}
              className="flex items-end gap-3"
            >
              <textarea
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === "Enter" && !e.shiftKey) {
                    e.preventDefault();
                    askCopilot();
                  }
                }}
                placeholder="Ask a question about your business..."
                rows={1}
                disabled={loading}
                className="min-h-[48px] flex-1 resize-none rounded-xl border border-gray-200 bg-gray-50 px-4 py-3 text-sm outline-none transition focus:border-blue-500 focus:bg-white focus:ring-2 focus:ring-blue-100 disabled:cursor-not-allowed disabled:opacity-60"
              />

              <button
                type="submit"
                disabled={!question.trim() || loading}
                className="flex h-12 items-center justify-center rounded-xl bg-blue-600 px-5 text-sm font-semibold text-white transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:bg-gray-300"
              >
                {loading ? "Thinking..." : "Ask"}
              </button>
            </form>

            <p className="mt-2 text-center text-xs text-gray-400">
              Press Enter to send • Shift + Enter for a new line
            </p>
          </div>

        </div>
      </div>
    </main>
  );
}