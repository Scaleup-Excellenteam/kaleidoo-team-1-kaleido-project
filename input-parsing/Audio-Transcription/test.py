import json
import os
import time
import numpy as np
import webrtcvad
import soundfile as sf
from pydub import AudioSegment
from datetime import timedelta
import psutil
from transformers import Wav2Vec2Processor, Wav2Vec2ForCTC
import torch
import librosa
from paths import * 
# Initialize model and processor
model_name = "facebook/wav2vec2-base-960h"
processor = Wav2Vec2Processor.from_pretrained(model_name)
model = Wav2Vec2ForCTC.from_pretrained(model_name)

def segment_audio(file_path, frame_duration_ms=30):
    audio = AudioSegment.from_wav(file_path)
    sample_rate = audio.frame_rate
    frame_size = int(sample_rate * frame_duration_ms / 1000)
    
    # Convert audio to raw PCM format (16-bit mono)
    audio = audio.set_channels(1).set_sample_width(2)  # Mono, 16-bit
    samples = np.array(audio.get_array_of_samples())
    
    # Initialize VAD
    vad = webrtcvad.Vad()
    
    # Segment the audio
    segments = []
    start = None
    num_frames = len(samples) // frame_size
    
    for i in range(num_frames):
        start_index = i * frame_size
        end_index = start_index + frame_size
        frame = samples[start_index:end_index].tobytes()
        
        if vad.is_speech(frame, sample_rate):
            if start is None:
                start = i
        elif start is not None:
            segments.append((start * frame_duration_ms, i * frame_duration_ms))
            start = None
    
    # Append the last segment if it ended with speech
    if start is not None:
        segments.append((start * frame_duration_ms, num_frames * frame_duration_ms))
    
    return segments

def format_transcription(file_path, transcriptions, snippets):
    # Extract filename without extension
    file_name = os.path.basename(file_path)
    name, _ = os.path.splitext(file_name)

    # Combine transcriptions
    combined_text = " ".join(transcriptions)

    # Format the start and end time from the first and last snippet
    start_time_str = str(timedelta(seconds=snippets[0]['start_time']))
    end_time_str = str(timedelta(seconds=snippets[-1]['end_time']))

    # Create the JSON structure
    transcription_json = {
        "source_type": "audio",
        "source_name": name,
        "start_time": start_time_str,
        "end_time": end_time_str,
        "text_content": combined_text,
        "snippets": snippets
    }

    return transcription_json

def transcribe(processor, model, audio):
    # Prepare the audio for the model
    inputs = processor(audio, return_tensors="pt", sampling_rate=16000)
    
    # Perform transcription
    with torch.no_grad():
        logits = model(input_values=inputs.input_values).logits
    predicted_ids = torch.argmax(logits, dim=-1)
    transcription = processor.batch_decode(predicted_ids)[0]
    
    return transcription

def monitor_resources(file_path):
    segments = segment_audio(file_path)
    all_transcriptions = []
    all_snippets = []
    
    for i, (start_time, end_time) in enumerate(segments):
        start_time_seconds = start_time / 1000
        end_time_seconds = end_time / 1000

        # Record the start time and resource usage
        start_time_process = time.time()
        start_cpu_percent = psutil.cpu_percent(interval=None)
        start_memory_info = psutil.virtual_memory().used / (1024 * 1024)  # Convert to MB

        # Read audio file and perform transcription
        audio, sample_rate = sf.read(file_path, always_2d=False)
        if sample_rate != 16000:
            # Resample to 16kHz if necessary
            audio = librosa.resample(audio, sample_rate, 16000)
        transcription = transcribe(processor, model, audio)  # Use the updated transcribe function

        # Record the end time and resource usage
        end_time_process = time.time()
        end_cpu_percent = psutil.cpu_percent(interval=None)
        end_memory_info = psutil.virtual_memory().used / (1024 * 1024)  # Convert to MB

        # Calculate elapsed time
        elapsed_time = end_time_process - start_time_process

        # Collect transcriptions and snippets for each segment
        snippet = {
            "start_time": str(timedelta(seconds=start_time_seconds)),
            "end_time": str(timedelta(seconds=end_time_seconds)),
            "text_content": transcription
        }
        all_snippets.append(snippet)

        # Print the results for each segment
        print(json.dumps(snippet, indent=2))
        print(f"Segment {i+1}: Elapsed time: {elapsed_time:.2f} seconds")
        print(f"CPU usage at end: {end_cpu_percent}%")
        print(f"Memory used at start: {start_memory_info:.2f} MB")
        print(f"Memory used at end: {end_memory_info:.2f} MB")

    # Combine all transcriptions into a single JSON output
    combined_transcriptions = format_transcription(file_path, [snippet['text_content'] for snippet in all_snippets], all_snippets)
    
    return combined_transcriptions

print('-------------------------------Transformer-------------------------------------------')
print()
print('--------------------------audio1_converted.wav---------------------------------------')
print(json.dumps(monitor_resources(ENGPATH1), indent=2))
print('--------------------------audio2_converted.wav---------------------------------------')
print(json.dumps(monitor_resources(ENGPATH2), indent=2))
print('--------------------------audio3_converted.wav---------------------------------------')
print(json.dumps(monitor_resources(ENGPATH3), indent=2))
