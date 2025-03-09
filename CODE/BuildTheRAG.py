from sentence_transformers import SentenceTransformer
import faiss
import requests
import json

class RAGSystem:
    def __init__(self):
        try:
            self.encoder = SentenceTransformer('./local_encoder')
            self.index = faiss.read_index("knowledge.index")
            with open("ThemessageDatebase\chunks.txt", "r", encoding='utf-8') as f:
                self.chunks = f.read().splitlines()
        except Exception as e:
            raise RuntimeError(f"初始化失败: {str(e)}")

        self.ollama_endpoint = "http://localhost:11434/api/generate"
        self.model_name = "deepseek-r1:1.5b"  
        
    def retrieve(self, query, k=3):
        query_embed = self.encoder.encode([query])
        if query_embed.ndim == 1:
            query_embed = query_embed.reshape(1, -1)
        distances, indices = self.index.search(query_embed.astype('float32'), k)
        return [self.chunks[i] for i in indices[0]]

    def generate(self, query):
        try:
            context = self.retrieve(query)
            prompt = f"""基于以下上下文用中文回答：
            {context}
            
            问题：{query}
            回答："""
            
            response = requests.post(
                self.ollama_endpoint,
                json={
                    "model": self.model_name,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.7,
                        "num_ctx": 4096,
                        "top_k": 40
                    }
                },
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json().get("response", "未获得有效响应")
            else:
                return f"API请求失败: {response.status_code} - {response.text[:200]}"
                
        except Exception as e:
            return f"系统错误: {str(e)}"