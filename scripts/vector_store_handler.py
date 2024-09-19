from typing import List, Dict, Any
from langchain.schema import Document
from langchain.vectorstores import FAISS, Pinecone

# **VectorStoreHandler** class
class VectorStoreHandler:
    def __init__(self, config: Dict[str, Any], embeddings, documents: List[Document]):
        self.config = config
        self.embeddings = embeddings
        self.documents = documents
        self.vector_store = self.initialize_vector_store()

    def initialize_vector_store(self):
        vector_store_type = self.config['vector_store_type']
        if vector_store_type == 'faiss':
            return FAISS.from_documents(self.documents, self.embeddings)
        elif vector_store_type == 'pinecone':
            return self.initialize_pinecone()
        else:
            raise ValueError(f"Unsupported vector store type: {vector_store_type}")

    def initialize_pinecone(self):
        pinecone_api_key = os.environ.get('PINECONE_API_KEY')
        pinecone.init(
            api_key=pinecone_api_key,
            environment=self.config.get('pinecone_environment', 'us-west1-gcp')
        )
        index_name = self.config.get('index_name', 'langchain-rag')

        if index_name not in pinecone.list_indexes():
            dimension = len(self.embeddings.embed_query("Test"))
            pinecone.create_index(
                name=index_name, metric="cosine", dimension=dimension)
            index = pinecone.Index(index_name)
            Pinecone.from_documents(
                self.documents, self.embeddings, index_name=index_name)
        return Pinecone.from_existing_index(index_name, self.embeddings)

    def similarity_search_with_score(self, query: str, k: int = 4):
        return self.vector_store.similarity_search_with_score(query, k=k)
