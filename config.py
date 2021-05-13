"""Flask configuration"""

UPLOAD_EXTENSIONS = ['png', 'jpg', 'jpeg']
UPLOAD_FOLDER = 'received'
MAX_CONTENT_LENGTH = 20 * 1024 * 1024 # 20MB max for an upload
MAX_CONCURRENT_REQUESTS = 4