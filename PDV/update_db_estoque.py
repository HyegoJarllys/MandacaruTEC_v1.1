# update_db_estoque.py
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "mandacarutec.db")


def ensure_columns():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Pega colunas atuais da tabela produtos
    cur.execute("PRAGMA table_info(produtos)")
    cols = {row[1] for row in cur.fetchall()}

    def add_column(name, type_sql, default=None):
        if name not in cols:
            sql = f"ALTER TABLE produtos ADD COLUMN {name} {type_sql}"
            if default is not None:
                sql += f" DEFAULT {default}"
            cur.execute(sql)

    # Garante todas as colunas novas
    add_column("preco_venda", "REAL", 0)
    add_column("preco_custo", "REAL", 0)
    add_column("validade", "TEXT", "'0000-00-00'")
    add_column("estoque_atual", "INTEGER", 0)
    add_column("estoque_minimo", "INTEGER", 0)
    add_column("unidade_venda", "TEXT", "'UNIDADE'")
    add_column("categoria", "TEXT", "''")
    add_column("descricao", "TEXT", "''")

    # Tabela de categorias
    cur.execute("""
        CREATE TABLE IF NOT EXISTS categorias (
            id   INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL UNIQUE
        );
    """)

    conn.commit()
    conn.close()


if __name__ == "__main__":
    ensure_columns()
    print("OK! Colunas e tabela de categorias garantidas.")
