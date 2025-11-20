# update_db_estrutura_produtos.py
from db import get_connection

def garantir_colunas_produtos():
    conn = get_connection()
    cur = conn.cursor()

    # Ver estrutura atual da tabela produtos
    cur.execute("PRAGMA table_info(produtos);")
    cols = {row[1] for row in cur.fetchall()}

    def add_col(nome, tipo, default=None):
        if nome not in cols:
            sql = f"ALTER TABLE produtos ADD COLUMN {nome} {tipo}"
            if default is not None:
                sql += f" DEFAULT {default}"
            print(">>", sql)
            cur.execute(sql)

    # Colunas novas
    add_col("preco_venda", "REAL", 0)
    add_col("preco_custo", "REAL", 0)
    add_col("validade", "TEXT")
    add_col("estoque_atual", "INTEGER", 0)
    add_col("estoque_minimo", "INTEGER", 0)
    add_col("unidade_venda", "TEXT")
    add_col("descricao", "TEXT")
    add_col("categoria_id", "INTEGER")

    conn.commit()
    conn.close()
    print("Estrutura da tabela produtos conferida/atualizada.")

def garantir_tabela_categorias():
    conn = get_connection()
    cur = conn.cursor()

    # Ver se já existe tabela categorias
    cur.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name='categorias';
    """)
    row = cur.fetchone()
    if not row:
        print(">> CREATE TABLE categorias ...")
        cur.execute("""
            CREATE TABLE categorias (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL UNIQUE,
                cor_tag TEXT
            );
        """)
        # categorias exemplo
        cur.executemany(
            "INSERT INTO categorias (nome, cor_tag) VALUES (?, ?);",
            [
                ("Geral", "#4B7BFF"),
                ("Alimentos", "#4CAF50"),
                ("Bebidas", "#FFC938"),
                ("Limpeza", "#FF4B4B"),
            ],
        )
        conn.commit()

    conn.close()
    print("Tabela categorias conferida/atualizada.")

if __name__ == "__main__":
    garantir_colunas_produtos()
    garantir_tabela_categorias()
    print("OK! Agora pode abrir o PDV e o cadastro de produtos.")
