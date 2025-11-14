from db import get_connection

def atualizar_estrutura():
    conn = get_connection()
    cur = conn.cursor()

    # --- PRODUTOS: preco_custo ---
    cur.execute("PRAGMA table_info(produtos);")
    colunas_prod = [row[1] for row in cur.fetchall()]

    if "preco_custo" not in colunas_prod:
        cur.execute(
            "ALTER TABLE produtos ADD COLUMN preco_custo REAL DEFAULT 0;"
        )
        print("Coluna 'preco_custo' adicionada à tabela produtos.")

    # --- VENDAS: lucro_total ---
    cur.execute("PRAGMA table_info(vendas);")
    colunas_vendas = [row[1] for row in cur.fetchall()]

    if "lucro_total" not in colunas_vendas:
        cur.execute(
            "ALTER TABLE vendas ADD COLUMN lucro_total REAL DEFAULT 0;"
        )
        print("Coluna 'lucro_total' adicionada à tabela vendas.")

    # --- ITENS_VENDA: custo_unit e lucro_item ---
    cur.execute("PRAGMA table_info(itens_venda);")
    colunas_itens = [row[1] for row in cur.fetchall()]

    if "custo_unit" not in colunas_itens:
        cur.execute(
            "ALTER TABLE itens_venda ADD COLUMN custo_unit REAL DEFAULT 0;"
        )
        print("Coluna 'custo_unit' adicionada à tabela itens_venda.")

    if "lucro_item" not in colunas_itens:
        cur.execute(
            "ALTER TABLE itens_venda ADD COLUMN lucro_item REAL DEFAULT 0;"
        )
        print("Coluna 'lucro_item' adicionada à tabela itens_venda.")

    conn.commit()
    conn.close()
    print("Atualização de estrutura concluída.")


if __name__ == "__main__":
    atualizar_estrutura()
