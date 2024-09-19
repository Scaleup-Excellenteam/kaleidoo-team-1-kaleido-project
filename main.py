from scripts.chat_bot import ChatBot
from bidi.algorithm import get_display




if __name__ == "__main__":
    # Define configurations for different setups
    configs = [
        {
            'name': 'תצורה 3: מודל mt0-base עבור עברית',
            'data_file_path': 'data/raw_data_hebrew.json',
            'language': 'hebrew',
            'embedding_type': 'huggingface',
            'embedding_model_name': 'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2',
            'vector_store_type': 'faiss',
            'llm_type': 'huggingface',
            'llm_model_name': 'bigscience/mt0-base',
            'huggingface_model_kwargs': {"temperature": 0.8, "max_length": 200}
        },
        {
            'name': 'תצורה 2: מודל ByT5 עבור עברית',
            'data_file_path': 'data/raw_data_english.json',
            'language': 'english',
            'embedding_type': 'huggingface',
            'embedding_model_name': 'sentence-transformers/distiluse-base-multilingual-cased-v1',
            'vector_store_type': 'faiss',
            'llm_type': 'huggingface',
            'llm_model_name': 'google/flan-t5-base',
            'huggingface_model_kwargs': {"max_new_tokens": 150,"temperature": 0.3}
        },
        # Add more configurations as needed
    ]

    # Choose a configuration to run
    for idx, cfg in enumerate(configs):
        print(get_display(f" {cfg['name']}\n"))

    choice = int(input(get_display("בחר תצורה להפעלה (הכנס מספר): " ) + "\n")) - 1
    selected_config = configs[choice]

    chatbot = ChatBot(selected_config)
    chatbot.run()
