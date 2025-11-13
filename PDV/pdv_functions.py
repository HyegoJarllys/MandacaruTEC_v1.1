from datetime import datetime
from tkinter import messagebox
from db import get_connection


def buscar_produto_por_codigo(codigo: str):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT nome, preco FROM produtos WHERE codigo_barras = ?;",
        (codigo,),
    )
    row = cur.fetchone()
    conn.close()

    if row:
        return {"nome": row["nome"], "preco": row["preco"]}
    return None


def adicionar_item(lista_itens, item):
    lista_itens.append(item)


def remover_item(lista_itens, index):
    if 0 <= index < len(lista_itens):
        lista_itens.pop(index)


def limpar_carrinho(lista_itens):
    lista_itens.clear()


def calcular_total(lista_itens):
    return round(sum(item["subtotal"] for item in lista_itens), 2)


def salvar_venda_no_banco(resumo):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO vendas (data_hora, total, forma_pagamento, valor_recebido, troco)
        VALUES (?, ?, ?, ?, ?);
        """,
        (
            resumo["data_hora"],
            resumo["total"],
            resumo["forma_pagamento"],
            resumo["valor_recebido"],
            resumo["troco"],
        ),
    )
    venda_id = cur.lastrowid

    for item in resumo["itens"]:
        cur.execute(
            """
            INSERT INTO itens_venda (
                venda_id, codigo_barras, descricao,
                quantidade, preco_unit, subtotal
            )
            VALUES (?, ?, ?, ?, ?, ?);
            """,
            (
                venda_id,
                item["codigo"],
                item["descricao"],
                item["quantidade"],
                item["preco_unit"],
                item["subtotal"],
            ),
        )

    conn.commit()
    conn.close()


def finalizar_venda(lista_itens, forma_pagamento: str, valor_recebido: float):
    if not lista_itens:
        raise ValueError("Nenhum item no carrinho.")

    total = calcular_total(lista_itens)

    if forma_pagamento.lower() == "dinheiro" and valor_recebido < total:
        raise ValueError("Valor recebido em dinheiro é menor que o total da venda.")

    troco = round(valor_recebido - total, 2) if forma_pagamento.lower() == "dinheiro" else 0.0

    resumo = {
        "total": total,
        "forma_pagamento": forma_pagamento,
        "valor_recebido": valor_recebido,
        "troco": troco,
        "data_hora": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        "itens": lista_itens.copy(),
    }

    salvar_venda_no_banco(resumo)

    return resumo


def exibir_resumo_venda(resumo):
    linhas = []
    linhas.append(f"Data/Hora: {resumo['data_hora']}")
    linhas.append("Itens:")

    for item in resumo["itens"]:
        linhas.append(
            f"- {item['descricao']} x {item['quantidade']} = R$ {item['subtotal']:.2f}"
        )

    linhas.append(f"\nTotal: R$ {resumo['total']:.2f}")
    linhas.append(f"Forma de pagamento: {resumo['forma_pagamento']}")

    if resumo["forma_pagamento"].lower() == "dinheiro":
        linhas.append(f"Recebido: R$ {resumo['valor_recebido']:.2f}")
        linhas.append(f"Troco: R$ {resumo['troco']:.2f}")

    mensagem = "\n".join(linhas)
    messagebox.showinfo("Resumo da Venda", mensagem)
