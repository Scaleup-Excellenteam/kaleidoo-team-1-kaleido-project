import json
import warnings
import os
import time
from typing import List, Dict, Any

import pinecone
from dotenv import load_dotenv
from datetime import datetime


from langchain.llms import HuggingFaceHub
from langchain.schema import Document
from langchain.vectorstores import FAISS, Pinecone
from langchain import PromptTemplate

from bidi.algorithm import get_display

from scripts.data_loader import DataLoader
from scripts.embedding_handler import EmbeddingHandler
from scripts.vector_store_handler import VectorStoreHandler
from scripts.llm_handler import LLMHandler, PromptManager

warnings.filterwarnings("ignore")
load_dotenv()





# **ChatBot** class
class ChatBot:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.language = config['language']

        # Initialize components
        data_loader = DataLoader(config['data_file_path'])
        raw_data = data_loader.load_data()
        self.documents = data_loader.data_to_documents(raw_data['data'])

        embedding_handler = EmbeddingHandler(config)
        self.embeddings = embedding_handler.embedding_model

        self.vector_store_handler = VectorStoreHandler(config, self.embeddings, self.documents)
        self.llm_handler = LLMHandler(config)
        self.prompt_manager = PromptManager(config)

    def answer_question(self, question: str) -> str:
        # Start timing
        start_time = time.time()

        # Retrieve documents along with their similarity scores
        docs_and_scores = self.vector_store_handler.similarity_search_with_score(
            question, k=3)

        # Prepare the context and metadata information
        
        context = ""
        
        
        metadata_info = {}
        i=0
        for doc, score in docs_and_scores:
            i += 1
            metadata_info[f"{i}"] = [doc.metadata, f"accuracy: {(score):.2f}", get_display(doc.page_content)]
            context += f"{i}.\n{doc.page_content}\n\n"

        # Format the prompt with metadata and context
        prompt_text = self.prompt_manager.format_prompt(context=context, question=question)

        # Get the answer from the LLM
        answer = self.llm_handler.generate_answer(prompt_text)

        # End timing
        end_time = time.time()
        elapsed_time = end_time - start_time

        # Include performance metrics
        performance_info = f"זמן תגובה: {elapsed_time:.2f} שניות"
        full_response = f"{answer}\n\n{performance_info}"

        return full_response , metadata_info

    def run(self):
        print(get_display("הצ'אטבוט מוכן לענות על שאלותיך. הקלד 'exit' כדי לצאת."))
        while True:
            user_input = input(get_display("שאל אותי כל דבר: ") + "\n")
            print("\n")
            if user_input.lower() == 'exit':
                break
            user_input = user_input[::-1] if self.language == 'hebrew' else user_input
            answer , metadata_info = self.answer_question(user_input) 

            print("\n" + get_display("תשובה:\n") +"\n"+ get_display(answer))
            for key, value in metadata_info.items():
                print(f"{key}")
                print(get_display("סוג המסמך:") + f"{value[0]['type']}")
                print(get_display("מקור המסמך:")+  f"{value[0]['ref']}")
                print(get_display("דיוק:") + f"{value[1]}")
                print(get_display("תוכן המסמך:") + f"{value[2]}")
                print(f"{value[0]['lang']}")
                print(f"{value[0]['offset']}") 
                print("-" * 50)
            print("-" * 50)

