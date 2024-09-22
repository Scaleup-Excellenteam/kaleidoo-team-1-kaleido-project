import json
import torch
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
from transformers import pipeline
import re 

# Initialize Hugging Face Sentence Transformer model for embeddings
hf_embedding_model = SentenceTransformer('all-MiniLM-L6-v2')  # Replace with any Hugging Face embedding model
hf_generator = pipeline("text-generation", model="gpt2")  # Replace with any Hugging Face language model for generation

# Load embeddings and metadata
def load_embeddings(file_path):
    with open(file_path, 'r') as f:
        embeddings = json.load(f)
    return embeddings

# Get embeddings for the query using Hugging Face model
def get_embeddings(texts, model="hf"):
    if model == "hf":
        embeddings = hf_embedding_model.encode(texts, convert_to_tensor=True).tolist()
    else:
        raise NotImplementedError("Only Hugging Face model supported in this script.")
    return embeddings


# Function to retrieve the most similar text for a given query
# Function to retrieve the most similar text for a given query
def retrieve_relevant_text(query, embeddings, top_k=3):
    # Embed the query using the Hugging Face model
    query_embedding = get_embeddings([query], model="hf")[0]

    # Ensure query_embedding is a 2D tensor
    query_embedding = torch.tensor(query_embedding).unsqueeze(0)  # Add batch dimension

    # Calculate cosine similarity between query embedding and stored embeddings
    similarities = []
    for item in embeddings:
        stored_embedding = torch.tensor(item['embedding'])

        # Ensure stored_embedding is also a 2D tensor
        if stored_embedding.dim() == 1:
            stored_embedding = stored_embedding.unsqueeze(0)  # Add batch dimension if needed
        elif stored_embedding.dim() > 2:
            stored_embedding = stored_embedding.view(-1, stored_embedding.size(-1))  # Flatten if 3D

        similarity = cosine_similarity(query_embedding.numpy(), stored_embedding.numpy())[0][0]
        similarities.append((similarity, item))

    # Sort by similarity and return top-k most relevant texts
    similarities.sort(key=lambda x: x[0], reverse=True)
    return [item[1] for item in similarities[:top_k]]



import re

def clean_output(text):
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Remove numbers
    text = re.sub(r'\d+', '', text)
    
    # Remove repeated phrases
    seen = set()
    cleaned_lines = []
    for line in text.split('. '):
        if line not in seen:
            seen.add(line)
            cleaned_lines.append(line)
    
    # Join cleaned lines and capitalize sentences
    cleaned_text = '. '.join(cleaned_lines).strip()
    cleaned_text = cleaned_text.capitalize()
    
    return cleaned_text



def generate_with_rag(query, embeddings, top_k=3):
    # Retrieve top-k relevant texts
    relevant_texts = retrieve_relevant_text(query, embeddings, top_k=top_k)
    context = " ".join([item['text'] for item in relevant_texts])

    # Use Hugging Face GPT-2 (or any model) to generate a response
    response = hf_generator(
        f"{context}\n\nAnswer the following question based on the context: {query}",
        max_length=1000,
        num_return_sequences=1,
        truncation=True,
        pad_token_id=hf_generator.model.config.eos_token_id
    )

    # Clean and format the output
    generated_text = response[0]["generated_text"].strip()
    formatted_response = clean_output(generated_text)

    return formatted_response

if __name__ == "__main__":
    # Path to the embeddings file
    output_embeddings_file = '/home/ameer/Kaleidoo/server-app/embeddings.json'

    # Load stored embeddings
    embeddings = load_embeddings(output_embeddings_file)

    # Example of how to use the RAG pipeline
    query = "can help you access"
    response = generate_with_rag(query, embeddings, top_k=3)
    print(f"Generated Response: {response}")
