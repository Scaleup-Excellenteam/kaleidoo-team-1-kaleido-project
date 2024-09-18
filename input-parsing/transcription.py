import logging
from transcriptor_audio import AudioTranscriptor
from transcriptor_video import VideoTranscriptor
from transcriptor_text import Pipeline
import uuid
from paths import * 

INTERVAL = 80000
VIDEO = 'video'
AUDIO = 'audio'
JSON = '.json'
# Set up logging configuration
logging.basicConfig(level=logging.INFO,  # Set level to INFO to capture all INFO messages
                    format='%(asctime)s - %(levelname)s - %(message)s')


def generate_unique_filename(extension):
    unique_id = uuid.uuid4().hex
    return f"{unique_id}{extension}"

def create_file(path):
    return f'{path}{generate_unique_filename(JSON)}'

class UnsupportedFileType(Exception):
    """Custom exception for unsupported file types."""
    pass


class FileMapper:
    """Maps the file format to the corresponding handler type."""
    
    MAPPED = {
    0: {'pdf', 'txt', 'doc', 'csv', 'docx', 'html', 'json', 'xml', 'xlsx', 'epub', 'msg', 'rst', 'odt', 'rtf', 'md', 'tex'},  # Text-based files
    1: {'mp3', 'aac', 'flac', 'ogg', 'wav', 'wma', 'm4a'},  # Audio files
    2: {'jpg', 'jpeg', 'png', 'gif', 'bmp', 'tiff', 'webp', 'svg'}  # Image files
    }


    def __init__(self, format: str):
        self.file_type = self.__eval__(format)

    def __eval__(self, format: str):
        """Evaluates the file type based on the format."""
        for k, v in self.MAPPED.items():
            if format in v:
                return k
        raise UnsupportedFileType(f"Unsupported file type: {format}")


class Factory:
    """Factory class that processes files based on their types."""
    
    def __init__(self, file: str, format_type: int):
        self.file = file
        self.format_type = format_type
        self.process_file()

    def process_file(self):
        """Processes the file based on its format type."""
        if self.format_type == 0:
            logging.info(f"Processing text file: {self.file}")
            # Instantiate a text parser or handle text file
            Pipeline(self.file, create_file(DUMPTEXT)).run()

        elif self.format_type == 1:
            logging.info(f"Processing audio file: {self.file}")
            at = AudioTranscriptor()
            at.segment_and_transcribe(self.file, INTERVAL, create_file(DUMPAUDIO))
        elif self.format_type == 2:
            logging.info(f"Processing video file: {self.file}")
            transcriptor = VideoTranscriptor(self.file)
            wav_file = transcriptor.convert_video_to_audio(self.file)
            transcriptor.monitor_resources(wav_file, INTERVAL, create_file(DUMPVIDEO), VIDEO)
        else:
            logging.error(f"Unsupported processing type for file: {self.file}")
            raise UnsupportedFileType(f"Unsupported processing type for file: {self.file}")


class FileValidator:
    """Validates if a file has a supported format."""
    
    SUPPORTED_FORMATS = ['mp4','aac', 'bmp', 'csv', 'doc', 'docx', 'epub', 'flac', 'gif', 'html', 'jpeg', 'jpg', 'json', 'm4a', 'md', 'msg', 'mp3', 'odt', 'ogg', 'pdf', 'png', 'rst', 'rtf', 'svg', 'tex', 'tiff', 'txt', 'wav', 'wma', 'xlsx', 'xml', 'webp']

    def __init__(self, file):
        self.file = file
        self.__format = None  # Stores the file format if valid

        logging.info(f"Validating file: {self.file}")

        if not self.__is_valid_file__():
            logging.error(f"Unsupported file type: {self.file}")
            raise UnsupportedFileType(f"Unsupported file type: {self.file}")

        logging.info(f"File passed validation: {self.file} (Format: {self.__format})")

    def __is_valid_file__(self):
        """Checks if the file has a valid format."""
        for format in self.SUPPORTED_FORMATS:
            if self.file.endswith(format):
                self.__format = format
                return True
        return False

    @property
    def file_format(self):
        """Returns the file format."""
        return self.__format


class Transcriptor:
    """Main class that validates and processes files."""
    
    def __init__(self, *args):
        self.files = args
        for file in args:
            try:
                validator = FileValidator(file)  # Validate the file
                self.__if_passed__process__(validator)
            except UnsupportedFileType as e:
                logging.warning(e)

    def __if_passed__process__(self, validator: FileValidator) -> None:
        """Processes the file if validation passed."""
        file_format = validator.file_format
        logging.info(f"Processing file: {validator.file} with format {file_format}")
        # Map the file format to a handler type and instantiate the factory
        format_type = FileMapper(file_format).file_type
        Factory(validator.file, format_type)


if __name__ == "__main__":
    # Example usage
    
    transcriptor = Transcriptor()
