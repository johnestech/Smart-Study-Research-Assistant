import google.generativeai as genai
from config import Config
import re
from typing import List, Dict, Any
import json

class GeminiService:
    def __init__(self):
        genai.configure(api_key=Config.GOOGLE_API_KEY)
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        # Academic content checking prompt
        self.academic_checker_prompt = """
        You are an academic content classifier. Your task is to determine if the given content is academic in nature.
        
        Academic content includes:
        - Research papers, studies, and scholarly articles
        - Educational materials and textbooks
        - Scientific data and analysis
        - Academic presentations and lectures
        - Thesis and dissertation content
        - Course materials and syllabi
        - Academic journals and publications
        - Educational assessments and assignments
        
        Non-academic content includes:
        - Personal documents (resumes, letters, etc.)
        - Entertainment content (novels, movies, games, etc.)
        - Commercial or marketing materials
        - Social media content
        - News articles (unless specifically academic research)
        - General web content
        - Personal photos or casual images
        
        Respond with only "ACADEMIC" or "NON_ACADEMIC" based on the content classification.
        
        Content to classify:
        """
        
        # System prompt for academic Q&A
        self.system_prompt = """
        You are an AI assistant specialized in academic research and study. Your primary function is to help users understand and analyze academic content from their uploaded documents.

        IMPORTANT GUIDELINES:
        1. You ONLY answer questions related to academic research and study
        2. If a question is not academic in nature, politely decline and explain your purpose
        3. Base your answers on the provided document content when available
        4. If asked about non-academic content in a document, respond: "The information found in this document is not academic related, and this application is built for academic study and research."
        5. Provide clear, well-structured, and educational responses
        6. Cite specific parts of documents when referencing them
        7. Encourage further academic inquiry and learning

        Always maintain a helpful, professional, and educational tone.
        """
    
    def is_academic_content(self, content: str) -> bool:
        """Check if content is academic in nature"""
        try:
            prompt = self.academic_checker_prompt + content[:2000]  # Limit to first 2000 chars
            response = self.model.generate_content(prompt)
            classification = response.text.strip().upper()
            return classification == "ACADEMIC"
        except Exception as e:
            print(f"Error checking academic content: {e}")
            # Default to allowing content if classification fails
            return True
    
    def is_academic_question(self, question: str) -> bool:
        """Check if a question is academic in nature"""
        academic_keywords = [
            'research', 'study', 'analysis', 'theory', 'hypothesis', 'methodology',
            'literature', 'academic', 'scholarly', 'scientific', 'experiment',
            'data', 'findings', 'conclusion', 'abstract', 'thesis', 'dissertation',
            'journal', 'publication', 'citation', 'reference', 'bibliography',
            'education', 'learning', 'course', 'curriculum', 'syllabus',
            'concept', 'principle', 'framework', 'model', 'paradigm'
        ]
        
        non_academic_keywords = [
            'entertainment', 'movie', 'game', 'music', 'celebrity', 'gossip',
            'shopping', 'recipe', 'cooking', 'fashion', 'sports', 'weather',
            'personal', 'relationship', 'dating', 'social media', 'meme'
        ]
        
        question_lower = question.lower()
        
        # Check for non-academic keywords first (more restrictive)
        for keyword in non_academic_keywords:
            if keyword in question_lower:
                return False
        
        # Check for academic keywords
        for keyword in academic_keywords:
            if keyword in question_lower:
                return True
        
        # If no clear indicators, use more sophisticated checking
        academic_patterns = [
            r'\b(what|how|why|when|where)\s+(is|are|does|do|did|can|could|would|should)\b.*\b(concept|theory|principle|method|approach|framework)\b',
            r'\bexplain\s+(the|this|that|how|why)\b',
            r'\b(analyze|examine|discuss|evaluate|compare|contrast|critique)\b',
            r'\b(according to|based on|as mentioned in|as stated in)\b.*\b(document|paper|text|study|research)\b'
        ]
        
        for pattern in academic_patterns:
            if re.search(pattern, question_lower):
                return True
        
        # Default to True for borderline cases to be inclusive
        return True
    
    def generate_chat_title(self, first_message: str, max_length: int = 50) -> str:
        """Generate a concise chat title based on the first message"""
        try:
            prompt = f"""
            Generate a concise, descriptive title (maximum {max_length} characters) for a chat conversation based on this first message:
            
            "{first_message}"
            
            The title should:
            - Be clear and specific
            - Capture the main topic or question
            - Be suitable for academic/research context
            - Not exceed {max_length} characters
            
            Respond with only the title, no additional text.
            """
            
            response = self.model.generate_content(prompt)
            title = response.text.strip()
            
            # Ensure title doesn't exceed max length
            if len(title) > max_length:
                title = title[:max_length-3] + "..."
            
            return title
        except Exception as e:
            print(f"Error generating chat title: {e}")
            # Fallback to truncated first message
            return first_message[:max_length-3] + "..." if len(first_message) > max_length else first_message
    
    def generate_response(self, question: str, document_contents: List[str] = None, 
                         chat_history: List[Dict[str, str]] = None) -> Dict[str, Any]:
        """Generate a response to a user question"""
        try:
            # Check if the question is academic
            if not self.is_academic_question(question):
                return {
                    'success': True,
                    'response': "I'm designed specifically for academic study and research purposes. Please ask questions related to academic content, research, or educational materials.",
                    'is_academic': False
                }
            
            # Build context
            context_parts = [self.system_prompt]
            
            # Add document contents if available
            if document_contents:
                academic_docs = []
                non_academic_docs = []
                
                for doc_content in document_contents:
                    if self.is_academic_content(doc_content):
                        academic_docs.append(doc_content)
                    else:
                        non_academic_docs.append(doc_content)
                
                if non_academic_docs and not academic_docs:
                    return {
                        'success': True,
                        'response': "The information found in this document is not academic related, and this application is built for academic study and research.",
                        'is_academic': False
                    }
                
                if academic_docs:
                    context_parts.append("\\n\\nDocument Content:")
                    for i, doc in enumerate(academic_docs):
                        context_parts.append(f"\\n--- Document {i+1} ---\\n{doc}")
            
            # Add chat history for context
            if chat_history:
                context_parts.append("\\n\\nPrevious Conversation:")
                for msg in chat_history[-10:]:  # Include last 10 messages for context
                    role = "User" if msg['role'] == 'user' else "Assistant"
                    context_parts.append(f"\\n{role}: {msg['content']}")
            
            # Add current question
            context_parts.append(f"\\n\\nCurrent Question: {question}")
            context_parts.append("\\n\\nPlease provide a comprehensive, academic response:")
            
            full_prompt = "".join(context_parts)
            
            # Generate response
            response = self.model.generate_content(full_prompt)
            
            return {
                'success': True,
                'response': response.text,
                'is_academic': True
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f"Error generating response: {str(e)}"
            }
    
    def summarize_document(self, content: str, max_length: int = 500) -> str:
        """Summarize document content for storage/display"""
        try:
            prompt = f"""
            Provide a concise summary (maximum {max_length} characters) of this academic document:
            
            {content}
            
            Focus on:
            - Main topic and objectives
            - Key findings or concepts
            - Relevance for academic study
            
            Respond with only the summary.
            """
            
            response = self.model.generate_content(prompt)
            summary = response.text.strip()
            
            if len(summary) > max_length:
                summary = summary[:max_length-3] + "..."
            
            return summary
        except Exception as e:
            return f"Document summary unavailable: {str(e)}"

# Global instance
gemini_service = GeminiService()
