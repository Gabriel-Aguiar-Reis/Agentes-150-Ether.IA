import sqlite3
import os
from services.logging_service import logging_service

DB_PATH = "data/banco.db"

def insert_into_db(data):
    """Insere dados no banco e retorna o número de registros inseridos"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS dados (id INTEGER PRIMARY KEY, conteudo TEXT)")
    
    records_count = 0
    for row in data:
        cursor.execute("INSERT INTO dados (conteudo) VALUES (?)", (str(row),))
        records_count += 1
    
    conn.commit()
    conn.close()
    
    # Log da operação de banco
    logging_service.log_database_operation("INSERT", "dados", records_count)
    
    return records_count

