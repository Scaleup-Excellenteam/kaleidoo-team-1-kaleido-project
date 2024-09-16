import whisper
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from paths import E
# TODO: Look for trained model 
# Force re-download of the model to make sure it's correctly downloaded
model = whisper.load_model("base", download_root="./whisper-models")


# Transcribe audio
def transcribe_audio_with_timestamps(audio_file):
    try:
        result = model.transcribe(audio_file, word_timestamps=True)
        return result
    except Exception as e:
        print(f"Error during transcription: {e}")
        return None

def save_transcription_to_file(transcription_result, file_name):
    if transcription_result is None:
        print("No transcription result to save.")
        return
    
    try:
        with open(file_name, 'w') as f:
            for segment in transcription_result['segments']:
                start = segment['start']
                end = segment['end']
                text = segment['text']
                f.write(f"{start:.2f} - {end:.2f}: {text}\n")
    except Exception as e:
        print(f"Error saving transcription to file: {e}")

# Embed and index
def embed_text(text_segments):
    try:
        model = SentenceTransformer('all-MiniLM-L6-v2')
        return model.encode(text_segments)
    except Exception as e:
        print(f"Error during text embedding: {e}")
        return np.array([])

def create_faiss_index(embeddings):
    try:
        dim = embeddings.shape[1]
        index = faiss.IndexFlatL2(dim)
        index.add(embeddings)
        return index
    except Exception as e:
        print(f"Error creating FAISS index: {e}")
        return None

def save_index(index, file_name):
    if index is None:
        print("No index to save.")
        return
    
    try:
        faiss.write_index(index, file_name)
    except Exception as e:
        print(f"Error saving FAISS index: {e}")

def search_faiss_index(query, index, text_segments):
    try:
        model = SentenceTransformer('all-MiniLM-L6-v2')
        query_embedding = model.encode([query])
        D, I = index.search(query_embedding, k=5)  # k is the number of top results
        results = [(text_segments[i], D[0][j]) for j, i in enumerate(I[0])]
        return results
    except Exception as e:
        print(f"Error searching FAISS index: {e}")
        return []

# Main execution


    
transcription_result = transcribe_audio_with_timestamps(audio_file)
save_transcription_to_file(transcription_result, "transcription.txt")

if transcription_result:
    text_segments = [segment['text'] for segment in transcription_result['segments']]
    embeddings = embed_text(text_segments)
    if embeddings.size > 0:
        index = create_faiss_index(embeddings)
        save_index(index, "faiss_index.index")

        # Search for query
        query = "its easy to tell"
        results = search_faiss_index(query, index, text_segments)
        for result in results:
            print(f"Found: {result[0]} with distance: {result[1]}")
    else:
        print("No embeddings to create an index.")
