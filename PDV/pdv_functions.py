from datetime import datetime
from tkinter import messagebox
from db import get_connection


def buscar_produto_por_codigo(codigo: str):
    """
    Busca o produto no banco pelo código de barras.
    Retorna dict com nome, preço de venda, estoque e custo.
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT nome, preco, preco_custo, estoque
        FROM produtos
        WHERE codigo_barras = ?
        ORDER BY id DESC
        LIMIT 1;
        """,
        (codigo,),
    )
    row = cur.fetchone()
    conn.close()

    if row:
        return {
            "nome": row["nome"],
            "preco": row["preco"],                     # preço de venda
            "custo": row["preco_custo"] or 0.0,       # custo (0.0 se vier None)
            "estoque": row["estoque"] if row["estoque"] is not None else None,
        }
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
    """
    Salva a venda (cabeçalho e itens) no banco de dados
    e atualiza o estoque dos produtos.
    """
    conn = get_connection()
    cur = conn.cursor()

    # Cabeçalho da venda
    cur.execute(
        """
        INSERT INTO vendas (data_hora, total, forma_pagamento, valor_recebido, troco, lucro_total)
        VALUES (?, ?, ?, ?, ?, ?);
        """,
        (
            resumo["data_hora"],
            resumo["total"],
            resumo["forma_pagamento"],
            resumo["valor_recebido"],
            resumo["troco"],
            resumo["lucro_total"],
        ),
    )
    venda_id = cur.lastrowid

    # Itens da venda
    for item in resumo["itens"]:
        custo_unit = item.get("custo_unit", 0.0)
        lucro_item = item["subtotal"] - (custo_unit * item["quantidade"])

        cur.execute(
            """
            INSERT INTO itens_venda (
                venda_id, codigo_barras, descricao,
                quantidade, preco_unit, subtotal,
                custo_unit, lucro_item
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?);
            """,
            (
                venda_id,
                item["codigo"],
                item["descricao"],
                item["quantidade"],
                item["preco_unit"],
                item["subtotal"],
                custo_unit,
                lucro_item,
            ),
        )

        # Atualiza estoque (não deixa negativo)
        cur.execute(
            """
            UPDATE produtos
            SET estoque = MAX(estoque - ?, 0)
            WHERE codigo_barras = ?;
            """,
            (item["quantidade"], item["codigo"]),
        )

    conn.commit()
    conn.close()


def finalizar_venda(lista_itens, forma_pagamento: str, valor_recebido: float):
    """
    Finaliza a venda, calcula troco, lucro total, salva no banco e retorna o resumo.
    """
    if not lista_itens:
        raise ValueError("Nenhum item no carrinho.")

    total = calcular_total(lista_itens)

    if forma_pagamento.lower() == "dinheiro" and valor_recebido < total:
        raise ValueError("Valor recebido em dinheiro é menor que o total da venda.")

    troco = round(valor_recebido - total, 2) if forma_pagamento.lower() == "dinheiro" else 0.0

    # Calcula lucro total da venda
    lucro_total = 0.0
    for item in lista_itens:
        custo_unit = item.get("custo_unit", 0.0)
        lucro_total += item["subtotal"] - (custo_unit * item["quantidade"])
    lucro_total = round(lucro_total, 2)

    resumo = {
        "total": total,
        "forma_pagamento": forma_pagamento,
        "valor_recebido": valor_recebido,
        "troco": troco,
        "data_hora": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        "itens": lista_itens.copy(),
        "lucro_total": lucro_total,
    }

    # Salva no banco e atualiza estoque
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
        linhas.append(f"Troco: {resumo['troco']:.2f}")

    linhas.append(f"\nLucro total da venda: R$ {resumo['lucro_total']:.2f}")
    if resumo["total"] > 0:
        margem = (resumo["lucro_total"] / resumo["total"]) * 100
        linhas.append(f"Margem bruta: {margem:.1f}%")

    mensagem = "\n".join(linhas)
    messagebox.showinfo("Resumo da Venda", mensagem)
