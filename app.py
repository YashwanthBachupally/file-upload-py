import os
import threading
import time
from flask import Flask, request, redirect, url_for, send_from_directory, render_template, abort, jsonify
from werkzeug.utils import secure_filename
from datetime import datetime
from config import (UPLOAD_FOLDER, MAX_CONTENT_LENGTH, ALLOWED_EXTENSIONS, 
                   DEFAULT_EXPIRATION_HOURS, CLEANUP_ON_STARTUP, AUTO_CLEANUP_INTERVAL)
import db

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
db.init_db()

# Cleanup expired files on startup
if CLEANUP_ON_STARTUP:
    print("Performing startup cleanup...")
    db.cleanup_expired_files()

def allowed_file(filename):
    if ALLOWED_EXTENSIONS is None:
        return True
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def periodic_cleanup():
    """Background thread function for periodic cleanup"""
    while True:
        time.sleep(AUTO_CLEANUP_INTERVAL)
        print("Running periodic cleanup...")
        db.cleanup_expired_files()

# Start background cleanup thread
cleanup_thread = threading.Thread(target=periodic_cleanup, daemon=True)
cleanup_thread.start()

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
            
            # Handle duplicate filenames
            if os.path.exists(filepath):
                name, ext = os.path.splitext(filename)
                filename = f"{name}_{int(datetime.now().timestamp())}{ext}"
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            
            file.save(filepath)
            
            # Get custom expiration hours from form (if provided)
            expiration_hours = request.form.get('expiration_hours', DEFAULT_EXPIRATION_HOURS, type=int)
            expiration_hours = max(1, min(expiration_hours, 168))  # Limit between 1 hour and 1 week
            
            db.insert_file(filename, datetime.now().isoformat(), expiration_hours)
            return redirect(url_for('index'))
    
    files = db.get_files()
    return render_template('index.html', files=files, default_expiration=DEFAULT_EXPIRATION_HOURS)

@app.route('/files/<int:file_id>')
def download_file(file_id):
    file = db.get_file(file_id)
    if file:
        filename = file[0]
        db.increment_download_count(file_id)
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)
    else:
        abort(404)

@app.route('/extend/<int:file_id>')
def extend_expiration(file_id):
    """Extend file expiration by default hours"""
    additional_hours = request.args.get('hours', DEFAULT_EXPIRATION_HOURS, type=int)
    additional_hours = max(1, min(additional_hours, 168))  # Limit between 1 hour and 1 week
    
    success = db.extend_file_expiration(file_id, additional_hours)
    if success:
        return jsonify({'status': 'success', 'message': f'Expiration extended by {additional_hours} hours'})
    else:
        return jsonify({'status': 'error', 'message': 'File not found'}), 404

@app.route('/cleanup')
def manual_cleanup():
    """Manual cleanup endpoint"""
    deleted_count = db.cleanup_expired_files()
    return jsonify({
        'status': 'success', 
        'message': f'Cleanup completed. {deleted_count} files removed.'
    })

@app.route('/stats')
def stats():
    """Show basic statistics"""
    files = db.get_files()
    expired_files = db.get_expired_files()
    
    total_size = 0
    for file in files:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file[1])
        if os.path.exists(file_path):
            total_size += os.path.getsize(file_path)
    
    stats_data = {
        'active_files': len(files),
        'expired_files': len(expired_files),
        'total_size_mb': round(total_size / (1024 * 1024), 2),
        'default_expiration_hours': DEFAULT_EXPIRATION_HOURS
    }
    
    return jsonify(stats_data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
