
from langchain.llms import HuggingFaceHub
from typing import List, Dict, Any
from langchain import PromptTemplate
from dotenv import load_dotenv
import os
load_dotenv()

# **LLMHandler** class
class LLMHandler:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.llm = self.initialize_llm()

    def initialize_llm(self):
        llm_type = self.config['llm_type']
        if llm_type == 'huggingface':
            huggingface_api_key = os.environ.get('HUGGINGFACE_API_KEY')
            model_name = self.config.get('llm_model_name')
            return HuggingFaceHub(
                repo_id=model_name,
                model_kwargs=self.config.get('huggingface_model_kwargs', {}),
                huggingfacehub_api_token=huggingface_api_key
            )
        else:
            raise ValueError(f"Unsupported LLM type: {llm_type}")

    def generate_answer(self, prompt_text: str) -> str:
        return self.llm(prompt_text)
    


# **PromptManager** class
class PromptManager:
    def __init__(self, config: Dict[str, Any]):
        self.template = self.create_prompt_template(config)

    def create_prompt_template(self, config: Dict[str, Any]) -> PromptTemplate:
        if config['language'] == 'english':
            template = config.get('prompt_template', """
You are a lecturer. The user will ask you questions. Use the following context to answer the question.
If you don't know the answer, just say you don't know.
No longer than 2 sentences.

Context: {context}

Question: {question}

""")
        else:
            template = config.get('prompt_template', """
אתה מרצה באוניברסיטה. המשתמש ישאל אותך שאלות. השתמש רק באחד מההקשרים הבאים כדי לענות על השאלה.
אם אינך יודע את התשובה, פשוט אמור שאינך יודע.
ספק תשובה קצרה ותמציתית, לא יותר מ-2 משפטים.


הקשר:
{context}

השאלה של המשתמש: 
{question}

""")
        
        return PromptTemplate(template=template, input_variables=["context", "question"])

    def format_prompt(self, context: str, question: str) -> str:
        return self.template.format(context=context, question=question)


