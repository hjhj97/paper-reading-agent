"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { api, SessionSummary } from "@/lib/api";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import {
  History,
  FileText,
  ArrowLeft,
  Loader2,
  CheckCircle,
  Circle,
  AlertCircle,
} from "lucide-react";

export default function HistoryPage() {
  const router = useRouter();
  const [sessions, setSessions] = useState<SessionSummary[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string>("");

  useEffect(() => {
    const fetchSessions = async () => {
      try {
        const data = await api.getAllSessions();
        setSessions(data);
      } catch (err: any) {
        setError(err.response?.data?.detail || "Failed to load history");
      } finally {
        setIsLoading(false);
      }
    };

    fetchSessions();
  }, []);

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleString("en-US", {
      year: "numeric",
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  const formatFileSize = (length: number) => {
    if (length < 1000) return `${length} chars`;
    if (length < 1000000) return `${(length / 1000).toFixed(1)}K chars`;
    return `${(length / 1000000).toFixed(1)}M chars`;
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-background to-muted/20">
      <div className="container mx-auto px-4 py-8 max-w-6xl">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-3">
              <History className="h-8 w-8 text-primary" />
              <h1 className="text-4xl font-bold">Paper History</h1>
            </div>
            <Button onClick={() => router.push("/")} variant="outline">
              <ArrowLeft className="mr-2 h-4 w-4" />
              Back to Home
            </Button>
          </div>
          <p className="text-muted-foreground">
            View all your uploaded papers and their summaries
          </p>
        </div>

        {/* Loading State */}
        {isLoading && (
          <Card>
            <CardContent className="flex items-center justify-center p-12">
              <div className="text-center space-y-3">
                <Loader2 className="h-10 w-10 text-primary mx-auto animate-spin" />
                <p className="text-muted-foreground">Loading history...</p>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Error State */}
        {error && !isLoading && (
          <Card>
            <CardContent className="p-8 text-center space-y-4">
              <AlertCircle className="h-12 w-12 text-destructive mx-auto" />
              <div className="text-destructive font-semibold">{error}</div>
            </CardContent>
          </Card>
        )}

        {/* Sessions List */}
        {!isLoading && !error && sessions.length === 0 && (
          <Card>
            <CardContent className="p-12 text-center space-y-4">
              <FileText className="h-16 w-16 text-muted-foreground/50 mx-auto" />
              <div>
                <h3 className="text-lg font-semibold mb-2">No papers yet</h3>
                <p className="text-muted-foreground">
                  Upload your first research paper to get started!
                </p>
              </div>
              <Button onClick={() => router.push("/")}>
                Upload Paper
              </Button>
            </CardContent>
          </Card>
        )}

        {!isLoading && !error && sessions.length > 0 && (
          <div className="space-y-4">
            <div className="text-sm text-muted-foreground mb-4">
              Total papers: {sessions.length}
            </div>

            {sessions.map((session) => (
              <Card
                key={session.session_id}
                className="hover:shadow-lg transition-shadow cursor-pointer"
                onClick={() => router.push(`/paper/${session.session_id}`)}
              >
                <CardHeader>
                  <div className="flex justify-between items-start gap-4">
                    <div className="flex-1">
                      <CardTitle className="flex items-center gap-2 mb-2">
                        <FileText className="h-5 w-5 text-primary" />
                        {session.filename}
                      </CardTitle>
                      <div className="flex flex-wrap gap-3 text-sm text-muted-foreground">
                        <div className="flex items-center gap-1">
                          {session.has_summary ? (
                            <>
                              <CheckCircle className="h-4 w-4 text-green-500" />
                              <span>Summary generated</span>
                            </>
                          ) : (
                            <>
                              <Circle className="h-4 w-4" />
                              <span>No summary yet</span>
                            </>
                          )}
                        </div>
                        <div>📅 {formatDate(session.created_at)}</div>
                        <div>📄 {formatFileSize(session.text_length)}</div>
                      </div>
                    </div>
                    <div className="text-xs bg-primary/10 text-primary px-2 py-1 rounded">
                      {session.session_id.slice(0, 8)}...
                    </div>
                  </div>
                </CardHeader>
              </Card>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

