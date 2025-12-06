"use client";

import { useState, useRef, useEffect } from "react";
import { api } from "@/lib/api";

interface Message {
  role: "user" | "assistant";
  content: string;
  sources?: string[];
  isStreaming?: boolean;
}

interface ChatInterfaceProps {
  sessionId: string;
  selectedModel: string;
}

export default function ChatInterface({
  sessionId,
  selectedModel,
}: ChatInterfaceProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [question, setQuestion] = useState<string>("");
  const [isAsking, setIsAsking] = useState(false);
  const [error, setError] = useState<string>("");
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleAsk = async () => {
    if (!question.trim()) return;

    const userMessage: Message = {
      role: "user",
      content: question,
    };

    setMessages((prev) => [
      ...prev,
      userMessage,
      {
        role: "assistant",
        content: "",
        sources: [],
        isStreaming: true,
      },
    ]);

    const currentQuestion = question;
    setQuestion("");
    setIsAsking(true);
    setError("");

    try {
      await api.askStream(
        sessionId,
        currentQuestion,
        selectedModel,
        // onChunk: append content
        (content: string) => {
          console.log("[ChatInterface] onChunk called with:", content);
          setMessages((prev) => {
            const newMessages = [...prev];
            const lastIdx = newMessages.length - 1;

            if (
              newMessages[lastIdx] &&
              newMessages[lastIdx].role === "assistant"
            ) {
              // Create a new object instead of mutating
              newMessages[lastIdx] = {
                ...newMessages[lastIdx],
                content: newMessages[lastIdx].content + content,
                isStreaming: true,
              };
              console.log(
                "[ChatInterface] Updated message:",
                newMessages[lastIdx].content
              );
            }
            return newMessages;
          });
        },
        // onSources: set sources
        (sources: string[]) => {
          setMessages((prev) => {
            const newMessages = [...prev];
            const lastIdx = newMessages.length - 1;

            if (
              newMessages[lastIdx] &&
              newMessages[lastIdx].role === "assistant"
            ) {
              // Create a new object instead of mutating
              newMessages[lastIdx] = {
                ...newMessages[lastIdx],
                sources: sources,
              };
            }
            return newMessages;
          });
        },
        // onComplete: mark streaming as done
        () => {
          setMessages((prev) => {
            const newMessages = [...prev];
            const lastIdx = newMessages.length - 1;

            if (
              newMessages[lastIdx] &&
              newMessages[lastIdx].role === "assistant"
            ) {
              // Create a new object instead of mutating
              newMessages[lastIdx] = {
                ...newMessages[lastIdx],
                isStreaming: false,
              };
            }
            return newMessages;
          });
          setIsAsking(false);
        },
        // onError: show error and remove assistant message
        (errorMsg: string) => {
          setError(errorMsg);
          setMessages((prev) => prev.slice(0, -1));
          setIsAsking(false);
        }
      );
    } catch (err: any) {
      setError(err.message || "Failed to get answer");
      setMessages((prev) => prev.slice(0, -1));
      setIsAsking(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleAsk();
    }
  };

  return (
    <div className="card">
      <h2>💬 Ask Questions About the Paper</h2>

      {error && <div className="error">{error}</div>}

      <div
        style={{
          background: "#f9fafb",
          borderRadius: "4px",
          padding: "1rem",
          marginBottom: "1rem",
          minHeight: "300px",
          maxHeight: "500px",
          overflowY: "auto",
        }}
      >
        {messages.length === 0 ? (
          <p
            style={{ color: "#9ca3af", textAlign: "center", marginTop: "2rem" }}
          >
            Ask any question about the paper...
          </p>
        ) : (
          <>
            {messages.map((message, index) => (
              <div
                key={index}
                style={{
                  marginBottom: "1rem",
                  padding: "1rem",
                  borderRadius: "4px",
                  background: message.role === "user" ? "#dbeafe" : "#ffffff",
                  border:
                    message.role === "assistant" ? "1px solid #e5e7eb" : "none",
                }}
              >
                <div style={{ fontWeight: "bold", marginBottom: "0.5rem" }}>
                  {message.role === "user" ? "👤 You" : "🤖 Assistant"}
                  {message.isStreaming && (
                    <span
                      style={{
                        marginLeft: "0.5rem",
                        color: "#10b981",
                        fontSize: "0.9rem",
                      }}
                    >
                      ●
                    </span>
                  )}
                </div>
                <div style={{ whiteSpace: "pre-wrap", lineHeight: "1.6" }}>
                  {message.content}
                  {message.isStreaming && (
                    <span
                      style={{
                        display: "inline-block",
                        width: "8px",
                        height: "16px",
                        background: "#2563eb",
                        marginLeft: "2px",
                        animation: "blink 1s infinite",
                      }}
                    />
                  )}
                </div>
                {message.sources && message.sources.length > 0 && (
                  <div
                    style={{
                      marginTop: "0.5rem",
                      fontSize: "0.85rem",
                      color: "#6b7280",
                      fontStyle: "italic",
                    }}
                  >
                    Sources: {message.sources.join(", ")}
                  </div>
                )}
              </div>
            ))}
            <div ref={messagesEndRef} />
          </>
        )}
      </div>

      <div style={{ display: "flex", gap: "0.5rem" }}>
        <input
          type="text"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Ask a question about the paper..."
          disabled={isAsking}
          style={{ marginBottom: 0, flex: 1 }}
        />
        <button
          onClick={handleAsk}
          disabled={isAsking || !question.trim()}
          style={{ marginBottom: 0 }}
        >
          {isAsking ? "Asking..." : "Ask"}
        </button>
      </div>

      <style jsx>{`
        @keyframes blink {
          0%,
          49% {
            opacity: 1;
          }
          50%,
          100% {
            opacity: 0;
          }
        }
      `}</style>
    </div>
  );
}
