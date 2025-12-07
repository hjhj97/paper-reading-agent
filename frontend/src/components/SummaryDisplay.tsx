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
import { Textarea } from "@/components/ui/textarea";
import {
  FileText,
  Loader2,
  ThumbsUp,
  ThumbsDown,
  Sparkles,
  AlertCircle,
} from "lucide-react";

interface SummaryDisplayProps {
  sessionId: string;
  selectedModel: string;
  selectedLanguage: string;
  onSummaryGenerated: () => void;
  autoSummarize?: boolean;
  initialSummary?: string | null;
}

export default function SummaryDisplay({
  sessionId,
  selectedModel,
  selectedLanguage,
  onSummaryGenerated,
  autoSummarize = false,
  initialSummary = null,
}: SummaryDisplayProps) {
  const [summary, setSummary] = useState<string>(initialSummary || "");
  const [customPrompt, setCustomPrompt] = useState<string>("");
  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState<string>("");
  const [rating, setRating] = useState<string>("");
  const [showRegenerate, setShowRegenerate] = useState(false);

  // Auto-summarize on mount if enabled and no existing summary
  useEffect(() => {
    if (autoSummarize && !initialSummary && !summary && !isGenerating) {
      handleGenerateSummary();
    }
  }, [autoSummarize, initialSummary]);

  // Update summary if initialSummary changes
  useEffect(() => {
    if (initialSummary) {
      setSummary(initialSummary);
      onSummaryGenerated();
    }
  }, [initialSummary]);

  const handleGenerateSummary = async () => {
    setIsGenerating(true);
    setError("");
    setSummary("");
    setRating("");

    // Add language instruction to custom prompt
    let finalPrompt = customPrompt;
    if (selectedLanguage === "ko" && !customPrompt) {
      finalPrompt =
        "Please provide the summary in Korean (한국어로 요약해주세요).";
    } else if (selectedLanguage === "ko" && customPrompt) {
      finalPrompt = `${customPrompt}\n\nPlease respond in Korean (한국어로 응답해주세요).`;
    }

    try {
      const response = await api.summarize(
        sessionId,
        finalPrompt || undefined,
        selectedModel
      );
      setSummary(response.summary);
      onSummaryGenerated();
      setShowRegenerate(false);
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to generate summary");
    } finally {
      setIsGenerating(false);
    }
  };

  const handleRate = async (ratingType: "thumbs_up" | "thumbs_down") => {
    try {
      await api.rate(sessionId, ratingType);
      setRating(ratingType);
    } catch (err: any) {
      console.error("Failed to rate:", err);
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <FileText className="h-5 w-5" />
          Paper Summary
        </CardTitle>
        <CardDescription>
          AI-generated summary of the research paper
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {error && (
          <div className="flex items-center gap-2 p-3 text-sm text-destructive bg-destructive/10 border border-destructive/20 rounded-md">
            <AlertCircle className="h-4 w-4" />
            {error}
          </div>
        )}

        {isGenerating && (
          <div className="text-center p-8 bg-primary/5 rounded-lg space-y-3">
            <Loader2 className="h-10 w-10 text-primary mx-auto animate-spin" />
            <p className="font-semibold text-primary">
              {selectedLanguage === "ko"
                ? "요약 생성 중..."
                : "Generating summary..."}
            </p>
            <p className="text-sm text-muted-foreground">
              {selectedLanguage === "ko"
                ? "논문 길이에 따라 시간이 걸릴 수 있습니다."
                : "This may take a moment depending on the paper length."}
            </p>
          </div>
        )}

        {!isGenerating && !summary && (
          <div className="space-y-4">
            <div className="space-y-2">
              <label className="text-sm font-medium">
                {selectedLanguage === "ko"
                  ? "커스텀 프롬프트 (선택사항)"
                  : "Custom Prompt (Optional)"}
              </label>
              <Textarea
                value={customPrompt}
                onChange={(e) => setCustomPrompt(e.target.value)}
                placeholder={
                  selectedLanguage === "ko"
                    ? "요약을 안내할 커스텀 프롬프트를 입력하세요 (예: '방법론과 결과에 집중해주세요')..."
                    : "Enter a custom prompt to guide the summarization (e.g., 'Focus on the methodology and results')..."
                }
                rows={4}
              />
            </div>

            <Button onClick={handleGenerateSummary} className="w-full">
              <Sparkles className="mr-2 h-4 w-4" />
              {selectedLanguage === "ko" ? "요약 생성" : "Generate Summary"}
            </Button>
          </div>
        )}

        {summary && (
          <div className="space-y-4">
            <div className="markdown bg-muted/30 p-6 rounded-lg border">
              <ReactMarkdown
                remarkPlugins={[remarkGfm, remarkMath]}
                rehypePlugins={[rehypeKatex]}
              >
                {normalizeMathNotation(summary)}
              </ReactMarkdown>
            </div>

            <div className="flex items-center gap-3 flex-wrap">
              <span className="text-sm font-medium">
                {selectedLanguage === "ko"
                  ? "이 요약을 평가하세요:"
                  : "Rate this summary:"}
              </span>
              <Button
                onClick={() => handleRate("thumbs_up")}
                variant={rating === "thumbs_up" ? "default" : "outline"}
                size="sm"
                className={
                  rating === "thumbs_up"
                    ? "bg-green-600 hover:bg-green-700"
                    : ""
                }
              >
                <ThumbsUp className="mr-1.5 h-3.5 w-3.5" />
                {selectedLanguage === "ko" ? "좋음" : "Good"}
              </Button>
              <Button
                onClick={() => handleRate("thumbs_down")}
                variant={rating === "thumbs_down" ? "default" : "outline"}
                size="sm"
                className={
                  rating === "thumbs_down" ? "bg-red-600 hover:bg-red-700" : ""
                }
              >
                <ThumbsDown className="mr-1.5 h-3.5 w-3.5" />
                {selectedLanguage === "ko" ? "나쁨" : "Not Good"}
              </Button>
              {rating && (
                <span className="text-sm text-muted-foreground">
                  {selectedLanguage === "ko"
                    ? "피드백 감사합니다!"
                    : "Thank you for your feedback!"}
                </span>
              )}
            </div>

            <div className="pt-4 border-t space-y-3">
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setShowRegenerate(!showRegenerate)}
                className="w-full justify-start"
              >
                <Sparkles className="mr-2 h-4 w-4" />
                {selectedLanguage === "ko"
                  ? "커스텀 프롬프트로 재생성"
                  : "Regenerate with custom prompt"}
              </Button>

              {showRegenerate && (
                <div className="space-y-3 pl-6">
                  <Textarea
                    value={customPrompt}
                    onChange={(e) => setCustomPrompt(e.target.value)}
                    placeholder={
                      selectedLanguage === "ko"
                        ? "커스텀 프롬프트를 입력하세요..."
                        : "Enter a custom prompt..."
                    }
                    rows={3}
                  />
                  <Button
                    onClick={handleGenerateSummary}
                    disabled={isGenerating}
                    size="sm"
                  >
                    {isGenerating ? (
                      <>
                        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                        {selectedLanguage === "ko"
                          ? "재생성 중..."
                          : "Regenerating..."}
                      </>
                    ) : (
                      <>
                        <Sparkles className="mr-2 h-4 w-4" />
                        {selectedLanguage === "ko" ? "재생성" : "Regenerate"}
                      </>
                    )}
                  </Button>
                </div>
              )}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
