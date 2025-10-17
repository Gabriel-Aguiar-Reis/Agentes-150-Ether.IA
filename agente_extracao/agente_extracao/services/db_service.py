import sqlite3
import os

DB_PATH = "data/banco.db"

def init_db():
    os.makedirs("data", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS dados (id INTEGER PRIMARY KEY, conteudo TEXT)")
    conn.commit()
    conn.close()

