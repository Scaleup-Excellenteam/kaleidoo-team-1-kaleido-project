from transformers import Wav2Vec2Processor, Wav2Vec2ForCTC
import pyaudio
import numpy as np
import torch

# Load pre-trained Wav2Vec2 model and processor
processor = Wav2Vec2Processor.from_pretrained("facebook/wav2vec2-base-960h")
model = Wav2Vec2ForCTC.from_pretrained("facebook/wav2vec2-base-960h")

# PyAudio setup for audio capture
CHUNK = 4096  # Number of audio frames per buffer
RATE = 16000  # Sampling rate (Wav2Vec2 expects 16kHz audio)
RECORD_SECONDS = 5  # Record 5 seconds of audio

p = pyaudio.PyAudio()

# Open a stream for microphone input
stream = p.open(format=pyaudio.paInt16, channels=1, rate=RATE, input=True, frames_per_buffer=CHUNK)

print(f'Recording for {RECORD_SECONDS} seconds...')

frames = []

# Record for a fixed duration
for _ in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
    data = stream.read(CHUNK)
    frames.append(np.frombuffer(data, dtype=np.int16))

# Stop the stream
stream.stop_stream()
stream.close()
p.terminate()

# Combine all frames into a single numpy array
audio_data = np.concatenate(frames)

# Normalize the audio data to the range [-1, 1]
audio_data = audio_data.astype(np.float32) / np.iinfo(np.int16).max

# Process the audio data through the processor
input_values = processor(audio_data, return_tensors="pt", sampling_rate=RATE).input_values

# Perform inference on the model
with torch.no_grad():
    logits = model(input_values).logits

# Decode the predicted token IDs to text
predicted_ids = torch.argmax(logits, dim=-1)
transcription = processor.batch_decode(predicted_ids)

# Print the transcription
print(f"Transcription: {transcription[0]}")
