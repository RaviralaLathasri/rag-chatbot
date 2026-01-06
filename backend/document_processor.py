import PyPDF2
import re

class DocumentProcessor:
    def __init__(self, chunk_size=500, chunk_overlap=50):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def extract_text(self, filepath):
        """Extract text from PDF or TXT file"""
        if filepath.endswith('.pdf'):
            return self._extract_from_pdf(filepath)
        elif filepath.endswith('.txt'):
            return self._extract_from_txt(filepath)
        else:
            raise ValueError("Unsupported file format")
    
    def _extract_from_pdf(self, filepath):
        """Extract text from PDF"""
        text = ""
        try:
            with open(filepath, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
        except Exception as e:
            raise Exception(f"Error reading PDF: {str(e)}")
        
        return self._clean_text(text)
    
    def _extract_from_txt(self, filepath):
        """Extract text from TXT file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as file:
                text = file.read()
        except UnicodeDecodeError:
            with open(filepath, 'r', encoding='latin-1') as file:
                text = file.read()
        
        return self._clean_text(text)
    
    def _clean_text(self, text):
        """Clean extracted text"""
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'\n+', '\n', text)
        text = text.strip()
        return text
    
    def chunk_text(self, text):
        """Split text into overlapping chunks"""
        words = text.split()
        chunks = []
        
        i = 0
        while i < len(words):
            chunk_words = words[i:i + self.chunk_size]
            chunk_text = ' '.join(chunk_words)
            
            chunks.append({
                'id': len(chunks),
                'text': chunk_text,
                'word_count': len(chunk_words)
            })
            
            i += self.chunk_size - self.chunk_overlap
        
        return chunks
