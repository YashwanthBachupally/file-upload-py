import os
from flask import Flask, request, redirect, url_for, send_from_directory, render_template, abort
from werkzeug.utils import secure_filename
from datetime import datetime
from config import UPLOAD_FOLDER, MAX_CONTENT_LENGTH, ALLOWED_EXTENSIONS
import db

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
db.init_db()

def allowed_file(filename):
    if ALLOWED_EXTENSIONS is None:
        return True
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            if os.path.exists(filepath):
                name, ext = os.path.splitext(filename)
                filename = f"{name}_{int(datetime.now().timestamp())}{ext}"
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            db.insert_file(filename, datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            return redirect(url_for('index'))
    files = db.get_files()
    return render_template('index.html', files=files)

@app.route('/files/<int:file_id>')
def download_file(file_id):
    file = db.get_file(file_id)
    if file:
        filename = file[0]
        db.increment_download_count(file_id)
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)
    else:
        abort(404)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
