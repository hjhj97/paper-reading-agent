from openai import OpenAI
from app.config import settings
from typing import Optional
import os

# Langfuse integration via OpenAI wrapper (optional)
LANGFUSE_ENABLED = False
LangfuseOpenAI = None
langfuse_client = None

try:
    if settings.langfuse_secret_key and settings.langfuse_public_key:
        # Set environment variables for Langfuse
        os.environ["LANGFUSE_SECRET_KEY"] = settings.langfuse_secret_key
        os.environ["LANGFUSE_PUBLIC_KEY"] = settings.langfuse_public_key
        os.environ["LANGFUSE_HOST"] = settings.langfuse_host or "https://cloud.langfuse.com"

        from langfuse.openai import OpenAI as _LangfuseOpenAI
        from langfuse import Langfuse
        LangfuseOpenAI = _LangfuseOpenAI
        langfuse_client = Langfuse()
        LANGFUSE_ENABLED = True
        print(f"✅ Langfuse enabled (host: {settings.langfuse_host})")
    else:
        print("ℹ️ Langfuse disabled (API keys not set)")
except Exception as e:
    print(f"ℹ️ Langfuse not available: {e}")


class LLMService:
    """Service for interacting with OpenAI LLM"""
    
    def __init__(self):
        # Standard OpenAI client (always works)
        self.client = OpenAI(api_key=settings.openai_api_key)
        # Langfuse-wrapped client for traced calls (if available)
        if LANGFUSE_ENABLED and LangfuseOpenAI:
            try:
                self.traced_client = LangfuseOpenAI(api_key=settings.openai_api_key)
            except Exception as e:
                print(f"⚠️ Langfuse client init failed: {e}")
                self.traced_client = self.client
        else:
            self.traced_client = self.client
        self.default_model = settings.default_model
    
    def get_available_models(self):
        """
        Get list of available models

        Returns:
            List of model information
        """
        return [
            {
                "id": "gpt-5-mini",
                "name": "GPT-5 Mini",
                "is_default": True
            }
        ]
    
    async def summarize_paper(
        self,
        paper_text: str,
        custom_prompt: Optional[str] = None,
        model: Optional[str] = None
    ) -> str:
        """
        Summarize paper text using LLM
        
        Args:
            paper_text: Full text of the paper
            custom_prompt: Optional custom prompt to guide summarization
            model: Model to use (defaults to configured default)
            
        Returns:
            Summary text
        """
        model_to_use = model or self.default_model
        
        # Default prompt for paper summarization
        default_prompt = """You are an expert academic research assistant specialized in analyzing and summarizing research papers.

Please provide a comprehensive yet concise summary of the following academic paper. Structure your summary with the following sections:

## Overview
- Paper title and main topic
- Research domain/field

## Research Objectives
- Primary research question(s)
- Hypotheses or goals

## Methodology
- Research design and approach
- Data collection methods
- Analysis techniques

## Key Findings
- Main results and discoveries
- Statistical significance (if applicable)
- Notable patterns or trends

## Conclusions & Implications
- Main conclusions drawn
- Practical implications
- Theoretical contributions

## Limitations & Future Work
- Acknowledged limitations
- Suggested future research directions

Keep the summary between 400-600 words. Use clear, academic language while making the content accessible. Focus on the most significant aspects of the research.

IMPORTANT: For mathematical formulas, use proper LaTeX syntax:
- For inline math: $formula$
- For block/display math: $$formula$$ (on separate lines)
- Do NOT use brackets [ ] or \\[ \\] for formulas."""
        
        # Use custom prompt if provided
        system_prompt = custom_prompt if custom_prompt else default_prompt
        
        try:
            # Use traced client for Langfuse logging
            response = self.traced_client.chat.completions.create(
                model=model_to_use,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Paper text:\n\n{paper_text}"}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            summary = response.choices[0].message.content
            return summary
        
        except Exception as e:
            raise Exception(f"Failed to generate summary: {str(e)}")
    
    async def answer_question(
        self,
        question: str,
        context: str,
        model: Optional[str] = None
    ) -> str:
        """
        Answer a question about the paper using RAG context
        
        Args:
            question: User's question
            context: Relevant context from the paper
            model: Model to use (defaults to configured default)
            
        Returns:
            Answer text
        """
        model_to_use = model or self.default_model
        
        system_prompt = """You are a helpful research assistant. Answer the user's question based on the provided context from a research paper.
If the answer is not clearly stated in the context, say so. Always be factual and cite relevant parts of the context."""
        
        user_message = f"""Context from paper:
{context}

Question: {question}

Please provide a clear and concise answer based on the context above."""
        
        try:
            response = self.client.chat.completions.create(
                model=model_to_use,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.5,
                max_tokens=1000
            )
            
            answer = response.choices[0].message.content
            return answer
        
        except Exception as e:
            raise Exception(f"Failed to generate answer: {str(e)}")
    
    def answer_question_stream(
        self,
        question: str,
        context: str,
        model: Optional[str] = None
    ):
        """
        Answer a question about the paper using RAG context with streaming
        
        Args:
            question: User's question
            context: Relevant context from the paper
            model: Model to use (defaults to configured default)
            
        Yields:
            Chunks of answer text
        """
        model_to_use = model or self.default_model
        
        system_prompt = """You are a helpful research assistant. Answer the user's question based on the provided context from a research paper.
If the answer is not clearly stated in the context, say so. Always be factual and cite relevant parts of the context.

IMPORTANT: For mathematical formulas, use proper LaTeX syntax:
- For inline math: $formula$
- For block/display math: $$formula$$ (on separate lines)
- Example: $$f(x) = x^2 + 2x + 1$$
- Do NOT use brackets [ ] or \\[ \\] for formulas."""
        
        user_message = f"""Context from paper:
{context}

Question: {question}

Please provide a clear and concise answer based on the context above. Use $$...$$ for mathematical formulas."""
        
        try:
            # Use traced client for Langfuse logging
            stream = self.traced_client.chat.completions.create(
                model=model_to_use,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.5,
                max_tokens=1000,
                stream=True
            )
            
            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    yield chunk.choices[0].delta.content
        
        except Exception as e:
            raise Exception(f"Failed to generate answer: {str(e)}")
    
    async def analyze_storyline(
        self,
        paper_text: str,
        model: Optional[str] = None,
        language: str = "en"
    ) -> str:
        """
        Analyze the paper's storyline/narrative flow
        
        Args:
            paper_text: Full text of the paper
            model: Model to use (defaults to configured default)
            
        Returns:
            Storyline analysis
        """
        model_to_use = model or self.default_model
        
        # Adjust prompt based on language
        if language == "ko":
            system_prompt = """당신은 연구 논문 분석 전문가입니다. 논문의 스토리라인을 분석하여 정확히 다음 형식으로 답변하세요 (600자 이내):

**문제 제기**
- [논문이 다루는 주요 문제나 연구 공백 설명]

**기존 방법론의 한계**
- [기존 접근법의 한계점 설명]

**본 논문의 방법론**
- [제안된 방법론이나 솔루션 설명]

**결과 및 기대효과**
- [주요 결과와 기대되는 영향 요약]

중요:
- 전체 길이 600자 이내로 유지
- 각 섹션당 1-2개의 간결한 불릿 포인트만 사용
- 핵심 스토리라인에만 집중
- 수식은 LaTeX 형식 사용: $인라인$ 또는 $$블록$$"""
            user_message = f"논문 텍스트:\n\n{paper_text[:15000]}"
        else:
            system_prompt = """You are an expert research paper analyst. Analyze the paper's storyline and structure your response in EXACTLY this format (600 characters or less):

**Problem Statement (문제 제기)**
- [Identify the main problem or research gap]

**Limitations of Existing Methods (기존 방법론의 한계)**
- [Explain limitations of existing approaches]

**Proposed Methodology (본 논문의 방법론)**
- [Describe the proposed methodology]

**Results & Expected Impact (결과 및 기대효과)**
- [Summarize key results and expected impact]

IMPORTANT:
- Keep TOTAL length under 600 characters
- Use 1-2 concise bullet points per section
- Focus on the main storyline only
- Use proper LaTeX for formulas: $inline$ or $$block$$"""
            user_message = f"Paper text:\n\n{paper_text[:15000]}"
        
        try:
            # Use traced client for Langfuse logging
            response = self.traced_client.chat.completions.create(
                model=model_to_use,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.7,
                max_tokens=800
            )
            
            storyline = response.choices[0].message.content
            return storyline
        
        except Exception as e:
            raise Exception(f"Failed to analyze storyline: {str(e)}")
    
    async def extract_metadata(
        self,
        paper_text: str
    ) -> dict:
        """
        Extract paper metadata (title, authors, year) from text

        Args:
            paper_text: Full text of the paper (first part)

        Returns:
            Dictionary with title, authors, year
        """
        system_prompt = """You are a metadata extraction expert. Extract the paper's title, authors, and publication year from the provided text.

Return your answer in EXACTLY this format:
TITLE: [paper title]
AUTHORS: [comma-separated author names]
YEAR: [publication year]

If any field is not found, use "Unknown" for that field."""

        try:
            response = self.client.chat.completions.create(
                model=self.default_model,  # Use default model for metadata
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Extract metadata from this paper:\n\n{paper_text[:3000]}"}
                ],
                temperature=0.3,
                max_tokens=200
            )

            result = response.choices[0].message.content

            # Parse the result
            metadata = {
                "title": "Unknown",
                "authors": "Unknown",
                "year": "Unknown"
            }

            for line in result.split('\n'):
                if line.startswith('TITLE:'):
                    metadata['title'] = line.replace('TITLE:', '').strip()
                elif line.startswith('AUTHORS:'):
                    metadata['authors'] = line.replace('AUTHORS:', '').strip()
                elif line.startswith('YEAR:'):
                    metadata['year'] = line.replace('YEAR:', '').strip()

            return metadata

        except Exception as e:
            print(f"Warning: Failed to extract metadata: {str(e)}")
            return {
                "title": "Unknown",
                "authors": "Unknown",
                "year": "Unknown"
            }

    async def evaluate_summary(
        self,
        original_text: str,
        summary: str,
        model: Optional[str] = None,
        session_id: Optional[str] = None
    ) -> dict:
        """
        Evaluate summary quality using LLM-as-a-judge approach

        Args:
            original_text: Original paper text
            summary: Generated summary to evaluate
            model: Model to use for evaluation (defaults to gpt-5-mini)
            session_id: Optional session ID for tracking

        Returns:
            Dictionary with evaluation scores and reasoning
        """
        model_to_use = model or self.default_model

        system_prompt = """You are an expert evaluator of academic paper summaries. Your task is to assess the quality of a summary based on multiple criteria.

Evaluate the summary on these dimensions (1-10 scale):

1. **Faithfulness (충실성)**: Does the summary accurately reflect the original paper's content without hallucinations or distortions?
   - 1-3: Major inaccuracies or hallucinations
   - 4-6: Some minor inaccuracies
   - 7-8: Mostly accurate with negligible errors
   - 9-10: Perfectly faithful to the original

2. **Completeness (완전성)**: Does the summary cover all key aspects of the paper (objectives, methods, findings, conclusions)?
   - 1-3: Missing multiple critical elements
   - 4-6: Missing some important details
   - 7-8: Covers most key aspects
   - 9-10: Comprehensive coverage of all essential elements

3. **Conciseness (간결성)**: Is the summary clear and concise without unnecessary information?
   - 1-3: Very verbose or includes irrelevant details
   - 4-6: Some unnecessary content
   - 7-8: Mostly concise
   - 9-10: Perfectly concise, every sentence adds value

4. **Coherence (일관성)**: Is the summary well-structured with logical flow?
   - 1-3: Disorganized or confusing structure
   - 4-6: Somewhat logical but could be better organized
   - 7-8: Well-structured with good flow
   - 9-10: Excellent structure and seamless transitions

5. **Clarity (명료성)**: Is the summary easy to understand for the target audience?
   - 1-3: Difficult to understand
   - 4-6: Understandable but requires effort
   - 7-8: Clear and accessible
   - 9-10: Exceptionally clear and well-written

Return your evaluation in EXACTLY this JSON format:
```json
{
  "faithfulness": 8,
  "completeness": 7,
  "conciseness": 9,
  "coherence": 8,
  "clarity": 9,
  "overall_score": 8.2,
  "reasoning": "Brief explanation of the evaluation (2-3 sentences)",
  "strengths": ["strength 1", "strength 2"],
  "weaknesses": ["weakness 1", "weakness 2"]
}
```"""

        user_message = f"""Original Paper (first 10000 chars):
{original_text[:10000]}

---

Summary to Evaluate:
{summary}

---

Please evaluate this summary using the criteria above and return a JSON response."""

        try:
            import json
            import re

            # Use traced client for Langfuse logging
            # For Langfuse, we need to wrap the call differently
            trace_id = None
            observation_id = None

            if LANGFUSE_ENABLED and session_id:
                # Langfuse OpenAI wrapper doesn't accept session_id directly
                # Instead, we can use the name parameter for tracking
                response = self.traced_client.chat.completions.create(
                    model=model_to_use,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_message}
                    ],
                    temperature=0.3,  # Lower temperature for more consistent evaluations
                    max_tokens=1000,
                    name=f"evaluate_summary_{session_id}",  # For Langfuse tracking
                    metadata={
                        "session_id": session_id,
                        "evaluation_type": "summary_quality",
                        "model_used": model_to_use
                    }
                )

                # Extract trace information from response for scoring
                if hasattr(response, '_langfuse_observation_id'):
                    observation_id = response._langfuse_observation_id
                if hasattr(response, '_langfuse_trace_id'):
                    trace_id = response._langfuse_trace_id
            else:
                response = self.traced_client.chat.completions.create(
                    model=model_to_use,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_message}
                    ],
                    temperature=0.3,
                    max_tokens=1000
                )

            result_text = response.choices[0].message.content

            # Try to find JSON block in response
            json_match = re.search(r'```json\s*(\{.*?\})\s*```', result_text, re.DOTALL)
            if json_match:
                result_json = json.loads(json_match.group(1))
            else:
                # Try to parse the entire response as JSON
                result_json = json.loads(result_text)

            # Ensure all required fields are present
            required_fields = ["faithfulness", "completeness", "conciseness", "coherence", "clarity"]
            for field in required_fields:
                if field not in result_json:
                    result_json[field] = 5  # Default middle score

            # Calculate overall score if not provided
            if "overall_score" not in result_json:
                result_json["overall_score"] = round(sum([
                    result_json["faithfulness"],
                    result_json["completeness"],
                    result_json["conciseness"],
                    result_json["coherence"],
                    result_json["clarity"]
                ]) / 5, 1)

            # Log scores to Langfuse Scores tab
            if LANGFUSE_ENABLED and langfuse_client and session_id:
                try:
                    # Determine trace ID for scoring
                    scoring_trace_id = trace_id if trace_id else f"summary_{session_id}"

                    # Overall score (main score)
                    langfuse_client.create_score(
                        name="overall_quality",
                        value=result_json["overall_score"] / 10,  # Normalize to 0-1
                        trace_id=scoring_trace_id,
                        observation_id=observation_id,
                        comment=result_json.get("reasoning", ""),
                        data_type="NUMERIC"
                    )

                    # Individual dimension scores
                    for dimension in ["faithfulness", "completeness", "conciseness", "coherence", "clarity"]:
                        langfuse_client.create_score(
                            name=dimension,
                            value=result_json[dimension] / 10,  # Normalize to 0-1
                            trace_id=scoring_trace_id,
                            observation_id=observation_id,
                            data_type="NUMERIC"
                        )

                    # Flush to ensure scores are sent
                    langfuse_client.flush()

                    print(f"📊 Scores logged to Langfuse for session {session_id}")

                except Exception as score_error:
                    print(f"⚠️  Failed to log scores to Langfuse: {score_error}")

            return result_json

        except json.JSONDecodeError as e:
            print(f"Warning: Failed to parse evaluation JSON: {str(e)}")
            # Return a default evaluation
            return {
                "faithfulness": 5,
                "completeness": 5,
                "conciseness": 5,
                "coherence": 5,
                "clarity": 5,
                "overall_score": 5.0,
                "reasoning": "Evaluation failed - unable to parse response",
                "strengths": [],
                "weaknesses": ["Evaluation error occurred"],
                "error": str(e)
            }
        except Exception as e:
            print(f"Warning: Failed to evaluate summary: {str(e)}")
            return {
                "faithfulness": 0,
                "completeness": 0,
                "conciseness": 0,
                "coherence": 0,
                "clarity": 0,
                "overall_score": 0.0,
                "reasoning": f"Evaluation failed: {str(e)}",
                "strengths": [],
                "weaknesses": ["System error during evaluation"],
                "error": str(e)
            }


# Global LLM service instance
llm_service = LLMService()

