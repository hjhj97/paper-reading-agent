"use client";

import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Select } from "@/components/ui/select";
import { Languages } from "lucide-react";

interface LanguageSelectorProps {
  selectedLanguage: string;
  onLanguageChange: (language: string) => void;
}

export default function LanguageSelector({
  selectedLanguage,
  onLanguageChange,
}: LanguageSelectorProps) {
  const languages = [
    { code: "en", name: "English (영어)" },
    { code: "ko", name: "Korean (한국어)" },
  ];

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Languages className="h-5 w-5" />
          언어 선택 / Select Language
        </CardTitle>
        <CardDescription>
          AI 응답 언어를 선택하세요 / Choose the language for AI responses
        </CardDescription>
      </CardHeader>
      <CardContent>
        <Select
          value={selectedLanguage}
          onChange={(e) => onLanguageChange(e.target.value)}
        >
          {languages.map((lang) => (
            <option key={lang.code} value={lang.code}>
              {lang.name}
            </option>
          ))}
        </Select>
      </CardContent>
    </Card>
  );
}
