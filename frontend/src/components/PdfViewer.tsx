"use client";

interface PdfViewerProps {
  pdfUrl: string;
  filename: string;
}

export default function PdfViewer({ pdfUrl, filename }: PdfViewerProps) {
  return (
    <div className="card">
      <h2>📄 {filename}</h2>

      {/* PDF Viewer using iframe */}
      <div
        style={{
          width: "100%",
          height: "700px",
          background: "#e5e7eb",
          borderRadius: "4px",
          overflow: "hidden",
        }}
      >
        <iframe
          src={`${pdfUrl}#toolbar=1&navpanes=1&scrollbar=1`}
          style={{
            width: "100%",
            height: "100%",
            border: "none",
          }}
          title={filename}
        />
      </div>

      <p
        style={{
          marginTop: "0.5rem",
          color: "#666",
          fontSize: "0.9rem",
          textAlign: "center",
        }}
      >
        PDF viewer powered by your browser.
      </p>
    </div>
  );
}
