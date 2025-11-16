from datetime import datetime
from tkinter import messagebox
from db import get_connection  # usa mesma conexão do resto do sistema


# =====================================================================
# CONEXÃO
# =====================================================================
def _get_conn():
    """Abre conexão usando o db.py do projeto."""
    return get_connection()


# =====================================================================
# PRODUTOS
# =====================================================================
def buscar_produto_por_codigo(codigo_barras: str):
    """
    Busca produto no banco pelo código de barras.

    Tenta buscar também o custo unitário (coluna 'custo' em produtos).
    Se a coluna não existir, assume custo 0.0.
    """
    conn = _get_conn()
    cur = conn.cursor()

    row = None

    # Primeiro tenta com coluna 'custo'
    try:
        cur.execute(
            "SELECT id, codigo_barras, nome, preco, custo FROM produtos WHERE codigo_barras = ?;",
            (codigo_barras,),
        )
        row = cur.fetchone()
    except Exception:
        # Se der erro (ex.: não existe coluna custo), tenta sem custo
        try:
            cur.execute(
                "SELECT id, codigo_barras, nome, preco FROM produtos WHERE codigo_barras = ?;",
                (codigo_barras,),
            )
            row2 = cur.fetchone()
            if row2:
                # monta tupla como se tivesse custo = 0
                row = (row2[0], row2[1], row2[2], row2[3], 0.0)
        except Exception:
            row = None

    conn.close()

    if not row:
        return None

    # row = (id, codigo_barras, nome, preco, custo)
    return {
        "id": row[0],
        "codigo": row[1],          # usado no PDV
        "codigo_barras": row[1],
        "descricao": row[2],       # nome do produto
        "nome": row[2],
        "preco": float(row[3]),
        "custo": float(row[4]) if row[4] is not None else 0.0,
    }


# =====================================================================
# ITENS DO CARRINHO (USADO PELO PDV)
# =====================================================================
def adicionar_item(lista_itens: list, codigo_barras: str, quantidade: int = 1):
    """
    Adiciona um item à lista de itens da venda.

    Cada item da lista:
        {
            "codigo": str,
            "descricao": str,
            "quantidade": int,
            "preco_unit": float,
            "custo_unit": float,
            "subtotal": float
        }

    Retorno:
        {"erro": None} em sucesso
        {"erro": "mensagem"} em erro
    """
    if quantidade <= 0:
        return {"erro": "Quantidade deve ser maior que zero."}

    produto = buscar_produto_por_codigo(codigo_barras)
    if not produto:
        return {"erro": f"Produto com código '{codigo_barras}' não encontrado."}

    preco = produto["preco"]
    custo = produto.get("custo", 0.0)
    descricao = produto["descricao"]

    subtotal = preco * quantidade

    item = {
        "codigo": produto["codigo"],
        "descricao": descricao,
        "quantidade": quantidade,
        "preco_unit": preco,
        "custo_unit": custo,
        "subtotal": subtotal,
    }

    lista_itens.append(item)
    return {"erro": None}


def remover_item(lista_itens: list, indice: int):
    """Remove o item da lista pelo índice, se existir."""
    if 0 <= indice < len(lista_itens):
        lista_itens.pop(indice)


def calcular_total(lista_itens: list) -> float:
    """Retorna o total da venda somando os subtotais."""
    return sum(float(item.get("subtotal", 0)) for item in lista_itens)


