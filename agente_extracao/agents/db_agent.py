import sqlite3

DB_PATH = "data/banco.db"

def insert_into_db(data):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS dados (id INTEGER PRIMARY KEY, conteudo TEXT)")
    
    for row in data:
        cursor.execute("INSERT INTO dados (conteudo) VALUES (?)", (str(row),))
    
    conn.commit()
    conn.close()

