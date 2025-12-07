"use client";

import { Viewer, Worker } from '@react-pdf-viewer/core';
import { defaultLayoutPlugin } from '@react-pdf-viewer/default-layout';

// Import styles
import '@react-pdf-viewer/core/lib/styles/index.css';
import '@react-pdf-viewer/default-layout/lib/styles/index.css';

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
  // Create default layout plugin instance with toolbar, sidebar, etc.
  const defaultLayoutPluginInstance = defaultLayoutPlugin({
    sidebarTabs: (defaultTabs) => [
      defaultTabs[0], // Thumbnails
      defaultTabs[1], // Bookmarks
    ],
  });

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <FileText className="h-5 w-5" />
          {filename}
        </CardTitle>
        <CardDescription>
          Interactive PDF viewer with search, zoom, and navigation
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="w-full h-[750px] border rounded-lg overflow-hidden bg-background">
          <Worker workerUrl="https://unpkg.com/pdfjs-dist@3.11.174/build/pdf.worker.min.js">
            <Viewer 
              fileUrl={pdfUrl}
              plugins={[defaultLayoutPluginInstance]}
              defaultScale={1.2}
            />
          </Worker>
        </div>
      </CardContent>
    </Card>
  );
}
