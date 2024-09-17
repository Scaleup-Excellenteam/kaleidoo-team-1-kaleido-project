import json
from unstructured.partition.pdf import partition_pdf
from langdetect import detect_langs, LangDetectException
from paths import DUMPTEXT

class PDFProcessor:
    def __init__(self, filename):
        """Initialize with the path to the PDF file."""
        self.filename = filename
        self.elements = []

    def partition_pdf_file(self):
        """Parse the PDF and extract elements."""
        try:
            self.elements = partition_pdf(self.filename)
        except Exception as e:
            raise RuntimeError(f"Error while partitioning PDF: {e}")

    def elements_to_dict(self):
        """Convert the extracted elements to dictionaries."""
        return [el.to_dict() for el in self.elements]


class PDFDataRefiner:
    def __init__(self, element_data):
        """Initialize with the element data."""
        self.data = element_data

    def refine_pdf_data(self):
        """Refine the PDF element data."""
        text = self.data.get("text", "")

        # Try to detect language if text is not empty or too short
        if len(text.strip()) > 5:  # Arbitrarily set threshold for minimum text length
            try:
                lang = detect_langs(text)[0].lang
            except LangDetectException:
                lang = 'unknown'  # Default to 'unknown' if detection fails
        else:
            lang = 'unknown'  # Default for short or empty texts

        # Prepare the refined data structure
        refined_data = {
            "type": self.data['metadata'].get('filetype', 'pdf'),
            "text": text,
            "metadata": {
                "offset": f"page{self.data['metadata'].get('page_number', '')}",
                "ref": f"{self.data['metadata'].get('file_directory', '')}/{self.data['metadata'].get('filename', '')}",
                "lang": lang,
                "filetype": self.data['metadata'].get('filetype', 'pdf')
            }
        }
        
        return refined_data


class PDFPipeline:
    def __init__(self, pdf_filename, output_filename):
        """Initialize with the input and output filenames."""
        self.pdf_filename = pdf_filename
        self.output_filename = output_filename

    def run(self):
        """Run the entire PDF processing and refining pipeline."""
        # Step 1: Partition the PDF
        processor = PDFProcessor(self.pdf_filename)
        processor.partition_pdf_file()
        element_dicts = processor.elements_to_dict()

        # Step 2: Refine the data
        refined_data = []
        for data in element_dicts:
            refiner = PDFDataRefiner(data)
            refined_data.append(refiner.refine_pdf_data())

        # Step 3: Save the refined data to a JSON file
        self.save_to_json(refined_data)

    def save_to_json(self, data):
        """Save the refined data to a JSON file."""
        with open(self.output_filename, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"Data saved to {self.output_filename}")


if __name__ == "__main__":
    # Example usage of the pipeline
    pdf_filename = "/home/ameer/Kaleidoo/Data/Text-Data/pdf/Kaleidoo-Research-Phase.pdf"
    output_filename = f"{DUMPTEXT}/pdf.json"

    pipeline = PDFPipeline(pdf_filename, output_filename)
    pipeline.run()
