#!/bin/bash

# Define the root directory for data
ROOT_DIR="/home/ameer/Kaleidoo/Data/Data_Dumper"

# Output file
OUTPUT_FILE="combined_data.json"

# Initialize JSON structure
echo '{"Audio": {}, "Text": {}, "Video": {}}' > $OUTPUT_FILE

# Function to merge JSON files into a section
merge_json_files() {
    local section=$1
    local dir=$2

    # Loop through all JSON files in the specified directory
    for file in "$dir"/*.json; do
        if [ -f "$file" ]; then
            # Extract filename without path
            filename=$(basename "$file")

            # Read file content and remove enclosing braces
            content=$(cat "$file" | sed '1d;$d')

            # Insert content into the correct section of the combined JSON file
            jq --arg section "$section" --arg key "$filename" --argjson value "{$content}" \
                '.[$section][$key] = $value' $OUTPUT_FILE > temp.json && mv temp.json $OUTPUT_FILE
        fi
    done
}

# Dynamically find subdirectories and merge JSON files
for section in Audio Text Video; do
    section_dir="$ROOT_DIR/$section"
    if [ -d "$section_dir" ]; then
        merge_json_files "$section" "$section_dir"
    else
        echo "Directory $section_dir does not exist. Skipping."
    fi
done

echo "All JSON files have been combined into $OUTPUT_FILE."
