import sqlite3
from config import DATABASE

def init_db():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            upload_time TEXT NOT NULL,
            download_count INTEGER NOT NULL DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()

def insert_file(filename, upload_time):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('INSERT INTO files (filename, upload_time) VALUES (?, ?)', (filename, upload_time))
    conn.commit()
    conn.close()

def get_files():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('SELECT id, filename, upload_time, download_count FROM files ORDER BY upload_time DESC')
    files = c.fetchall()
    conn.close()
    return files

def get_file(file_id):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('SELECT filename FROM files WHERE id = ?', (file_id,))
    file = c.fetchone()
    conn.close()
    return file

def increment_download_count(file_id):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('UPDATE files SET download_count = download_count + 1 WHERE id = ?', (file_id,))
    conn.commit()
    conn.close()
