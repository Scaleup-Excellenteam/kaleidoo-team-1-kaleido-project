import os
import json

# Define the root directory for data
ROOT_DIR = "./Data/Data_Dumper"
OUTPUT_FILE = "combined_data.json"

# Initialize an empty list to hold combined data
combined_data = []

def merge_json_files(dir_path):
    global combined_data
    # Loop through all JSON files in the specified directory
    for file in os.listdir(dir_path):
        if file.endswith('.json'):
            file_path = os.path.join(dir_path, file)
            with open(file_path, 'r') as f:
                try:
                    content = json.load(f)
                    # Check if content is a list or a dictionary
                    if isinstance(content, list):
                        combined_data.extend(content)  # Append to list
                    elif isinstance(content, dict):
                        combined_data.append(content)  # Add as single object
                    else:
                        print(f"Unsupported JSON structure in {file_path}")
                    
                    # Delete the file if content is not empty
                    if content:  # Check if content is not empty
                        os.remove(file_path)
                        print(f"Deleted file: {file_path}")

                except json.JSONDecodeError:
                    print(f"Error reading JSON from {file_path}")

# Dynamically find subdirectories and merge JSON files
for dir_name in os.listdir(ROOT_DIR):
    dir_path = os.path.join(ROOT_DIR, dir_name)
    if os.path.isdir(dir_path):
        merge_json_files(dir_path)

# Write the combined data to the output file
with open(OUTPUT_FILE, 'w') as output_file:
    json.dump(combined_data, output_file, indent=4)

print(f"All JSON files have been combined into {OUTPUT_FILE}.")
