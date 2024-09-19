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

from data_loader import DataLoader
from embedding_handler import EmbeddingHandler
from vector_store_handler import VectorStoreHandler
from llm_handler import LLMHandler, PromptManager

warnings.filterwarnings("ignore")
load_dotenv()





# **ChatBot** class

class ChatBot:
    def __init__(self, config: Dict[str, Any] = None):
        if config == None:
            with open("config.json", "r") as file:
               configs = json.loads(file.read())
            self.config = configs["configs"][1]
        else:
            self.config = config
        self.language = self.config['language']

        # Initialize components
        data_loader = DataLoader(self.config['data_file_path'])
        raw_data = data_loader.load_data()
        self.documents = data_loader.data_to_documents(raw_data['data'])

        embedding_handler = EmbeddingHandler(self.config)
        self.embeddings = embedding_handler.embedding_model

        self.vector_store_handler = VectorStoreHandler(self.config, self.embeddings, self.documents)
        self.llm_handler = LLMHandler(self.config)
        self.prompt_manager = PromptManager(self.config)

    def answer_question(self, question: str) -> str:
        # Start timing
        start_time = time.time()

        docs_and_scores = self.vector_store_handler.similarity_search_with_score(
            question, k=3)
        
        context = ""
        
        
        metadata_info = {}
        i=0
        for doc, score in docs_and_scores:
            i += 1
            metadata_info[f"{i}"] = [doc.metadata, f"accuracy: {(self.normalize_cosine_similarity(score)):.2f}", get_display(doc.page_content)]
            context += f"{i}.\n{doc.page_content}\n\n"

        prompt_text = self.prompt_manager.format_prompt(context=context, question=question)

        answer = self.llm_handler.generate_answer(prompt_text)

        end_time = time.time()
        elapsed_time = end_time - start_time

        performance_info = f"זמן תגובה: {elapsed_time:.2f} שניות"
        full_response = f"{answer}\n\n{performance_info}"

        return answer , metadata_info, elapsed_time

    def normalize_cosine_similarity(self, cosine_similarity: float) -> float:
        return (cosine_similarity + 1) / 2

    #TODO: the chatbot should be able to keep running while new data is being added to the vector store
    #TODO: the chatbot should warn the user if the answer is not accurate enough

    # def run(self):
    #     print(get_display("הצ'אטבוט מוכן לענות על שאלותיך. הקלד 'exit' כדי לצאת."))
    #     while True:
    #         user_input = input(get_display("שאל אותי כל דבר: ") + "\n")
    #         print("\n")
    #         if user_input.lower() == 'exit':
    #             break
    #         user_input = user_input[::-1] if self.language == 'hebrew' else user_input
    #         answer , metadata_info = self.answer_question(user_input) 

    #         print("\n" + get_display("תשובה:\n") +"\n"+ get_display(answer))
    #         for key, value in metadata_info.items():
    #             print(f"{key}")
    #             print(get_display("סוג המסמך:") + f"{value[0]['type']}")
    #             print(get_display("מקור המסמך:")+  f"{value[0]['ref']}")
    #             print(get_display("דיוק:") + f"{value[1]}")
    #             print(get_display("תוכן המסמך:") + f"{value[2]}")
    #             print(f"{value[0]['lang']}")
    #             print(f"{value[0]['offset']}") 
    #             print("-" * 50)
    #         print("-" * 50)

    def api_answer_question(self, user_input: str):
        '''
        Answer a user question and return the answer, metadata info and elapsed time

        Args:
            user_input (str): The user question

        Returns:
            srting: The llm answer to the user question
            float: The elapsed time of the process
            dict: The metadata info of the 3 sources with the highest accuracy
                dict key: The document index
                dict value: [metadata, accuracy, content]

        Example usage:
            chatbot = ChatBot()
            answer , metadata_info, elapsed_time = chatbot.api_answer_question("what are the dvantages of local features ? ")

        Example of a metadata_info return value:
            {'1':
                [
                    {
                        'type': 'application/pdf',
                        'ref': '/home/ameer/Kaleidoo/Data/Text_Data/pdf/https://moodle.telhai.ac.il/course/view.php?id=28504',
                        'offset': 'page1',
                        'lang': 'en'
                    },
                    'accuracy: 1.34',
                    'Tel Hai Study Buddy\nIn this project, you are going to research, design and implement a chatbot that bases its answers on multiple types of media sources. Your client is Tel Hai college, and this product is intended to be used by all of the students, regardless of the degree they are studying. During the given time period, your goal is not to build an entire product (not enough time), but to prove that building this kind of product is possible by implementing a quick and dirty MVP of it, and deploy it for the students to interact with.\nProduct description Core features\nMultimodal Search:\nAllows users to search for lecture materials across multiple formats: documents, video\nrecordings, and audio files.\nProvides results that are timestamped for video and audio, guiding users directly to the\nrelevant parts of the original input.\nNatural Language Query Support:\nEnables students to ask questions or search for content using conversational language,\nsuch as requesting specific topics, dates, or lecture details.'
                ],
            '2':
                <same as above>,
            '3':
                <same as above>
            }
        '''
        user_input = user_input[::-1] if self.language == 'hebrew' else user_input
        answer , metadata_info, elapsed_time = self.answer_question(user_input)
        return answer , metadata_info, elapsed_time



from flask import Flask, request, jsonify

app = Flask(__name__)

# Initialize the ChatBot instance
chatbot = ChatBot()

@app.route('/api/answer', methods=['POST'])
def answer_question():
    """
    Flask API endpoint to get an answer from the chatbot.

    The request should contain a JSON body with a "question" field:
    {
        "question": "What is your question?"
    }

    The response will return the chatbot's answer, metadata, and elapsed time in JSON format:
    {
        "answer": "Chatbot's answer",
        "metadata": { ... },  # Metadata information of the top documents
        "elapsed_time": 1.23   # Time taken to process the request
    }
    """
    # Extract the user question from the request
    data = request.get_json()
    question = data.get('question')

    if not question:
        return jsonify({"error": "Please provide a question."}), 400

    # Get the answer, metadata info, and elapsed time from the chatbot
    answer, metadata_info, elapsed_time = chatbot.api_answer_question(question)

    # Return the result as a JSON response
    return jsonify({
        "answer": answer,
        "metadata": metadata_info,
        "elapsed_time": elapsed_time
    })


if __name__ == '__main__':
    # Run the Flask app
    app.run(debug=True)
