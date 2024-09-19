#!/bin/bash

# List of supported formats
SUPPORTED_FORMATS=('mp4' 'aac' 'bmp' 'csv' 'doc' 'docx' 'epub' 'flac' 'gif' 'html' 'jpeg' 'jpg' 'm4a' 'md' 'msg' 'mp3' 'odt' 'ogg' 'pdf' 'png' 'rst' 'rtf' 'svg' 'tex' 'tiff' 'txt' 'wav' 'wma' 'xlsx' 'xml' 'webp')

# Check if a directory argument is provided
if [ "$#" -ne 1 ]; then
    echo "Usage: $0 /path/to/start/directory"
    exit 1
fi

# Set the starting directory from the argument
start_dir="$1"

# Check if the provided argument is a directory
if [ ! -d "$start_dir" ]; then
    echo "Error: $start_dir is not a valid directory."
    exit 1
fi

# Check if db.txt exists, and if so, delete it
if [ -f "db.txt" ]; then
    echo "db.txt exists, deleting it."
    rm "db.txt"
fi

# Function to get the file extension
get_file_extension() {
    local filename="$1"
    echo "${filename##*.}" | tr '[:upper:]' '[:lower:]'  # Get the file extension and convert to lowercase
}

# Function to check if a file extension is in the SUPPORTED_FORMATS array
is_supported_format() {
    local ext="$1"
    for format in "${SUPPORTED_FORMATS[@]}"; do
        if [[ "$format" == "$ext" ]]; then
            return 0  # True: the format is supported
        fi
    done
    return 1  # False: the format is not supported
}

# Function to recursively list files with absolute paths, filtering by supported formats
list_files_with_absolute_paths() {
    local dir="$1"

    # Find files and filter by supported formats
    find "$dir" -type f | while read -r file; do
        extension=$(get_file_extension "$file")
        if is_supported_format "$extension"; then
            realpath "$file" >> db.txt
        fi
    done
}

# Print all absolute file paths from the starting directory
echo "Listing all absolute file paths from $start_dir:"
list_files_with_absolute_paths "$start_dir"
