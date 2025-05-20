from flask import Flask, request, redirect, url_for, send_from_directory, render_template_string
import os
import sqlite3
from datetime import datetime

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
DATABASE = 'file_data.db'

# Ensure the upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize the SQLite database
def init_db():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS files (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    filename TEXT NOT NULL,
                    upload_time TEXT NOT NULL,
                    download_count INTEGER NOT NULL DEFAULT 0
                )''')
    conn.commit()
    conn.close()

init_db()

# Route to display the upload form and list of files
@app.route('/')
def index():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('SELECT id, filename, upload_time, download_count FROM files')
    files = c.fetchall()
    conn.close()
    return render_template_string('''
<!doctype html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>File Upload</title>
  <style>
    body {
      background-color: #B00058;
      color: #ffffff;
      font-family: Arial, sans-serif;
      text-align: center;
      padding: 40px;
    }
    form {
      margin-bottom: 30px;
    }
    input[type="file"] {
      margin: 10px;
    }
    ul {
      list-style-type: none;
      padding: 0;
    }
    li {
      margin: 10px 0;
    }
    a {
      color: #00bfff;
      text-decoration: none;
    }
    a:hover {
      text-decoration: underline;
    }
  </style>
</head>
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


# Route to handle file uploads
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

        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        c.execute('INSERT INTO files (filename, upload_time) VALUES (?, ?)',
                  (filename, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
        conn.commit()
        conn.close()

        return redirect(url_for('index'))

# Route to handle file downloads and increment download count
@app.route('/files/<int:file_id>')
def download_file(file_id):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('SELECT filename FROM files WHERE id = ?', (file_id,))
    file = c.fetchone()
    if file:
        filename = file[0]
        c.execute('UPDATE files SET download_count = download_count + 1 WHERE id = ?', (file_id,))
        conn.commit()
        conn.close()
        return send_from_directory(UPLOAD_FOLDER, filename)
    conn.close()
    return 'File not found', 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

