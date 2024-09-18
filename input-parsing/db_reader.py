import os
import logging

class DB:
    def __init__(self, db_path: str = 'db.txt') -> None:
        self.db_path = db_path
        # Set up logging configuration
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)

    def read_db(self):
        try:
            self.logger.info(f"Attempting to read file paths from {self.db_path}.")
            # Open the database file in read mode
            with open(self.db_path, 'r') as f:
                # Iterate through each line in the file
                for line in f:
                    # Strip any leading/trailing whitespace (like newlines)
                    file_path = line.strip()
                    # Check if the path exists and is a file
                    if os.path.isfile(file_path):
                        yield file_path
                        self.logger.info(f"Valid file path: {file_path}")
                    else:
                        self.logger.warning(f"Invalid path or file does not exist: {file_path}")
        except FileNotFoundError:
            self.logger.error(f"The file {self.db_path} does not exist.")
        except IOError as e:
            self.logger.error(f"Error reading file {self.db_path}: {e}")

        

# Example usage
if __name__ == "__main__":
    reader = DB('db.txt')
    files = reader.read_db()
    logging.info("Valid file paths:")
    for file in files:
        logging.info(file)
