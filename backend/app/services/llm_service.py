from openai import OpenAI
from app.config import settings
from typing import Optional


class LLMService:
    """Service for interacting with OpenAI LLM"""
    
    def __init__(self):
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.default_model = settings.default_model
    
    def get_available_models(self):
        """
        Get list of available models
        
        Returns:
            List of model information
        """
        return [
            {
                "id": "gpt-4o-mini",
                "name": "GPT-4o Mini",
                "is_default": True
            },
            {
                "id": "gpt-4o",
                "name": "GPT-4o",
                "is_default": False
            },
            {
                "id": "gpt-3.5-turbo",
                "name": "GPT-3.5 Turbo",
                "is_default": False
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
        default_prompt = """You are a helpful research assistant. Summarize the following academic paper.
Include:
1. Main research question and objectives
2. Methodology used
3. Key findings and results
4. Conclusions and implications
5. Limitations (if any)

Keep the summary concise but comprehensive, around 300-500 words."""
        
        # Use custom prompt if provided
        system_prompt = custom_prompt if custom_prompt else default_prompt
        
        try:
            response = self.client.chat.completions.create(
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


# Global LLM service instance
llm_service = LLMService()

