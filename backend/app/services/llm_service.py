from openai import OpenAI
from app.config import settings
from app.prompts import (
    SUMMARIZE_PAPER_PROMPT,
    ANSWER_QUESTION_PROMPT,
    ANSWER_QUESTION_STREAM_PROMPT,
    STORYLINE_KOREAN_PROMPT,
    STORYLINE_ENGLISH_PROMPT,
    EXTRACT_METADATA_PROMPT,
    EVALUATE_SUMMARY_PROMPT
)
from typing import Optional
import os
import json
import re

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
        system_prompt = custom_prompt if custom_prompt else SUMMARIZE_PAPER_PROMPT
        
        try:
            # Use traced client for Langfuse logging
            response = self.traced_client.chat.completions.create(
                model=model_to_use,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Paper text:\n\n{paper_text}"}
                ],
                max_completion_tokens=2000
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
        system_prompt = ANSWER_QUESTION_PROMPT
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
                max_completion_tokens=1000
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
        system_prompt = ANSWER_QUESTION_STREAM_PROMPT
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
                max_completion_tokens=1000,
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
        
        # Select prompt based on language
        if language == "ko":
            system_prompt = STORYLINE_KOREAN_PROMPT
            user_message = f"논문 텍스트:\n\n{paper_text[:15000]}"
        else:
            system_prompt = STORYLINE_ENGLISH_PROMPT
            user_message = f"Paper text:\n\n{paper_text[:15000]}"
        
        try:
            # Use traced client for Langfuse logging
            response = self.traced_client.chat.completions.create(
                model=model_to_use,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                max_completion_tokens=800
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
        system_prompt = EXTRACT_METADATA_PROMPT
        
        try:
            response = self.client.chat.completions.create(
                model=self.default_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Extract from:\n\n{paper_text[:5000]}"}
                ],
                max_completion_tokens=500
            )

            result = response.choices[0].message.content.strip()
            
            if not result:
                print(f"Warning: Empty response from metadata extraction")
                return {"title": "Unknown", "authors": "Unknown", "year": "Unknown"}

            # Parse JSON response - try to find any JSON object
            try:
                # Try to extract JSON (handles both plain and code-block formats)
                json_match = re.search(r'\{[^}]*"title"[^}]*"authors"[^}]*"year"[^}]*\}', result, re.DOTALL)
                if not json_match:
                    # Fallback: find any JSON object
                    json_match = re.search(r'\{.*?\}', result, re.DOTALL)
                
                if json_match:
                    metadata = json.loads(json_match.group(0))
                    return {
                        "title": metadata.get("title", "Unknown"),
                        "authors": metadata.get("authors", "Unknown"),
                        "year": metadata.get("year", "Unknown")
                    }
                else:
                    print(f"Warning: No JSON found in response: {result[:200]}")
                    return {"title": "Unknown", "authors": "Unknown", "year": "Unknown"}
                
            except (json.JSONDecodeError, AttributeError) as e:
                print(f"Warning: JSON parse error: {e}")
                print(f"Raw response: {result[:300]}")
                return {"title": "Unknown", "authors": "Unknown", "year": "Unknown"}

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
        system_prompt = EVALUATE_SUMMARY_PROMPT
        user_message = f"""Original Paper (first 10000 chars):
{original_text[:10000]}

---

Summary to Evaluate:
{summary}

---

Please evaluate this summary using the criteria above and return a JSON response."""

        try:
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
                    max_completion_tokens=1500,  # Increased for detailed reasoning
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
                    max_completion_tokens=1500   # Increased for detailed reasoning
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

