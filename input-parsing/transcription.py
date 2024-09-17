import logging
from transcriptor_audio import AudioTranscriptor
from transcriptor_text import 

# Set up logging configuration
logging.basicConfig(level=logging.INFO,  # Set level to INFO to capture all INFO messages
                    format='%(asctime)s - %(levelname)s - %(message)s')


class UnsupportedFileType(Exception):
    """Custom exception for unsupported file types."""
    pass


class FileMapper:
    """Maps the file format to the corresponding handler type."""
    
    MAPPED = {
        0: {'pdf', 'txt'},  # Text-based files
        1: {'jpg', 'jpeg'},  # Image files
        2: {'wav', 'mp3'}    # Audio files
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
            TestParser().parse(self.file)
        elif self.format_type == 1:
            logging.info(f"Processing image file: {self.file}")
            # Handle image file processing here
        elif self.format_type == 2:
            logging.info(f"Processing audio file: {self.file}")
            # Instantiate an audio transcriptor
            AudioTranscriptor().monitor_resources(self.file, 80000)
        else:
            logging.error(f"Unsupported processing type for file: {self.file}")
            raise UnsupportedFileType(f"Unsupported processing type for file: {self.file}")


class FileValidator:
    """Validates if a file has a supported format."""
    
    SUPPORTED_FORMATS = ['pdf', 'txt', 'jpg', 'jpeg', 'wav', 'mp3']

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
    files = ['/home/ameer/Kaleidoo/Data/Audio_Data/English/img-processing.mp3', 'audio.wav', 'image.jpg', 'video.mp4']
    transcriptor = Transcriptor(*files)
