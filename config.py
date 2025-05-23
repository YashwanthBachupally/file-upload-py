import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', os.path.join(BASE_DIR, 'uploads'))
DATABASE = os.environ.get('DATABASE', os.path.join(BASE_DIR, 'file_data.db'))
MAX_CONTENT_LENGTH = 2 * 1024 * 1024 * 1024  # 2 GB
ALLOWED_EXTENSIONS = None  # or set to ['txt', 'jpg'] etc.

# File expiration settings
DEFAULT_EXPIRATION_HOURS = int(os.environ.get('DEFAULT_EXPIRATION_HOURS', 24))  # 24 hours default
CLEANUP_ON_STARTUP = os.environ.get('CLEANUP_ON_STARTUP', 'true').lower() == 'true'
AUTO_CLEANUP_INTERVAL = int(os.environ.get('AUTO_CLEANUP_INTERVAL', 3600))  # 1 hour in seconds
