from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import librosa
import os

# Set your Hugging Face token here
hf_token = "your_hf_token_here"

def load_model_and_processor(model_name):
    try:
        tokenizer = AutoTokenizer.from_pretrained(model_name, token=hf_token)
        model = AutoModelForSequenceClassification.from_pretrained(model_name, token=hf_token)
        print("Model and tokenizer loaded successfully.")
        return tokenizer, model
    except Exception as e:
        print(f"Error loading model or tokenizer: {e}")
        return None, None

def transcribe_audio(model_name, audio_file_path):
    tokenizer, model = load_model_and_processor(model_name)
    if tokenizer is None or model is None:
        return

    if not os.path.isfile(audio_file_path):
        print(f"Audio file not found: {audio_file_path}")
        return

    try:
        # Load and preprocess audio
        speech, rate = librosa.load(audio_file_path, sr=16000)
        print(f"Loaded audio file with {len(speech)} samples.")
    except Exception as e:
        print(f"Error loading audio file: {e}")
        return

    # Assuming HBERT needs raw audio for tokenization
    # Adjust the processing part according to HBERT's requirements
    inputs = tokenizer(speech, return_tensors="pt", padding=True)
    print(f"Processed inputs: {inputs}")

    try:
        with torch.no_grad():
            outputs = model(**inputs)
        
        # Extract prediction
        logits = outputs.logits
        predicted_ids = torch.argmax(logits, dim=-1)
        transcription = tokenizer.decode(predicted_ids[0], skip_special_tokens=True)
        print("Transcription:", transcription)
    except Exception as e:
        print(f"Error during transcription: {e}")

# Example usage
model_name = "your-hbert-model"  # Replace with the actual HBERT model name
audio_file_path = "/home/ameer/Kaleidoo/Data/Audio_Data/Hebrow/test.mp3"

transcribe_audio(model_name, audio_file_path)
