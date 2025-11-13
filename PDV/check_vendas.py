from db import get_connection

def listar_vendas():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM vendas ORDER BY id DESC;")
    vendas = cur.fetchall()

    print("==== VENDAS REGISTRADAS ====\n")
    for v in vendas:
        print(f"ID: {v['id']}")
        print(f"Data/Hora: {v['data_hora']}")
        print(f"Total: R$ {v['total']:.2f}")
        print(f"Forma de pagamento: {v['forma_pagamento']}")
        print(f"Recebido: R$ {v['valor_recebido']:.2f}")
        print(f"Troco: R$ {v['troco']:.2f}")

        # Itens da venda
        cur.execute(
            "SELECT * FROM itens_venda WHERE venda_id = ?;",
            (v["id"],),
        )
        itens = cur.fetchall()
        print("Itens:")
        for item in itens:
            print(
                f"  - {item['descricao']} x {item['quantidade']} "
                f"= R$ {item['subtotal']:.2f}"
            )
        print("-" * 40)

    conn.close()


if __name__ == "__main__":
    listar_vendas()