# =====================================================================
# VENDAS NO BANCO
# =====================================================================
def _garantir_tabelas_venda(cur):
    """Cria as tabelas de venda no banco, se ainda não existirem."""
    # Tabela de vendas
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS vendas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data_hora TEXT NOT NULL,
            total REAL NOT NULL,
            forma_pagamento TEXT,
            valor_recebido REAL,
            troco REAL
        );
        """
    )

    # Itens da venda (já com custo e lucro)
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS itens_venda (
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


def finalizar_venda(
    lista_itens: list,
    forma_pagamento: str = None,
    valor_recebido: float = None,
) -> dict:
    """
    Finaliza a venda:
      - Valida itens
      - Calcula total e troco (se tiver valor_recebido)
      - Salva em 'vendas' e 'itens_venda'
      - Calcula e salva o lucro de cada item
      - Retorna resumo para o PDV (sem lucro na tela do PDV).

    Retorno:
      {
        "erro": None ou "mensagem de erro",
        "id_venda": int ou None,
        "data_hora": str,
        "total": float,
        "itens": [...],
        "qtd_itens": int,
        "forma_pagamento": str,
        "valor_recebido": float ou None,
        "troco": float ou None,
        "erro_bd": str ou None
      }
    """
    if not lista_itens:
        return {"erro": "Não há itens na venda."}

    total = calcular_total(lista_itens)
    data_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    troco = None
    if valor_recebido is not None:
        try:
            troco = float(valor_recebido) - total
        except Exception:
            troco = None

    venda_id = None
    erro_bd = None

    # Registrar no banco
    try:
        conn = _get_conn()
        cur = conn.cursor()

        _garantir_tabelas_venda(cur)

        cur.execute(
            """
            INSERT INTO vendas
                (data_hora, total, forma_pagamento, valor_recebido, troco)
            VALUES (?, ?, ?, ?, ?);
            """,
            (data_hora, total, forma_pagamento, valor_recebido, troco),
        )
        venda_id = cur.lastrowid

        for item in lista_itens:
            qtd = float(item["quantidade"])
            preco_unit = float(item["preco_unit"])
            custo_unit = float(item.get("custo_unit", 0.0))
            subtotal = float(item["subtotal"])
            lucro_item = subtotal - (custo_unit * qtd)

            cur.execute(
                """
                INSERT INTO itens_venda
                    (venda_id, codigo, descricao, quantidade,
                     preco_unit, subtotal, custo_unit, lucro)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?);
                """,
                (
                    venda_id,
                    item["codigo"],
                    item["descricao"],
                    qtd,
                    preco_unit,
                    subtotal,
                    custo_unit,
                    lucro_item,
                ),
            )

        conn.commit()
        conn.close()

    except Exception as e:
        erro_bd = str(e)

    resumo = {
        "erro": None,
        "id_venda": venda_id,
        "data_hora": data_hora,
        "total": total,
        "itens": list(lista_itens),  # cópia
        "qtd_itens": sum(int(i["quantidade"]) for i in lista_itens),
        "forma_pagamento": forma_pagamento,
        "valor_recebido": valor_recebido,
        "troco": troco,
        "erro_bd": erro_bd,
    }

    return resumo


# =====================================================================
# EXIBIÇÃO DO RESUMO (SEM LUCRO)
# =====================================================================
def exibir_resumo_venda(resumo: dict):
    """
    Mostra um resumo simples da venda em uma caixa de diálogo.
    Não mostra lucro (apenas itens, total e forma de pagamento).
    """
    if resumo.get("erro"):
        messagebox.showerror("Erro na venda", resumo["erro"])
        return

    linhas = []
    linhas.append(f"Venda Nº: {resumo.get('id_venda', '-')}")
    linhas.append(f"Data/Hora: {resumo.get('data_hora', '-')}")
    if resumo.get("forma_pagamento"):
        linhas.append(f"Pagamento: {resumo['forma_pagamento']}")

    if resumo.get("valor_recebido") not in (None, 0):
        linhas.append(f"Valor Recebido: R$ {resumo['valor_recebido']:.2f}")
    if resumo.get("troco") is not None:
        linhas.append(f"Troco: R$ {resumo['troco']:.2f}")

    linhas.append("-" * 40)

    for item in resumo.get("itens", []):
        linhas.append(
            f"{item['descricao']}\n"
            f"  Qtd: {item['quantidade']:.0f}  "
            f"Unit: R$ {item['preco_unit']:.2f}  "
            f"Sub: R$ {item['subtotal']:.2f}"
        )

    linhas.append("-" * 40)
    linhas.append(f"TOTAL: R$ {resumo.get('total', 0):.2f}")

    if resumo.get("erro_bd"):
        linhas.append("")
        linhas.append("Obs.: Erro ao registrar no banco:")
        linhas.append(resumo["erro_bd"])

    mensagem = "\n".join(linhas)
    messagebox.showinfo("Resumo da Venda", mensagem)
