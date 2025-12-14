"use client";

import { useState, useEffect } from "react";
import { api } from "@/lib/api";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import remarkMath from "remark-math";
import rehypeKatex from "rehype-katex";
import { normalizeMathNotation } from "@/lib/mathUtils";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { GitBranch, Loader2, Sparkles, AlertCircle } from "lucide-react";

interface StorylineDisplayProps {
  sessionId: string;
  selectedModel: string;
  selectedLanguage: string;
  autoAnalyze?: boolean;
  initialStoryline?: string | null;
}

export default function StorylineDisplay({
  sessionId,
  selectedModel,
  selectedLanguage,
  autoAnalyze = false,
  initialStoryline = null,
}: StorylineDisplayProps) {
  const [storyline, setStoryline] = useState<string>(initialStoryline || "");
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [error, setError] = useState<string>("");
  const [hasAutoAnalyzed, setHasAutoAnalyzed] = useState(false);

  // Auto-analyze on mount if enabled and no existing storyline
  useEffect(() => {
    // Only auto-analyze once when component mounts
    if (autoAnalyze && !initialStoryline && !storyline && !isAnalyzing && !hasAutoAnalyzed) {
      setHasAutoAnalyzed(true);
      handleAnalyzeStoryline();
    }
  }, [autoAnalyze, initialStoryline, storyline, isAnalyzing, hasAutoAnalyzed]);

  // Update storyline if initialStoryline changes
  useEffect(() => {
    if (initialStoryline) {
      setStoryline(initialStoryline);
    }
  }, [initialStoryline]);

  const handleAnalyzeStoryline = async () => {
    setIsAnalyzing(true);
    setError("");
    setStoryline("");

    try {
      const response = await api.analyzeStoryline(
        sessionId,
        selectedModel,
        selectedLanguage
      );
      setStoryline(response.storyline);
    } catch (err: any) {
      const errorMsg =
        selectedLanguage === "ko"
          ? "스토리라인 분석에 실패했습니다"
          : "Failed to analyze storyline";
      setError(err.response?.data?.detail || errorMsg);
    } finally {
      setIsAnalyzing(false);
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <GitBranch className="h-5 w-5" />
          {selectedLanguage === "ko" ? "논문 스토리라인" : "Paper Storyline"}
        </CardTitle>
        <CardDescription>
          {selectedLanguage === "ko"
            ? "논문의 흐름을 한눈에 파악하세요"
            : "Understand the paper's narrative flow at a glance"}
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {error && (
          <div className="flex items-center gap-2 p-3 text-sm text-destructive bg-destructive/10 border border-destructive/20 rounded-md">
            <AlertCircle className="h-4 w-4" />
            {error}
          </div>
        )}

        {isAnalyzing && (
          <div className="text-center p-8 bg-primary/5 rounded-lg space-y-3">
            <Loader2 className="h-10 w-10 text-primary mx-auto animate-spin" />
            <p className="font-semibold text-primary">
              {selectedLanguage === "ko"
                ? "스토리라인 분석 중..."
                : "Analyzing storyline..."}
            </p>
            <p className="text-sm text-muted-foreground">
              {selectedLanguage === "ko"
                ? "논문의 흐름을 분석하고 있습니다..."
                : "Analyzing the paper's narrative flow..."}
            </p>
          </div>
        )}

        {!isAnalyzing && !storyline && (
          <Button onClick={handleAnalyzeStoryline} className="w-full">
            <Sparkles className="mr-2 h-4 w-4" />
            {selectedLanguage === "ko"
              ? "스토리라인 분석하기"
              : "Analyze Storyline"}
          </Button>
        )}

        {storyline && (
          <div className="space-y-4">
            <div className="markdown bg-gradient-to-br from-primary/5 to-blue-50 dark:from-primary/10 dark:to-blue-900/20 p-6 rounded-lg border-2 border-primary/20">
              <ReactMarkdown
                remarkPlugins={[remarkGfm, remarkMath]}
                rehypePlugins={[rehypeKatex]}
              >
                {normalizeMathNotation(storyline)}
              </ReactMarkdown>
            </div>

            <Button
              onClick={handleAnalyzeStoryline}
              disabled={isAnalyzing}
              variant="outline"
              size="sm"
              className="w-full"
            >
              {isAnalyzing ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  {selectedLanguage === "ko" ? "재분석 중..." : "Reanalyzing..."}
                </>
              ) : (
                <>
                  <Sparkles className="mr-2 h-4 w-4" />
                  {selectedLanguage === "ko" ? "재분석하기" : "Reanalyze"}
                </>
              )}
            </Button>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

