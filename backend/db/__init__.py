# atlas/backend/init_db_script.py
from backend.db.connection import init_db

init_db()
print("Tables created.")