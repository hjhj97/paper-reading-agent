import axios from "axios";

export interface UploadResponse {
  session_id: string;
  filename: string;
  text_length: number;
  message: string;
}

export interface SummarizeResponse {
  session_id: string;
  summary: string;
  model: string;
}

export interface StorylineResponse {
  session_id: string;
  storyline: string;
  model: string;
}

export interface AskResponse {
  session_id: string;
  question: string;
  answer: string;
  sources: string[];
}

export interface RateResponse {
  session_id: string;
  rating: string;
  message: string;
}

export interface ModelInfo {
  id: string;
  name: string;
  is_default: boolean;
}

export interface SessionDetail {
  session_id: string;
  filename: string;
  text: string;
  has_pdf: boolean;
  title: string | null;
  authors: string | null;
  year: string | null;
  summary: string | null;
  storyline: string | null;
  rating: string | null;
  created_at: string;
}

export interface SessionSummary {
  session_id: string;
  filename: string;
  has_pdf: boolean;
  has_summary: boolean;
  title: string | null;
  authors: string | null;
  year: string | null;
  created_at: string;
  text_length: number;
}

// 환경 변수로 API URL 설정 (Docker/프로덕션 환경 지원)
// 로컬 개발: http://localhost:8000/api
// Docker/프로덕션: NEXT_PUBLIC_API_URL 환경변수 사용
export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL
  ? `${process.env.NEXT_PUBLIC_API_URL}/api`
  : "http://localhost:8000/api";

export const getPdfUrl = (sessionId: string): string => {
  return `${API_BASE_URL}/session/${sessionId}/pdf`;
};

export const api = {
  uploadPdf: async (file: File): Promise<UploadResponse> => {
    const formData = new FormData();
    formData.append("file", file);
    const response = await axios.post(`${API_BASE_URL}/upload`, formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });
    return response.data;
  },

  summarize: async (
    sessionId: string,
    customPrompt?: string,
    model?: string
  ): Promise<SummarizeResponse> => {
    const response = await axios.post(`${API_BASE_URL}/summarize`, {
      session_id: sessionId,
      custom_prompt: customPrompt,
      model: model,
    });
    return response.data;
  },

  analyzeStoryline: async (
    sessionId: string,
    model?: string,
    language?: string
  ): Promise<StorylineResponse> => {
    const response = await axios.post(`${API_BASE_URL}/storyline`, {
      session_id: sessionId,
      model: model,
      language: language || "en",
    });
    return response.data;
  },

  ask: async (
    sessionId: string,
    question: string,
    model?: string
  ): Promise<AskResponse> => {
    const response = await axios.post(`${API_BASE_URL}/ask`, {
      session_id: sessionId,
      question: question,
      model: model,
    });
    return response.data;
  },

  rate: async (sessionId: string, rating: string): Promise<RateResponse> => {
    const response = await axios.post(`${API_BASE_URL}/rate`, {
      session_id: sessionId,
      rating: rating,
    });
    return response.data;
  },

  getModels: async (): Promise<ModelInfo[]> => {
    const response = await axios.get(`${API_BASE_URL}/models`);
    return response.data;
  },

  getSession: async (sessionId: string): Promise<SessionDetail> => {
    const response = await axios.get(`${API_BASE_URL}/session/${sessionId}`);
    return response.data;
  },

  getAllSessions: async (): Promise<SessionSummary[]> => {
    const response = await axios.get(`${API_BASE_URL}/sessions`);
    return response.data;
  },

  askStream: async (
    sessionId: string,
    question: string,
    model: string | undefined,
    onChunk: (content: string) => void,
    onSources: (sources: string[]) => void,
    onComplete: () => void,
    onError: (error: string) => void
  ) => {
    try {
      const response = await fetch(`${API_BASE_URL}/ask/stream`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          session_id: sessionId,
          question: question,
          model: model,
        }),
      });

      if (!response.ok) {
        throw new Error("Stream request failed");
      }

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();

      if (!reader) {
        throw new Error("No reader available");
      }

      while (true) {
        const { done, value } = await reader.read();

        if (done) {
          break;
        }

        const chunk = decoder.decode(value);
        const lines = chunk.split("\n");

        for (const line of lines) {
          if (line.startsWith("data: ")) {
            try {
              const data = JSON.parse(line.slice(6));

              if (data.type === "sources") {
                onSources(data.sources);
              } else if (data.type === "content") {
                onChunk(data.content);
              } else if (data.type === "done") {
                onComplete();
              } else if (data.type === "error") {
                onError(data.error);
              }
            } catch (e) {
              // Skip invalid JSON
            }
          }
        }
      }
    } catch (error: any) {
      onError(error.message || "Failed to stream answer");
    }
  },
};
