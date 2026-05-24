"""WSGI entry point for production servers."""
import os
from app import app, db, create_admin

with app.app_context():
    db.create_all()
    create_admin()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
