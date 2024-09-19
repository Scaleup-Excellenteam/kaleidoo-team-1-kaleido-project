from typing import List, Dict, Any
from langchain.embeddings import HuggingFaceEmbeddings

# **EmbeddingHandler** class
class EmbeddingHandler:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.embedding_model = self.initialize_embeddings()

    def initialize_embeddings(self):
        embedding_type = self.config['embedding_type']
        if embedding_type == 'huggingface':
            model_name = self.config.get('embedding_model_name')
            return HuggingFaceEmbeddings(model_name=model_name)
        else:
            raise ValueError(f"Unsupported embedding type: {embedding_type}")
