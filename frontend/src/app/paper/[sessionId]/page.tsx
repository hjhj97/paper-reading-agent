"use client";

import { useState, useEffect } from "react";
import { useParams, useRouter } from "next/navigation";
import { api, SessionDetail, getPdfUrl } from "@/lib/api";
import ModelSelector from "@/components/ModelSelector";
import LanguageSelector from "@/components/LanguageSelector";
import SummaryDisplay from "@/components/SummaryDisplay";
import StorylineDisplay from "@/components/StorylineDisplay";
import ChatInterface from "@/components/ChatInterface";
import PdfViewer from "@/components/PdfViewer";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import {
  ArrowLeft,
  Loader2,
  FileText,
  ChevronDown,
  ChevronUp,
  AlertCircle,
  History,
} from "lucide-react";

export default function PaperPage() {
  const params = useParams();
  const router = useRouter();
  const sessionId = params.sessionId as string;

  const [session, setSession] = useState<SessionDetail | null>(null);
  const [selectedModel, setSelectedModel] = useState<string>(
    typeof window !== "undefined"
      ? localStorage.getItem("preferredModel") || "gpt-4o-mini"
      : "gpt-4o-mini"
  );
  const [selectedLanguage, setSelectedLanguage] = useState<string>(
    typeof window !== "undefined"
      ? localStorage.getItem("preferredLanguage") || "en"
      : "en"
  );
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
      <div className="min-h-screen bg-gradient-to-b from-background to-muted/20">
        <div className="container mx-auto px-4 py-8 max-w-6xl">
          <Card>
            <CardContent className="flex items-center justify-center p-12">
              <div className="text-center space-y-3">
                <Loader2 className="h-10 w-10 text-primary mx-auto animate-spin" />
                <p className="text-muted-foreground">Loading paper...</p>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }

  if (error || !session) {
    return (
      <div className="min-h-screen bg-gradient-to-b from-background to-muted/20">
        <div className="container mx-auto px-4 py-8 max-w-6xl">
          <Card>
            <CardContent className="p-8 text-center space-y-4">
              <AlertCircle className="h-12 w-12 text-destructive mx-auto" />
              <div className="text-destructive font-semibold">
                {error || "Paper not found"}
              </div>
              <Button onClick={() => router.push("/")} variant="outline">
                <ArrowLeft className="mr-2 h-4 w-4" />
                Go Back Home
              </Button>
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-background to-muted/20">
      <div className="container mx-auto px-4 py-8 max-w-6xl space-y-6">
        {/* Header */}
        <div className="space-y-4">
          <div className="flex justify-between items-center">
            <Button
              onClick={() => router.push("/")}
              variant="outline"
              size="sm"
            >
              <ArrowLeft className="mr-2 h-4 w-4" />
              Home
            </Button>
            <h1 className="text-4xl font-bold bg-gradient-to-r from-primary to-blue-600 bg-clip-text text-transparent">
              📄 Paper Reading Agent
            </h1>
            <Button
              onClick={() => router.push("/history")}
              variant="outline"
              size="sm"
            >
              <History className="mr-2 h-4 w-4" />
              History
            </Button>
          </div>
          <p className="text-center text-muted-foreground">
            AI-powered paper summarization and Q&A system
          </p>
        </div>

        {/* Paper Info */}
        <Card>
          <CardHeader>
            <div className="flex justify-between items-start gap-4">
              <div className="flex-1 space-y-3">
                {/* Title and Year */}
                <div>
                  <CardTitle className="flex items-start gap-2 text-2xl leading-tight">
                    <FileText className="h-6 w-6 mt-1 flex-shrink-0" />
                    <span>
                      {session.title || session.filename}
                      {session.year && session.year !== "Unknown" && (
                        <span className="text-muted-foreground ml-2">
                          ({session.year})
                        </span>
                      )}
                    </span>
                  </CardTitle>
                </div>

                {/* Authors */}
                {session.authors && session.authors !== "Unknown" && (
                  <div className="text-base text-muted-foreground pl-8">
                    {session.authors}
                  </div>
                )}

                {/* Metadata */}
                <div className="flex flex-wrap gap-4 text-sm text-muted-foreground/80 pl-8">
                  <div>
                    Session ID:{" "}
                    <code className="bg-muted px-2 py-1 rounded text-xs">
                      {session.session_id}
                    </code>
                  </div>
                  <div>
                    Uploaded: {new Date(session.created_at).toLocaleString()}
                  </div>
                </div>
              </div>
            </div>
          </CardHeader>
        </Card>

        {/* PDF Viewer or Raw Text */}
        {session.has_pdf ? (
          <>
            <PdfViewer
              pdfUrl={getPdfUrl(sessionId)}
              filename={session.filename}
            />

            {/* Toggle to show raw text */}
            <Card>
              <CardContent className="p-4">
                <Button
                  onClick={() => setShowRawText(!showRawText)}
                  variant="ghost"
                  className="w-full"
                >
                  {showRawText ? (
                    <>
                      <ChevronUp className="mr-2 h-4 w-4" />
                      Hide Extracted Text
                    </>
                  ) : (
                    <>
                      <ChevronDown className="mr-2 h-4 w-4" />
                      Show Extracted Text
                    </>
                  )}
                </Button>

                {showRawText && (
                  <div className="mt-4 bg-muted/30 p-6 rounded-lg max-h-[400px] overflow-y-auto border">
                    <pre className="whitespace-pre-wrap font-serif text-sm leading-relaxed">
                      {session.text}
                    </pre>
                  </div>
                )}
              </CardContent>
            </Card>
          </>
        ) : (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <FileText className="h-5 w-5" />
                Paper Content
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="bg-muted/30 p-6 rounded-lg max-h-[400px] overflow-y-auto border">
                <pre className="whitespace-pre-wrap font-serif text-sm leading-relaxed">
                  {session.text}
                </pre>
              </div>
              <p className="mt-3 text-sm text-muted-foreground">
                Total characters: {session.text.length.toLocaleString()}
              </p>
            </CardContent>
          </Card>
        )}

        {/* Settings */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <ModelSelector
            selectedModel={selectedModel}
            onModelChange={setSelectedModel}
          />
          <LanguageSelector
            selectedLanguage={selectedLanguage}
            onLanguageChange={setSelectedLanguage}
          />
        </div>

        {/* Storyline Analysis */}
        <StorylineDisplay
          sessionId={sessionId}
          selectedModel={selectedModel}
          selectedLanguage={selectedLanguage}
          autoAnalyze={true}
          initialStoryline={session.storyline}
        />

        {/* Summary Display */}
        <SummaryDisplay
          sessionId={sessionId}
          selectedModel={selectedModel}
          selectedLanguage={selectedLanguage}
          onSummaryGenerated={handleSummaryGenerated}
          autoSummarize={true}
          initialSummary={session.summary}
        />

        {/* Chat Interface (only shown after summary is generated) */}
        {hasSummary && (
          <ChatInterface
            sessionId={sessionId}
            selectedModel={selectedModel}
            selectedLanguage={selectedLanguage}
          />
        )}
      </div>
    </div>
  );
}
