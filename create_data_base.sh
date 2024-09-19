#!/bin/bash

# Define the root directory for data in the current directory
ROOT_DIR="./Data"

# Check if the root Data directory exists
if [ ! -d "$ROOT_DIR" ]; then
    echo "Root directory $ROOT_DIR does not exist. Creating directories..."
    
    # Define the subdirectories to be created
    SUBDIRECTORIES=(
        "Audio_Data/English"
        "Audio_Data/Hebrow"
        "Audio_Data/Russian"
        "Audio_Data/vosk-model-small-en-us-0.15/am"
        "Audio_Data/vosk-model-small-en-us-0.15/conf"
        "Audio_Data/vosk-model-small-en-us-0.15/graph"
        "Audio_Data/vosk-model-small-en-us-0.15/graph/phones"
        "Audio_Data/vosk-model-small-en-us-0.15/ivector"
        "Audio_Data/vosk-model-small-ru-0.22/am"
        "Audio_Data/vosk-model-small-ru-0.22/conf"
        "Audio_Data/vosk-model-small-ru-0.22/graph"
        "Audio_Data/vosk-model-small-ru-0.22/graph/phones"
        "Audio_Data/vosk-model-small-ru-0.22/ivector"
        "Data_Dumper/Audio"
        "Data_Dumper/Text"
        "Data_Dumper/Video"
        "Text_Data/docs"
        "Text_Data/pdf"
        "Video_Data/English"
        "Video_Data/Hebrow"
    )

    # Create the root directory if it doesn't exist
    mkdir -p "$ROOT_DIR"
    echo "Created root directory: $ROOT_DIR"

    # Create each subdirectory
    for dir in "${SUBDIRECTORIES[@]}"; do
        full_path="$ROOT_DIR/$dir"
        if [ ! -d "$full_path" ]; then
            mkdir -p "$full_path"
            echo "Created directory: $full_path"
        else
            echo "Directory already exists: $full_path"
        fi
    done

    echo "All specified directories have been created."
else
    echo "Root directory $ROOT_DIR already exists. No directories were created."
fi
