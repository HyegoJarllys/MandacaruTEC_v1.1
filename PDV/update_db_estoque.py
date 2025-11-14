from db import get_connection

def adicionar_colunas_estoque():
    conn = get_connection()
    cur = conn.cursor()

    # Verificar colunas existentes
    cur.execute("PRAGMA table_info(produtos);")
    colunas = [row[1] for row in cur.fetchall()]  # row[1] é o nome da coluna

    if "estoque" not in colunas:
        cur.execute("ALTER TABLE produtos ADD COLUMN estoque REAL DEFAULT 0;")
        print("Coluna 'estoque' adicionada à tabela produtos.")

    if "estoque_minimo" not in colunas:
        cur.execute("ALTER TABLE produtos ADD COLUMN estoque_minimo REAL DEFAULT 0;")
        print("Coluna 'estoque_minimo' adicionada à tabela produtos.")

    conn.commit()
    conn.close()
    print("Atualização de estrutura de produtos concluída.")


if __name__ == "__main__":
    adicionar_colunas_estoque()
