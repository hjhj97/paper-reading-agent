"use client";

import { useRouter } from "next/navigation";
import PdfUploader from "@/components/PdfUploader";

export default function Home() {
  const router = useRouter();

  const handleUploadSuccess = (newSessionId: string) => {
    // Navigate to paper detail page after upload
    router.push(`/paper/${newSessionId}`);
  };

  return (
    <div className="container">
      <div className="header">
        <h1>📄 Paper Reading Agent</h1>
        <p>AI-powered paper summarization and Q&A system</p>
      </div>

      <PdfUploader onUploadSuccess={handleUploadSuccess} />

      <div className="card" style={{ textAlign: "center", color: "#666" }}>
        <h3>How it works</h3>
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))",
            gap: "1.5rem",
            marginTop: "1.5rem",
          }}
        >
          <div>
            <div style={{ fontSize: "2rem", marginBottom: "0.5rem" }}>📤</div>
            <h4>1. Upload PDF</h4>
            <p style={{ fontSize: "0.9rem" }}>
              Upload your research paper in PDF format
            </p>
          </div>
          <div>
            <div style={{ fontSize: "2rem", marginBottom: "0.5rem" }}>🤖</div>
            <h4>2. AI Summary</h4>
            <p style={{ fontSize: "0.9rem" }}>
              Get an AI-generated summary of the paper
            </p>
          </div>
          <div>
            <div style={{ fontSize: "2rem", marginBottom: "0.5rem" }}>💬</div>
            <h4>3. Ask Questions</h4>
            <p style={{ fontSize: "0.9rem" }}>
              Ask questions and get answers from the paper
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
