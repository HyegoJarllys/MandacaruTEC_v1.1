from db import get_connection

def atualizar_tabelas_vendas():
    """
    Atualiza o esquema das tabelas 'vendas' e 'itens_venda'
    para o formato usado pelo PDV atual.

    ATENÇÃO: isso APAGA as vendas já registradas nessas tabelas.
    Os produtos, estoque e outras tabelas NÃO são alterados.
    """
    conn = get_connection()
    cur = conn.cursor()

    # Apaga as tabelas antigas (se existirem)
    cur.execute("DROP TABLE IF EXISTS itens_venda;")
    cur.execute("DROP TABLE IF EXISTS vendas;")

    # Recria tabela de vendas
    cur.execute(
        """
        CREATE TABLE vendas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data_hora TEXT NOT NULL,
            total REAL NOT NULL,
            forma_pagamento TEXT,
            valor_recebido REAL,
            troco REAL
        );
        """
    )

    # Recria tabela de itens da venda com custo e lucro
    cur.execute(
        """
        CREATE TABLE itens_venda (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            venda_id INTEGER NOT NULL,
            codigo TEXT NOT NULL,
            descricao TEXT NOT NULL,
            quantidade REAL NOT NULL,
            preco_unit REAL NOT NULL,
            subtotal REAL NOT NULL,
            custo_unit REAL NOT NULL,
            lucro REAL NOT NULL,
            FOREIGN KEY (venda_id) REFERENCES vendas (id)
        );
        """
    )

    conn.commit()
    conn.close()
    print("Tabelas 'vendas' e 'itens_venda' recriadas com sucesso.")

if __name__ == "__main__":
    atualizar_tabelas_vendas()
