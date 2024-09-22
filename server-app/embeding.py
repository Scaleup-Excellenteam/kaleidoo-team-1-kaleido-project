import json
import os
from sentence_transformers import SentenceTransformer  # For Hugging Face embeddings

# Initialize Hugging Face transformer model for embeddings
hf_model = SentenceTransformer('all-MiniLM-L6-v2')  # You can replace this with any other model from Hugging Face

# Load the JSON data
def load_json_files(directory):
    data = []
    for filename in os.listdir(directory):
        if filename.endswith('.json'):
            filepath = os.path.join(directory, filename)
            with open(filepath, 'r') as f:
                json_data = json.load(f)
                data.append(json_data)
    return data

# Get embeddings using Hugging Face Sentence Transformers model
def get_embeddings(texts):
    embeddings = hf_model.encode(texts, convert_to_tensor=True).tolist()  # Convert the embeddings to list
    return embeddings

# Process each JSON file and get embeddings for the text
def process_json_files(json_data_list):
    embeddings = []
    for data in json_data_list:
        # If the JSON data is a list, iterate over each item
        if isinstance(data, list):
            for item in data:
                text = item.get("text", "")
                if text:
                    emb = get_embeddings([text])  # Embed the text
                    embeddings.append({
                        "ref": item.get("ref", ""),  # Reference for the file (filename, path, etc.)
                        "text": text,
                        "embedding": emb,
                        "offset": item.get("offset", ""),
                        "lang": item.get("lang", "")
                    })
        else:
            # If it's not a list, process it as a single dictionary
            text = data.get("text", "")
            if text:
                emb = get_embeddings([text])  # Embed the text
                embeddings.append({
                    "ref": data.get("ref", ""),  # Reference for the file (filename, path, etc.)
                    "text": text,
                    "embedding": emb,
                    "offset": data.get("offset", ""),
                    "lang": data.get("lang", "")
                })
    return embeddings

# Save embeddings
def save_embeddings(embeddings, output_file):
    with open(output_file, 'w') as f:
        json.dump(embeddings, f)

if __name__ == "__main__":
    # Directory containing JSON files
    json_directory = '/home/ameer/Kaleidoo/server-app/files'
    output_embeddings_file = './embeddings.json'

    # Load JSON, process, and get embeddings
    json_data = load_json_files(json_directory)
    embeddings = process_json_files(json_data)
    save_embeddings(embeddings, output_embeddings_file)

    print(f"Embeddings saved to {output_embeddings_file}")
