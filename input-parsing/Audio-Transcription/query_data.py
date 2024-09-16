import whisper

def transcribe_audio_with_timestamps(audio_file):
    model = whisper.load_model("base")
    result = model.transcribe(audio_file, word_timestamps=True)
    return result

def search_transcription(query, transcription_result):
    matches = []
    for segment in transcription_result['segments']:
        if query.lower() in segment['text'].lower():
            matches.append({
                'start': segment['start'],
                'end': segment['end'],
                'text': segment['text']
            })
    return matches

def main(audio_file, query):
    # Transcribe the audio
    transcription_result = transcribe_audio_with_timestamps(audio_file)

    # Search for the query in the transcription
    matches = search_transcription(query, transcription_result)

    # Print results
    for match in matches:
        print(f"Found '{query}' from {match['start']:.2f} s to {match['end']:.2f} s: {match['text']}")

# Example usage
audio_file = "path/to/your/audiofile.mp3"
query = "linear algebra"
main(audio_file, query)
