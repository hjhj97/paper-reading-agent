"use client";

import { useState } from "react";

interface PdfViewerProps {
  pdfUrl: string;
  filename: string;
}

export default function PdfViewer({ pdfUrl, filename }: PdfViewerProps) {
  const [isLoading, setIsLoading] = useState<boolean>(true);

  return (
    <div className="card">
      <h2>📄 {filename}</h2>

      {/* PDF Viewer using iframe */}
      <div
        style={{
          position: "relative",
          width: "100%",
          height: "700px",
          background: "#e5e7eb",
          borderRadius: "4px",
          overflow: "hidden",
        }}
      >
        {isLoading && (
          <div
            style={{
              position: "absolute",
              top: "50%",
              left: "50%",
              transform: "translate(-50%, -50%)",
              textAlign: "center",
              zIndex: 1,
            }}
          >
            <p>Loading PDF...</p>
          </div>
        )}

        <iframe
          src={`${pdfUrl}#toolbar=1&navpanes=1&scrollbar=1`}
          style={{
            width: "100%",
            height: "100%",
            border: "none",
          }}
          title={filename}
          onLoad={() => setIsLoading(false)}
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
        PDF viewer powered by your browser. If the PDF doesn&apos;t display, try
        the &quot;Open in New Tab&quot; button.
      </p>
    </div>
  );
}
