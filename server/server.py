from flask import Flask, render_template, request, jsonify, send_file
import os
import subprocess
from threading import Semaphore
from transcription import Transcriptor
from flask_socketio import SocketIO
import time
from werkzeug.utils import secure_filename

app = Flask(__name__)
socketio = SocketIO(app)

UPLOAD_FOLDER = 'uploads'
COMBINED_FILE = 'combined_data.json'
CLEAN = './Data/Data_Dumper'




# Supported formats
SUPPORTED_FORMATS = [
    'mp4', 'aac', 'bmp', 'csv', 'doc', 'docx', 'epub', 'flac', 'gif', 'html', 
    'jpeg', 'jpg', 'm4a', 'md', 'msg', 'mp3', 'odt', 'ogg', 'pdf', 'png', 
    'rst', 'rtf', 'svg', 'tex', 'tiff', 'txt', 'wav', 'wma', 'xlsx', 'xml', 'webp'
]

# Function to get file extension and convert to lowercase
def get_file_extension(filename):
    return os.path.splitext(filename)[-1].lower().lstrip('.')

# Function to check if a file extension is supported
def is_supported_format(extension):
    return extension in SUPPORTED_FORMATS

# Function to recursively list files and write supported formats to db.txt
def list_files_with_absolute_paths(start_dir):
    with open("db.txt", "w") as db_file:
        for root, _, files in os.walk(start_dir):
            for file in files:
                extension = get_file_extension(file)
                if is_supported_format(extension):
                    abs_path = os.path.abspath(os.path.join(root, file))
                    db_file.write(abs_path + "\n")



if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

semaphore = Semaphore(1)



def clean_files_in_directory(directory):
    if os.path.exists(directory):
        for root, dirs, files in os.walk(directory):
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    os.remove(file_path)
                    print(f"Deleted file: {file_path}")
                except Exception as e:
                    print(f"Error deleting {file_path}: {e}")
    else:
        print(f"Directory {directory} does not exist.")
        

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload_file', methods=['POST'])
def upload_file():
    if 'files' not in request.files:
        return jsonify({'error': 'No files part'}), 400

    files = request.files.getlist('files')
    for file in files:
        if file.filename:
            filename = secure_filename(file.filename)
            file.save(os.path.join(UPLOAD_FOLDER, filename))

    return jsonify({'message': 'Files successfully uploaded'}), 200



@app.route('/delete_combined_file', methods=['DELETE'])
def delete_combined_file():
    try:
        os.remove(COMBINED_FILE)
        return jsonify({'message': 'File deleted successfully.'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/transcribe', methods=['POST'])
def transcribe_files():
    with semaphore:
        try:
            list_files_with_absolute_paths(UPLOAD_FOLDER)

            with open('db.txt', 'r') as db_file:
                file_paths = [line.strip() for line in db_file.readlines()]

            total_files = len(file_paths)
            processed_files = 0
            
            for file_path in file_paths:
                Transcriptor(file_path)
                processed_files += 1
                
                percentage = int((processed_files / total_files) * 100)
                socketio.emit('update progress', percentage)

            cleanup_files(file_paths)
            subprocess.run(['python', 'combine_json.py'], check=True)
            socketio.emit('transcription complete', f"/download/{COMBINED_FILE}")
            clean_files_in_directory(CLEAN)
            return jsonify({'message': 'Transcription completed and files deleted.'}), 200

        except Exception as e:
            cleanup_files(file_paths)
            return jsonify({'error': 'Transcription failed'}), 500


@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    return send_file(filename, as_attachment=True)

def cleanup_files(file_paths):
    for file_path in file_paths:
        if os.path.isfile(file_path):
            os.remove(file_path)

if __name__ == '__main__':
    socketio.run(app=app, debug=True)
