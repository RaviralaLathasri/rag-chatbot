import os
import requests
from dotenv import load_dotenv

load_dotenv()

class RAGEngine:
    def __init__(self):
        self.api_key = os.getenv('OPENROUTER_API_KEY')
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY not found in environment variables")
        
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"
        self.model = "meta-llama/llama-3.2-3b-instruct:free"
    
    def retrieve_relevant_chunks(self, query, knowledge_base, top_k=3):
        """Simple keyword-based retrieval"""
        query_words = set(query.lower().split())
        
        scored_chunks = []
        for chunk in knowledge_base['chunks']:
            chunk_words = set(chunk['text'].lower().split())
            overlap = len(query_words.intersection(chunk_words))
            
            if overlap > 0:
                scored_chunks.append({
                    'chunk': chunk,
                    'score': overlap
                })
        
        scored_chunks.sort(key=lambda x: x['score'], reverse=True)
        
        return [item['chunk'] for item in scored_chunks[:top_k]]
    
    def generate_response(self, query, knowledge_base):
        """Generate response using OpenRouter Meta LLaMA"""
        relevant_chunks = self.retrieve_relevant_chunks(query, knowledge_base)
        
        if not relevant_chunks:
            return "I don't have enough information in the provided data to answer that."
        
        context = "\n\n".join([chunk['text'] for chunk in relevant_chunks])
        
        system_prompt = """You are a helpful assistant that answers questions strictly based on the provided document content. 

CRITICAL RULES:
1. Answer ONLY using information from the context provided below
2. If the answer is not in the context, you MUST respond with: "I don't have enough information in the provided data to answer that."
3. Do NOT use any external knowledge
4. Do NOT make assumptions or inferences beyond what is explicitly stated
5. Be concise and accurate
6. If you're unsure, say you don't have enough information"""

        user_prompt = f"""Context from the document:
{context}

Question: {query}

Answer based ONLY on the context above. If the information is not in the context, respond with: "I don't have enough information in the provided data to answer that." """

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.1,
            "max_tokens": 500
        }
        
        try:
            response = requests.post(self.api_url, json=payload, headers=headers, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            
            if 'choices' in result and len(result['choices']) > 0:
                answer = result['choices'][0]['message']['content'].strip()
                return answer
            else:
                return "Error: Unable to generate response from the API"
                
        except requests.exceptions.RequestException as e:
            return f"Error communicating with OpenRouter API: {str(e)}"
