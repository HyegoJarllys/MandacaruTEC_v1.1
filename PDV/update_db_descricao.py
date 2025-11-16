from db import get_connection

def atualizar_estrutura_descricao():
    conn = get_connection()
    cur = conn.cursor()

    # Verifica colunas da tabela produtos
    cur.execute("PRAGMA table_info(produtos);")
    colunas = [row[1] for row in cur.fetchall()]

    if "descricao" not in colunas:
        cur.execute("ALTER TABLE produtos ADD COLUMN descricao TEXT;")
        print("Coluna 'descricao' adicionada à tabela produtos.")

    conn.commit()
    conn.close()
    print("Atualização de estrutura (descricao) concluída.")


if __name__ == "__main__":
    atualizar_estrutura_descricao()
