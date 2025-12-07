"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import PdfUploader from "@/components/PdfUploader";
import ModelSelector from "@/components/ModelSelector";
import LanguageSelector from "@/components/LanguageSelector";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { FileText, Sparkles, MessageCircle, History } from "lucide-react";

export default function Home() {
  const router = useRouter();
  const [selectedModel, setSelectedModel] = useState<string>("gpt-4o-mini");
  const [selectedLanguage, setSelectedLanguage] = useState<string>("en");

  const handleUploadSuccess = (newSessionId: string) => {
    // Save preferences to localStorage
    localStorage.setItem("preferredModel", selectedModel);
    localStorage.setItem("preferredLanguage", selectedLanguage);

    // Navigate to paper detail page after upload
    router.push(`/paper/${newSessionId}`);
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-background to-muted/20">
      <div className="container mx-auto px-4 py-8 max-w-6xl">
        {/* Header */}
        <div className="text-center mb-12 space-y-4">
          <div className="flex justify-between items-start">
            <div className="flex-1"></div>
            <div className="flex-1 text-center">
              <h1 className="text-5xl font-bold bg-gradient-to-r from-primary to-blue-600 bg-clip-text text-transparent">
                📄 Paper Reading Agent
              </h1>
              <p className="text-xl text-muted-foreground mt-4">
                AI-powered paper summarization and Q&A system
              </p>
            </div>
            <div className="flex-1 flex justify-end">
              <Button
                onClick={() => router.push("/history")}
                variant="outline"
                size="sm"
              >
                <History className="mr-2 h-4 w-4" />
                History
              </Button>
            </div>
          </div>
        </div>

        {/* Settings */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
          <ModelSelector
            selectedModel={selectedModel}
            onModelChange={setSelectedModel}
          />
          <LanguageSelector
            selectedLanguage={selectedLanguage}
            onLanguageChange={setSelectedLanguage}
          />
        </div>

        {/* Uploader */}
        <div className="mb-12">
          <PdfUploader onUploadSuccess={handleUploadSuccess} />
        </div>

        {/* How it works */}
        <Card>
          <CardHeader className="text-center">
            <CardTitle className="text-2xl">How it works</CardTitle>
            <CardDescription>
              Three simple steps to understand any research paper
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="text-center space-y-3 p-4 rounded-lg hover:bg-accent/50 transition-colors">
                <div className="flex justify-center">
                  <div className="p-3 bg-primary/10 rounded-full">
                    <FileText className="h-8 w-8 text-primary" />
                  </div>
                </div>
                <h4 className="font-semibold text-lg">1. Upload PDF</h4>
                <p className="text-sm text-muted-foreground">
                  Upload your research paper in PDF format
                </p>
              </div>

              <div className="text-center space-y-3 p-4 rounded-lg hover:bg-accent/50 transition-colors">
                <div className="flex justify-center">
                  <div className="p-3 bg-primary/10 rounded-full">
                    <Sparkles className="h-8 w-8 text-primary" />
                  </div>
                </div>
                <h4 className="font-semibold text-lg">2. AI Summary</h4>
                <p className="text-sm text-muted-foreground">
                  Get an AI-generated summary of the paper
                </p>
              </div>

              <div className="text-center space-y-3 p-4 rounded-lg hover:bg-accent/50 transition-colors">
                <div className="flex justify-center">
                  <div className="p-3 bg-primary/10 rounded-full">
                    <MessageCircle className="h-8 w-8 text-primary" />
                  </div>
                </div>
                <h4 className="font-semibold text-lg">3. Ask Questions</h4>
                <p className="text-sm text-muted-foreground">
                  Ask questions and get answers from the paper
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
