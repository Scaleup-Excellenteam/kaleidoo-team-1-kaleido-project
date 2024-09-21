import json
from partition import partition_file  # Updated import
from langdetect import detect_langs, LangDetectException
from paths import * 
import uuid

def generate_unique_filename(extension):
    unique_id = uuid.uuid4().hex
    return f"{unique_id}.{extension}"

class FileProcessor:
    def __init__(self, filename):
        """Initialize with the path to the file."""
        self.filename = filename
        self.elements = []

    def partition_file(self):
        """Parse the file and extract elements."""
        try:
            self.elements = partition_file(self.filename)
        except Exception as e:
            raise RuntimeError(f"Error while partitioning file: {e}")

    def elements_to_dict(self):
        """Convert the extracted elements to dictionaries."""
        return [el.to_dict() for el in self.elements]

class DataRefiner:
    def __init__(self, element_data, remaining_text=""):
        """Initialize with the element data and any remaining text from previous chunks."""
        self.data = element_data
        self.remaining_text = remaining_text  # Text carried over from previous chunks

    def refine_data(self):
        """Refine the element data."""
        text = self.remaining_text + self.data.get("text", "")
        page_number = self.data['metadata'].get('page_number', '')

        # Chunk the text into sections of approximately 1000 characters
        sentences, remaining_text = self.chunk_text(text)

        refined_sentences = []
        for sentence in sentences:
            # Try to detect language if the sentence is not empty or too short
            if len(sentence.strip()) > 5:  # Arbitrary threshold for minimum text length
                try:
                    lang = detect_langs(sentence)[0].lang
                except LangDetectException:
                    lang = 'unknown'  # Default to 'unknown' if detection fails
            else:
                lang = 'unknown'  # Default for short or empty texts

            # Prepare the refined sentence structure
            refined_data = {
                "filetype": self.data['metadata'].get('filetype', 'unknown'),
                "text": sentence,
                "offset": f"page{page_number}",
                "ref": f"{self.data['metadata'].get('file_directory', '')}/{self.data['metadata'].get('filename', '')}",
                "lang": lang
            }
            
            refined_sentences.append(refined_data)

        # Return both the refined sentences and any remaining text
        return refined_sentences, remaining_text

    def chunk_text(self, text):
        """Split the text into chunks of around 1000 characters."""
        chunks = []
        max_chars = 1000
        start = 0

        # Process text in chunks of 1000 characters
        while start < len(text):
            end = start + max_chars
            # Ensure we don't cut words in the middle
            if end < len(text) and text[end] != ' ':
                end = text.rfind(' ', start, end)  # Try to cut at the last space within this range
                if end == -1:
                    end = start + max_chars  # If no space is found, cut exactly at 1000 chars
            
            chunk = text[start:end].strip()
            chunks.append(chunk)
            start = end

        remaining_text = text[start:].strip()  # Keep any remaining text to append to the next chunk
        return chunks, remaining_text

class Pipeline:
    def __init__(self, file_filename, output_filename):
        """Initialize with the input and output filenames."""
        self.file_filename = file_filename
        self.output_filename = output_filename
        self.remaining_text = ""  # Track text carried over between chunks
        self.last_refined = None  # Track the last refined element

    def run(self):
        """Run the entire file processing and refining pipeline."""
        # Step 1: Partition the file
        elements = partition_file(self.file_filename)
        element_dicts = [el.to_dict() for el in elements]

        # Step 2: Refine the data
        refined_data = []
        for data in element_dicts:
            refiner = DataRefiner(data, self.remaining_text)
            refined_sentences, self.remaining_text = refiner.refine_data()  # Save remaining text
            
            # Step 3: Check if the last sentence is under 1000 characters and from the same page
            if self.last_refined and len(self.last_refined["text"]) < 1000:
                current_page = refined_sentences[0]["offset"] if refined_sentences else None
                if current_page == self.last_refined["offset"]:  # Check if it's the same page
                    # Concatenate the last refined text with the first sentence from the current page
                    self.last_refined["text"] += "\n" + refined_sentences[0]["text"]
                    
                    # Update the language of the concatenated text
                    combined_text = self.last_refined["text"]
                    if len(combined_text.strip()) > 5:
                        try:
                            lang = detect_langs(combined_text)[0].lang
                        except LangDetectException:
                            lang = 'unknown'
                    else:
                        lang = 'unknown'
                    self.last_refined["lang"] = lang
                    
                    # Remove the first sentence from the current batch
                    refined_sentences.pop(0)

            # Extend because multiple sentences can be generated
            refined_data.extend(refined_sentences)

            # Update last refined
            if refined_sentences:
                self.last_refined = refined_sentences[-1]  # Track the last refined element

        # Step 4: Save the refined data to a JSON file
        self.save_to_json(refined_data)

    def save_to_json(self, data):
        """Save the refined data to a JSON file."""
        with open(self.output_filename, 'w') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"Data saved to {self.output_filename}")

if __name__ == "__main__":
    # Example usage of the pipeline
    file_filename = f'{DOCS}interview-getting-ready.docx'
    output_filename = f"{DUMPTEXT}interview-getting-ready.json"

    pipeline = Pipeline(file_filename, output_filename)
    pipeline.run()
