from flask import Flask, request, redirect, url_for, send_from_directory, render_template_string
import os
from datetime import datetime
from db import init_db, insert_file, fetch_files, fetch_file_by_id, increment_download_count

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app = Flask(__name__)

@app.route('/')
def index():
    files = fetch_files()
    return render_template_string('''
    <!doctype html>
    <html lang="en">
    <head> ... (your HTML remains same) ... </head>
    <body>
      <h1>Upload a File</h1>
      <form method="post" enctype="multipart/form-data">
        <input type="file" name="file">
        <input type="submit" value="Upload">
      </form>
      <h2>Uploaded Files</h2>
      <ul>
        {% for file in files %}
          <li>
            <a href="{{ url_for('download_file', file_id=file[0]) }}">{{ file[1] }}</a>
            ({{ file[2] }}) - Downloads: {{ file[3] }}
          </li>
        {% endfor %}
      </ul>
    </body>
    </html>
    ''', files=files)

@app.route('/', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        return redirect(request.url)
    if file:
        filename = file.filename
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        insert_file(filename, datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        return redirect(url_for('index'))

@app.route('/files/<int:file_id>')
def download_file(file_id):
    file = fetch_file_by_id(file_id)
    if file:
        increment_download_count(file_id)
        return send_from_directory(UPLOAD_FOLDER, file[0])
    return 'File not found', 404
