from db import init_db
from web import app

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)
