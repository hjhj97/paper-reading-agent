import PyPDF2
from io import BytesIO


class PDFParser:
    """Service for parsing PDF files and extracting text"""
    
    @staticmethod
    async def extract_text_from_pdf(file_content: bytes) -> str:
        """
        Extract text from PDF file content
        
        Args:
            file_content: Raw bytes of the PDF file
            
        Returns:
            Extracted text as a string
            
        Raises:
            Exception: If PDF parsing fails
        """
        try:
            pdf_file = BytesIO(file_content)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            
            text = ""
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text += page.extract_text() + "\n"
            
            if not text.strip():
                raise ValueError("No text could be extracted from the PDF")
            
            return text.strip()
        
        except Exception as e:
            raise Exception(f"Failed to parse PDF: {str(e)}")
    
    @staticmethod
    def clean_text(text: str) -> str:
        """
        Clean extracted text by removing extra whitespace and normalizing
        
        Args:
            text: Raw extracted text
            
        Returns:
            Cleaned text
        """
        # Remove multiple spaces
        text = " ".join(text.split())
        
        # Remove multiple newlines
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        text = "\n".join(lines)
        
        return text

