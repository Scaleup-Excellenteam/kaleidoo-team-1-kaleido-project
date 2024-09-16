import os
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

# Function to extract text lines from a file
def extract_text_from_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.readlines()

# Function to build embeddings and index them
def build_index(file_paths):
    model = SentenceTransformer('all-MiniLM-L6-v2')
    all_lines = []
    file_names = []
    line_numbers = []

    for file_path in file_paths:
        lines = extract_text_from_file(file_path)
        for line_number, line in enumerate(lines):
            all_lines.append(line.strip())
            file_names.append(file_path)
            line_numbers.append(line_number)
    
    embeddings = model.encode(all_lines)
    
    # Create a Faiss index
    embedding_dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(embedding_dimension)
    index.add(embeddings)
    
    return index, model, file_names, line_numbers

# Function to search for a query
def search_query(query, index, model, file_names, line_numbers, k=5):
    query_embedding = model.encode([query])
    D, I = index.search(query_embedding, k)
    
    results = []
    for idx in I[0]:
        file_name = file_names[idx]
        line_number = line_numbers[idx]
        results.append((file_name, line_number))
    
    return results

# Example usage
if __name__ == "__main__":
    # Define your files
    file_paths = ['file1.txt', 'file2.txt']  # Replace with your actual file paths
    
    # Build index
    index, model, file_names, line_numbers = build_index(file_paths)
    
    # Define a query
    query = "Linear Algebra"  # Replace with your actual query
    
    # Search for the query
    results = search_query(query, index, model, file_names, line_numbers)
    
    # Print results
    for file_name, line_number in results:
        print(f"File: {file_name}, Line Number: {line_number}")
