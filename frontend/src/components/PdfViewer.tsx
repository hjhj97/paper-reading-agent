"use client";

import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { FileText } from "lucide-react";

interface PdfViewerProps {
  pdfUrl: string;
  filename: string;
}

export default function PdfViewer({ pdfUrl, filename }: PdfViewerProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <FileText className="h-5 w-5" />
          {filename}
        </CardTitle>
        <CardDescription>PDF viewer powered by your browser</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="w-full h-[700px] bg-muted/30 rounded-lg overflow-hidden border">
          <iframe
            src={`${pdfUrl}#toolbar=1&navpanes=1&scrollbar=1`}
            className="w-full h-full border-0"
            title={filename}
          />
        </div>
      </CardContent>
    </Card>
  );
}
