import sqlite3
import os

# Caminho do arquivo do banco dentro da pasta PDV
DB_PATH = os.path.join(os.path.dirname(__file__), "mandacarutec.db")


def get_connection():
    """Retorna uma conexão com o banco SQLite."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # permite acessar colunas por nome
    return conn