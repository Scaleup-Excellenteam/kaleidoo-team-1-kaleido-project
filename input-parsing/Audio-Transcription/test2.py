import whisper
from pydub import AudioSegment
import json
import datetime
import numpy as np 
import os 


def transcribe_audio_segment(segment_path):
    model = whisper.load_model("base")
    audio = whisper.load_audio(segment_path)
    audio = whisper.pad_or_trim(audio)
    result = model.transcribe(audio)
    return result["text"]

def format_time(ms):
    return str(datetime.timedelta(milliseconds=ms))

def segment_and_transcribe(file_path, interval_ms, output_json_path):
    audio = AudioSegment.from_file(file_path)
    duration_ms = len(audio)
    num_segments = int(np.ceil(duration_ms / interval_ms))
    
    transcript_data = []
    
    for i in range(num_segments):
        start_time_ms = i * interval_ms
        end_time_ms = min((i + 1) * interval_ms, duration_ms)
        
        segment = audio[start_time_ms:end_time_ms]
        segment_file_path = f"segment_{i + 1}.wav"
        segment.export(segment_file_path, format="wav")
        
        transcript = transcribe_audio_segment(segment_file_path)
        
        transcript_data.append({
            "source_type": "audio",
            "source_name": file_path.split("/")[-1],
            "start_time": format_time(start_time_ms),
            "end_time": format_time(end_time_ms),
            "text_content": transcript
        })
        os.remove(segment_file_path)
    
    
    if output_json_path :
        with open(output_json_path, 'a+') as f:
            f.seek(0)
            try:
                existing_data = json.load(f)
            except json.JSONDecodeError:
                existing_data = []
            existing_data.append({
                       "source_type": "audio",
                        "source_name": file_path.split("/")[-1],
                        'data': transcript_data,
                        })
            f.seek(0)
            f.truncate()

            json.dump(existing_data, f,indent=4)

            print(f'Data successfully written to {file_path}')    
    else:
        return json.dumps(transcript_data, indent=4)

# Example usage
if __name__ == "__main__":
    input_file = "/home/ameer/Kaleidoo/Audio_Data/English/A1.wav"  # Replace with your audio file path
    time_interval_ms = 10000  # Segment length in milliseconds (e.g., 10000 ms = 10 seconds)
    output_json = "transcriptions.json"  # Output JSON file path
    
    segment_and_transcribe(input_file, time_interval_ms, output_json)
