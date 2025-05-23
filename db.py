import sqlite3
import os
from datetime import datetime, timedelta
from config import DATABASE, UPLOAD_FOLDER

def init_db():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            upload_time TEXT NOT NULL,
            download_count INTEGER NOT NULL DEFAULT 0,
            expires_at TEXT NOT NULL
        )
    """)
    
    # Check if expires_at column exists (for existing databases)
    c.execute("PRAGMA table_info(files)")
    columns = [column[1] for column in c.fetchall()]
    if 'expires_at' not in columns:
        c.execute('ALTER TABLE files ADD COLUMN expires_at TEXT')
        # Set default expiration for existing files (10 minutes from now)
        default_expiration = (datetime.now() + timedelta(minutes=10)).isoformat()
        c.execute('UPDATE files SET expires_at = ? WHERE expires_at IS NULL', (default_expiration,))
    
    conn.commit()
    conn.close()

def insert_file(filename, upload_time, expiration_minutes=10):
    """Insert a new file with expiration time"""
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    
    # Calculate expiration time
    upload_dt = datetime.fromisoformat(upload_time)
    expires_at = (upload_dt + timedelta(minutes=expiration_minutes)).isoformat()
    
    c.execute('INSERT INTO files (filename, upload_time, expires_at) VALUES (?, ?, ?)', 
              (filename, upload_time, expires_at))
    conn.commit()
    conn.close()

def get_files():
    """Get all non-expired files"""
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    current_time = datetime.now().isoformat()
    c.execute('''SELECT id, filename, upload_time, download_count, expires_at 
                 FROM files 
                 WHERE expires_at > ? 
                 ORDER BY upload_time DESC''', (current_time,))
    files = c.fetchall()
    conn.close()
    return files

def get_file(file_id):
    """Get a specific file if it hasn't expired"""
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    current_time = datetime.now().isoformat()
    c.execute('SELECT filename FROM files WHERE id = ? AND expires_at > ?', (file_id, current_time))
    file = c.fetchone()
    conn.close()
    return file

def increment_download_count(file_id):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('UPDATE files SET download_count = download_count + 1 WHERE id = ?', (file_id,))
    conn.commit()
    conn.close()

def cleanup_expired_files():
    """Remove expired files from database and filesystem"""
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    current_time = datetime.now().isoformat()
    
    # Get expired files
    c.execute('SELECT filename FROM files WHERE expires_at <= ?', (current_time,))
    expired_files = c.fetchall()
    
    # Delete expired files from filesystem
    deleted_count = 0
    for (filename,) in expired_files:
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                deleted_count += 1
        except OSError as e:
            print(f"Error deleting file {filename}: {e}")
    
    # Delete expired files from database
    c.execute('DELETE FROM files WHERE expires_at <= ?', (current_time,))
    db_deleted = c.rowcount
    
    conn.commit()
    conn.close()
    
    print(f"Cleanup completed: {deleted_count} files deleted from filesystem, {db_deleted} records removed from database")
    return deleted_count

def get_expired_files():
    """Get list of expired files for manual review"""
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    current_time = datetime.now().isoformat()
    c.execute('''SELECT id, filename, upload_time, expires_at 
                 FROM files 
                 WHERE expires_at <= ?
                 ORDER BY expires_at DESC''', (current_time,))
    files = c.fetchall()
    conn.close()
    return files

def extend_file_expiration(file_id, additional_minutes=10):
    """Extend expiration time for a specific file"""
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    
    # Get current expiration
    c.execute('SELECT expires_at FROM files WHERE id = ?', (file_id,))
    result = c.fetchone()
    
    if result:
        current_expiration = datetime.fromisoformat(result[0])
        new_expiration = (current_expiration + timedelta(minutes=additional_minutes)).isoformat()
        c.execute('UPDATE files SET expires_at = ? WHERE id = ?', (new_expiration, file_id))
        conn.commit()
        success = c.rowcount > 0
    else:
        success = False
    
    conn.close()
    return success
