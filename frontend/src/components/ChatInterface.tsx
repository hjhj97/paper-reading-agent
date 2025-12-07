"use client";

import { useState, useRef, useEffect } from "react";
import { api } from "@/lib/api";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  MessageCircle,
  Send,
  User,
  Bot,
  Loader2,
  AlertCircle,
} from "lucide-react";

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
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <MessageCircle className="h-5 w-5" />
          Ask Questions About the Paper
        </CardTitle>
        <CardDescription>
          Get instant answers from the paper using AI
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {error && (
          <div className="flex items-center gap-2 p-3 text-sm text-destructive bg-destructive/10 border border-destructive/20 rounded-md">
            <AlertCircle className="h-4 w-4" />
            {error}
          </div>
        )}

        <div className="bg-muted/30 rounded-lg p-4 min-h-[300px] max-h-[500px] overflow-y-auto border">
          {messages.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full text-center space-y-3 py-12">
              <MessageCircle className="h-12 w-12 text-muted-foreground/50" />
              <p className="text-muted-foreground">
                Ask any question about the paper...
              </p>
              <p className="text-xs text-muted-foreground">
                Try asking about methodology, results, or conclusions
              </p>
            </div>
          ) : (
            <div className="space-y-4">
              {messages.map((message, index) => (
                <div
                  key={index}
                  className={`flex gap-3 ${
                    message.role === "user" ? "justify-end" : "justify-start"
                  }`}
                >
                  {message.role === "assistant" && (
                    <div className="flex-shrink-0">
                      <div className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center">
                        <Bot className="h-5 w-5 text-primary" />
                      </div>
                    </div>
                  )}

                  <div
                    className={`flex-1 max-w-[80%] ${
                      message.role === "user" ? "text-right" : ""
                    }`}
                  >
                    <div
                      className={`inline-block p-3 rounded-lg ${
                        message.role === "user"
                          ? "bg-primary text-primary-foreground"
                          : "bg-background border"
                      }`}
                    >
                      <div className="flex items-center gap-2 mb-1">
                        <span className="text-xs font-medium opacity-70">
                          {message.role === "user" ? "You" : "Assistant"}
                        </span>
                        {message.isStreaming && (
                          <Loader2 className="h-3 w-3 animate-spin text-green-500" />
                        )}
                      </div>

                      <div className="text-sm markdown">
                        {message.role === "assistant" ? (
                          <ReactMarkdown remarkPlugins={[remarkGfm]}>
                            {message.content}
                          </ReactMarkdown>
                        ) : (
                          <p className="whitespace-pre-wrap">
                            {message.content}
                          </p>
                        )}
                        {message.isStreaming && (
                          <span className="inline-block w-2 h-4 bg-current ml-1 animate-pulse" />
                        )}
                      </div>

                      {message.sources && message.sources.length > 0 && (
                        <div className="mt-2 pt-2 border-t border-current/20">
                          <p className="text-xs opacity-70 italic">
                            Sources: {message.sources.join(", ")}
                          </p>
                        </div>
                      )}
                    </div>
                  </div>

                  {message.role === "user" && (
                    <div className="flex-shrink-0">
                      <div className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center">
                        <User className="h-5 w-5 text-primary" />
                      </div>
                    </div>
                  )}
                </div>
              ))}
              <div ref={messagesEndRef} />
            </div>
          )}
        </div>

        <div className="flex gap-2">
          <Input
            type="text"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Ask a question about the paper..."
            disabled={isAsking}
            className="flex-1"
          />
          <Button
            onClick={handleAsk}
            disabled={isAsking || !question.trim()}
            size="icon"
          >
            {isAsking ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <Send className="h-4 w-4" />
            )}
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
