import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, "db_portao_esp.db")

def conexao():
    return sqlite3.connect(DATABASE)

def criar_tabela():
    conn = conexao()
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS acessos (
            id SERIAL PRIMARY KEY,
            hora_entrada TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

criar_tabela()