"use client";

import { useState, useEffect } from "react";
import { api, ModelInfo } from "@/lib/api";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Select } from "@/components/ui/select";
import { Bot, Loader2 } from "lucide-react";

interface ModelSelectorProps {
  selectedModel: string;
  onModelChange: (model: string) => void;
}

export default function ModelSelector({
  selectedModel,
  onModelChange,
}: ModelSelectorProps) {
  const [models, setModels] = useState<ModelInfo[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchModels = async () => {
      try {
        const modelList = await api.getModels();
        setModels(modelList);
      } catch (err) {
        console.error("Failed to fetch models:", err);
        // Set default models as fallback
        setModels([{ id: "gpt-5-mini", name: "GPT-5 Mini", is_default: true }]);
      } finally {
        setIsLoading(false);
      }
    };

    fetchModels();
  }, []);

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Bot className="h-5 w-5" />
          Select AI Model
        </CardTitle>
        <CardDescription>
          Choose the language model for summarization and Q&A
        </CardDescription>
      </CardHeader>
      <CardContent>
        {isLoading ? (
          <div className="flex items-center gap-2 text-muted-foreground">
            <Loader2 className="h-4 w-4 animate-spin" />
            Loading models...
          </div>
        ) : (
          <Select
            value={selectedModel}
            onChange={(e) => onModelChange(e.target.value)}
          >
            {models.map((model) => (
              <option key={model.id} value={model.id}>
                {model.name} {model.is_default ? "(Default)" : ""}
              </option>
            ))}
          </Select>
        )}
      </CardContent>
    </Card>
  );
}
