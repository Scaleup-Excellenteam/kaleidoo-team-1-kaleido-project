from flask import Flask, request, render_template, redirect, url_for, flash, jsonify
import os
import subprocess
import threading
from transcription import Transcriptor
from db_reader import DB

app = Flask(__name__)
app.secret_key = 'your_secret_key'
UPLOAD_FOLDER = 'uploads'
DBPATH = 'db.txt'
TRANSCRIPTIONS_DIR = 'transcriptions'
OUTPUT_FILE = 'combined_transcriptions.json'

ALLOWED_EXTENSIONS = {
    'mp4', 'aac', 'bmp', 'csv', 'doc', 'docx', 'epub', 'flac', 'gif',
    'html', 'jpeg', 'jpg', 'json', 'm4a', 'md', 'msg', 'mp3', 'odt',
    'ogg', 'pdf', 'png', 'rst', 'rtf', 'svg', 'tex', 'tiff', 'txt',
    'wav', 'wma', 'xlsx', 'xml', 'webp'
}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Utility function to check file extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Index route
@app.route('/')
def index():
    return render_template('index.html')

# Progress checking endpoint
@app.route('/progress')
def progress():
    try:
        with open('status.txt', 'r') as f:
            status_content = f.read()
    except FileNotFoundError:
        status_content = 'Processing...'

    return jsonify({'status': status_content})

# File upload route
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'files' not in request.files:
        flash('No file part')
        return redirect(request.url)
    
    files = request.files.getlist('files')
    uploaded_files = 0
    for file in files:
        if file.filename == '':
            continue
        if file and allowed_file(file.filename):
            filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filename)
            uploaded_files += 1
    
    if uploaded_files > 0:
        flash(f'Successfully uploaded {uploaded_files} file(s).')
        
        # Execute initialization script or any required process
        try:
            subprocess.run(['./init.sh', app.config['UPLOAD_FOLDER']], check=True)
            flash('Initialization script executed successfully.')
        except subprocess.CalledProcessError as e:
            flash(f'Error running initialization script: {e}')
    else:
        flash('No valid files uploaded.')
    
    return redirect(url_for('index'))

# Transcription process route
@app.route('/transcribe', methods=['POST'])
def transcribe_files():
    def run_transcription():
        try:
            # Initialize status
            with open('status.txt', 'w') as f:
                f.write('Transcription started...')
            
            # Read the DB and run the Transcriptor
            db = DB(DBPATH)
            files = db.read_db()
            for file in files:
                Transcriptor(file)
                # Update status (optional, can show file being processed)
                with open('status.txt', 'w') as f:
                    f.write(f'Transcribing {file}...')
            
            # Write final status
            with open('status.txt', 'w') as f:
                f.write('Transcription completed.')

            # Merge all transcriptions into one JSON file
            try:
                subprocess.run(['./compine_json.sh'], check=True)
                flash('JSON files merged successfully.')
            except subprocess.CalledProcessError as e:
                flash(f'Error running JSON merge script: {e}')
       
        except Exception as e:
            with open('status.txt', 'w') as f:
                f.write(f'Error during transcription: {e}')
    
    # Run transcription in a separate thread
    thread = threading.Thread(target=run_transcription)
    thread.start()

    return jsonify({'message': 'Transcription started'}), 202

# Status route for transcription progress
@app.route('/status')
def status():
    try:
        with open('status.txt', 'r') as f:
            status_content = f.read()
    except FileNotFoundError:
        status_content = 'Status file not found. Please check if the transcription was started.'

    return render_template('status.html', status=status_content)

if __name__ == '__main__':
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    if not os.path.exists(TRANSCRIPTIONS_DIR):
        os.makedirs(TRANSCRIPTIONS_DIR)
    app.run(debug=True)
