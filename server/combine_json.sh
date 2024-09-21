#!/bin/bash

# Define the root directory for data
ROOT_DIR="../Data/Data_Dumper"

# Output file
OUTPUT_FILE="combined_data.json"

# Initialize JSON structure as an empty array
echo '[]' > $OUTPUT_FILE

# Function to merge JSON files into a single JSON array
merge_json_files() {
    local dir=$1

    # Loop through all JSON files in the specified directory
    for file in "$dir"/*.json; do
        if [ -f "$file" ]; then
            # Read file content
            content=$(cat "$file")

            # Check if content is an array or object
            if echo "$content" | jq -e 'type == "array"' > /dev/null; then
                # If content is an array, append it to the output array
                jq --argjson new_content "$content" \
                    '. += $new_content' $OUTPUT_FILE > temp.json && mv temp.json $OUTPUT_FILE
            elif echo "$content" | jq -e 'type == "object"' > /dev/null; then
                # If content is an object, merge it into the output object
                jq --argjson new_content "$content" \
                    '(. + $new_content)' $OUTPUT_FILE > temp.json && mv temp.json $OUTPUT_FILE
            else
                echo "Unsupported JSON structure in $file"
            fi
        fi
    done
}

# Dynamically find subdirectories and merge JSON files
for dir in "$ROOT_DIR"/*; do
    if [ -d "$dir" ]; then
        merge_json_files "$dir"
    fi
done

echo "All JSON files have been combined into $OUTPUT_FILE."
