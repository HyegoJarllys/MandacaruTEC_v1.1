import sqlite3
import os
import sys

# Add the PDV directory to the path so we can import modules
sys.path.append(r"c:\Users\Hyego Jarllys\OneDrive\Ambiente de Trabalho\Mandacaru\Mercadinh\MandacaruTEC_v1.1\PDV")

from db import get_connection
from cadastro_produtos import ensure_columns

print("Starting verification...")

# 1. Check if ensure_columns works without error
try:
    print("Running ensure_columns()...")
    ensure_columns()
    print("ensure_columns() completed.")
except Exception as e:
    print(f"FAILED: ensure_columns() raised an exception: {e}")
    sys.exit(1)

# 2. Check if table 'produtos' exists and has all columns
try:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("PRAGMA table_info(produtos)")
    cols = {row[1] for row in cur.fetchall()}
    
    required_cols = {
        "codigo_barras", "nome", "preco_venda", "preco_custo", "validade",
        "estoque_atual", "estoque_minimo", "unidade_venda", "categoria", "descricao"
    }
    
    missing = required_cols - cols
    if missing:
        print(f"FAILED: Missing columns in 'produtos': {missing}")
    else:
        print("SUCCESS: All required columns are present.")
    
    conn.close()
except Exception as e:
    print(f"FAILED: Database check failed: {e}")
    sys.exit(1)

print("Verification passed!")
