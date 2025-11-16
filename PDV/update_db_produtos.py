from db import get_connection

def atualizar_tabela_produtos():
    """
    Garante que a tabela 'produtos' tenha as colunas:
      - estoque REAL
      - custo REAL
      - validade TEXT
    sem apagar nada do que já existe.
    """
    conn = get_connection()
    cur = conn.cursor()

    # Garante existência da tabela (se for um banco muito novo)
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS produtos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo_barras TEXT UNIQUE,
            nome TEXT,
            preco REAL DEFAULT 0
        );
        """
    )

    # Descobre as colunas atuais
    cur.execute("PRAGMA table_info(produtos);")
    cols = {row[1] for row in cur.fetchall()}

    if "estoque" not in cols:
        cur.execute("ALTER TABLE produtos ADD COLUMN estoque REAL DEFAULT 0;")

    if "custo" not in cols:
        cur.execute("ALTER TABLE produtos ADD COLUMN custo REAL DEFAULT 0;")

    if "validade" not in cols:
        cur.execute("ALTER TABLE produtos ADD COLUMN validade TEXT;")

    conn.commit()
    conn.close()
    print("Tabela 'produtos' atualizada com estoque, custo e validade.")

if __name__ == "__main__":
    atualizar_tabela_produtos()
