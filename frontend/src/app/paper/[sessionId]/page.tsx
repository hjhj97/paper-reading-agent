"use client";

import { useState, useEffect } from "react";
import { useParams, useRouter } from "next/navigation";
import { api, SessionDetail, getPdfUrl } from "@/lib/api";
import ModelSelector from "@/components/ModelSelector";
import SummaryDisplay from "@/components/SummaryDisplay";
import ChatInterface from "@/components/ChatInterface";
import PdfViewer from "@/components/PdfViewer";

export default function PaperPage() {
  const params = useParams();
  const router = useRouter();
  const sessionId = params.sessionId as string;

  const [session, setSession] = useState<SessionDetail | null>(null);
  const [selectedModel, setSelectedModel] = useState<string>("gpt-4o-mini");
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string>("");
  const [hasSummary, setHasSummary] = useState<boolean>(false);
  const [showRawText, setShowRawText] = useState<boolean>(false);

  useEffect(() => {
    const fetchSession = async () => {
      if (!sessionId) return;

      try {
        const data = await api.getSession(sessionId);
        setSession(data);
        if (data.summary) {
          setHasSummary(true);
        }
      } catch (err: any) {
        setError(err.response?.data?.detail || "Failed to load paper");
      } finally {
        setIsLoading(false);
      }
    };

    fetchSession();
  }, [sessionId]);

  const handleSummaryGenerated = () => {
    setHasSummary(true);
  };

  if (isLoading) {
    return (
      <div className="container">
        <div className="card">
          <p className="loading">Loading paper...</p>
        </div>
      </div>
    );
  }

  if (error || !session) {
    return (
      <div className="container">
        <div className="card">
          <div className="error">{error || "Paper not found"}</div>
          <button onClick={() => router.push("/")}>Go Back Home</button>
        </div>
      </div>
    );
  }

  return (
    <div className="container">
      <div className="header">
        <h1>📄 Paper Reading Agent</h1>
        <p>AI-powered paper summarization and Q&A system</p>
      </div>

      <div className="card">
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            marginBottom: "1rem",
          }}
        >
          <h2>📑 {session.filename}</h2>
          <button
            onClick={() => router.push("/")}
            style={{ background: "#6b7280", padding: "0.5rem 1rem" }}
          >
            ← Upload New Paper
          </button>
        </div>
        <p style={{ color: "#666", marginBottom: "1rem" }}>
          Session ID:{" "}
          <code
            style={{
              background: "#f3f4f6",
              padding: "0.25rem 0.5rem",
              borderRadius: "4px",
            }}
          >
            {session.session_id}
          </code>
        </p>
        <p style={{ color: "#666" }}>
          Uploaded: {new Date(session.created_at).toLocaleString()}
        </p>
      </div>

      <ModelSelector
        selectedModel={selectedModel}
        onModelChange={setSelectedModel}
      />

      {/* PDF Viewer or Raw Text */}
      {session.has_pdf ? (
        <>
          <PdfViewer
            pdfUrl={getPdfUrl(sessionId)}
            filename={session.filename}
          />

          {/* Toggle to show raw text */}
          <div className="card">
            <button
              onClick={() => setShowRawText(!showRawText)}
              style={{
                background: "#6b7280",
                width: "100%",
                padding: "0.75rem",
              }}
            >
              {showRawText
                ? "🔼 Hide Extracted Text"
                : "🔽 Show Extracted Text"}
            </button>

            {showRawText && (
              <div
                style={{
                  marginTop: "1rem",
                  background: "#f9fafb",
                  padding: "1.5rem",
                  borderRadius: "4px",
                  maxHeight: "400px",
                  overflowY: "auto",
                  lineHeight: "1.8",
                  whiteSpace: "pre-wrap",
                  fontFamily: "Georgia, serif",
                  fontSize: "0.95rem",
                  border: "1px solid #e5e7eb",
                }}
              >
                {session.text}
              </div>
            )}
          </div>
        </>
      ) : (
        <div className="card">
          <h2>📖 Paper Content</h2>
          <div
            style={{
              background: "#f9fafb",
              padding: "1.5rem",
              borderRadius: "4px",
              maxHeight: "400px",
              overflowY: "auto",
              lineHeight: "1.8",
              whiteSpace: "pre-wrap",
              fontFamily: "Georgia, serif",
              fontSize: "0.95rem",
              border: "1px solid #e5e7eb",
            }}
          >
            {session.text}
          </div>
          <p style={{ marginTop: "0.5rem", color: "#666", fontSize: "0.9rem" }}>
            Total characters: {session.text.length.toLocaleString()}
          </p>
        </div>
      )}

      <SummaryDisplay
        sessionId={sessionId}
        selectedModel={selectedModel}
        onSummaryGenerated={handleSummaryGenerated}
        autoSummarize={true}
        initialSummary={session.summary}
      />

      {hasSummary && (
        <ChatInterface sessionId={sessionId} selectedModel={selectedModel} />
      )}
    </div>
  );
}
