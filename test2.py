from transformers import Wav2Vec2Processor, Wav2Vec2ForCTC
import pyaudio
import numpy as np
import torch

# Load pre-trained Wav2Vec2 model and processor
processor = Wav2Vec2Processor.from_pretrained("facebook/wav2vec2-base-960h")
model = Wav2Vec2ForCTC.from_pretrained("facebook/wav2vec2-base-960h")

# PyAudio setup for real-time audio capture
CHUNK = 1024  # Number of audio frames per buffer
RATE = 16000  # Sampling rate (Wav2Vec2 expects 16kHz audio)

p = pyaudio.PyAudio()

# Open a stream for microphone input
stream = p.open(format=pyaudio.paInt16, channels=1, rate=RATE, input=True, frames_per_buffer=CHUNK)

print("Recording and transcribing...")

# Real-time transcription
try:
    while True:
        # Read audio data from the microphone
        data = stream.read(CHUNK)
        audio_data = np.frombuffer(data, dtype=np.int16)

        # Normalize the audio data to the range [-1, 1]
        audio_data = audio_data.astype(np.float32) / np.iinfo(np.int16).max

        # Process the audio chunk through the processor
        input_values = processor(audio_data, return_tensors="pt", sampling_rate=RATE).input_values

        # Perform inference on the model
        with torch.no_grad():
            logits = model(input_values).logits

        # Decode the predicted token IDs to text
        predicted_ids = torch.argmax(logits, dim=-1)
        transcription = processor.batch_decode(predicted_ids)

        # Print the real-time transcription
        print(f"Transcription: {transcription[0]}")
        
except KeyboardInterrupt:
    # Stop the stream on exit
    stream.stop_stream()
    stream.close()
    p.terminate()

print("Real-time transcription stopped.")
