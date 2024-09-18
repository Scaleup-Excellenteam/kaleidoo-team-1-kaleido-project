import whisper
from pydub import AudioSegment
import json
import datetime
import numpy as np
import time
import psutil
import os
import soundfile as sf
from langdetect import detect
from moviepy.editor import VideoFileClip  # For video processing
from paths import *

class AudioTranscriptor:
    def __init__(self,  video_path: str, model_name="base"):
        self.model = whisper.load_model(model_name)
        self.video_path = video_path
    
    def transcribe_audio_segment(self, segment_path):
        audio = whisper.load_audio(segment_path)
        audio = whisper.pad_or_trim(audio)
        result = self.model.transcribe(audio)
        return result["text"]

    def format_time(self, ms):
        return str(datetime.timedelta(milliseconds=ms))

    def transcribe_segment(self, file_path, start_time, end_time):
        audio = AudioSegment.from_wav(file_path)
        segment = audio[start_time:end_time]
        segment.export("segment.wav", format="wav")
        speech, sample_rate = sf.read("segment.wav")

        transcript = self.transcribe_audio_segment("segment.wav")
        return transcript

    def segment_and_transcribe(self, file_path, interval_ms, output_json_path=None, file_type="audio"):
        audio = AudioSegment.from_file(file_path)
        duration_ms = len(audio)
        num_segments = int(np.ceil(duration_ms / interval_ms))

        transcript_data = []

        for i in range(num_segments):
            start_time_ms = i * interval_ms
            end_time_ms = min((i + 1) * interval_ms, duration_ms)

            segment_file_path = f"{GARBAGE}segment_{i + 1}.wav"
            segment = audio[start_time_ms:end_time_ms]
            segment.export(segment_file_path, format="wav")

            transcript = self.transcribe_audio_segment(segment_file_path)

            transcript_data.append({
                "offset": f'{self.format_time(start_time_ms)}, {self.format_time(end_time_ms)}',
                "text": transcript,
                'lang': detect(transcript),
                "type": file_type,
                "ref": self.video_path
            })
            os.remove(segment_file_path)

        if output_json_path:
            with open(output_json_path, 'a+') as f:
                f.seek(0)
                try:
                    existing_data = json.load(f)
                except json.JSONDecodeError:
                    existing_data = []

                existing_data.append(
                     transcript_data
                )
                f.seek(0)
                f.truncate()

                json.dump(existing_data, f, ensure_ascii=False, indent=4)

                print(f'Data successfully written to {output_json_path}')
        else:
            return json.dumps(transcript_data, indent=4)

    def monitor_resources(self, file_path, time_interval, output_json=None, file_type="audio"):
        # Record the start time and resource usage
        start_time = time.time()
        start_cpu_percent = psutil.cpu_percent(interval=None)
        start_memory_info = psutil.virtual_memory().used / (1024 * 1024)  # Convert to MB

        # Transcription process
        transcript_output = self.segment_and_transcribe(file_path, time_interval, output_json, file_type)

        # Record the end time and resource usage
        end_time = time.time()
        end_cpu_percent = psutil.cpu_percent(interval=None)
        end_memory_info = psutil.virtual_memory().used / (1024 * 1024)  # Convert to MB

        # Calculate elapsed time
        elapsed_time = end_time - start_time

        # Print the results
        print(f"Elapsed time: {elapsed_time:.2f} seconds")
        print(f"CPU usage at end: {end_cpu_percent}%")
        print(f"Memory used at start: {start_memory_info:.2f} MB")
        print(f"Memory used at end: {end_memory_info:.2f} MB")

        return transcript_output

    def convert_video_to_audio(self, output_audio_path):
        """Convert video to audio (wav format)."""
        video_clip = VideoFileClip(self.video_path)
        video_clip.audio.write_audiofile(output_audio_path, codec='pcm_s16le')
        return output_audio_path

# Example usage for videos
if __name__ == "__main__":
    time_interval_ms = 80000  # Segment length in milliseconds (e.g., 80000 ms = 80 seconds)
    output_json = f'{DUMPVIDEO}video_transcriptions.json'  # Output JSON file path

    transcriptor = AudioTranscriptor(f'{HEBROWVIDEO}elazar.mp4')


    wav_file = transcriptor.convert_video_to_audio(f'{ENGLISHAUDIO}temp.wav')
    transcriptor.monitor_resources(wav_file, time_interval_ms, output_json)
