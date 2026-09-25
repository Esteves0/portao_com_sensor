import psycopg2
from dotenv import *


load_dotenv()
DATABASE_URL = 'postgresql://neondb_owner:npg_iMKY63TDqvdU@ep-lingering-resonance-b4ldlx0x-pooler.c-6.us-east-2.aws.neon.tech/neondb?sslmode=require&channel_binding=require'
DB_HOST = "localhost"
DB_NAME = "db_portao_esp"
DB_USER = "postgres"
DB_PASSWORD = "1234"
DB_PORT = 5432

def conexao():
    if not DATABASE_URL:
        raise Exception("Database não encontrado")
    conn = psycopg2.connect(DATABASE_URL)
    return conn
