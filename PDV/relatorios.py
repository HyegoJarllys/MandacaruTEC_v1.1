import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from db import get_connection


def abrir_relatorio_caixa_dia(parent=None):
    """Abre uma janela com o resumo de caixa do dia atual."""

    # Data de hoje no formato dd/mm/AAAA
    hoje_str = datetime.now().strftime("%d/%m/%Y")

    conn = get_connection()
    cur = conn.cursor()

    # Filtra vendas pela data (primeiros 10 caracteres do campo data_hora)
    cur.execute(
        """
        SELECT id, data_hora, total, forma_pagamento, valor_recebido, troco
        FROM vendas
        WHERE substr(data_hora, 1, 10) = ?
        ORDER BY id DESC;
        """,
        (hoje_str,),
    )
    vendas = cur.fetchall()
    conn.close()

    if not vendas:
        messagebox.showinfo(
            "Relatório de Caixa",
            f"Não há vendas registradas em {hoje_str}."
        )
        return

    # Cálculos de resumo
    total_geral = sum(v["total"] for v in vendas)
    qtd_vendas = len(vendas)
    total_dinheiro = sum(
        v["total"] for v in vendas if v["forma_pagamento"].lower() == "dinheiro"
    )
    total_pix = sum(
        v["total"] for v in vendas if v["forma_pagamento"].lower() == "pix"
    )
    ticket_medio = total_geral / qtd_vendas if qtd_vendas else 0.0

    # Janela do relatório
    if parent is None:
        janela = tk.Toplevel()
    else:
        janela = tk.Toplevel(parent)

    janela.title(f"Relatório de Caixa - {hoje_str}")
    janela.geometry("700x500")
    janela.configure(bg="#f7f7f7")

    titulo = tk.Label(
        janela,
        text=f"Relatório de Caixa - {hoje_str}",
        font=("Arial", 14, "bold"),
        bg="#f7f7f7",
    )
    titulo.pack(pady=10)

    resumo_lbl = tk.Label(
        janela,
        text=(
            f"Total Geral: R$ {total_geral:.2f}   |   "
            f"Vendas: {qtd_vendas}   |   "
            f"Ticket Médio: R$ {ticket_medio:.2f}\n"
            f"Dinheiro: R$ {total_dinheiro:.2f}   |   "
            f"PIX: R$ {total_pix:.2f}"
        ),
        bg="#f7f7f7",
        justify="left",
    )
    resumo_lbl.pack(pady=5)

    # Tabela de vendas
    frame_tab = tk.Frame(janela, bg="#f7f7f7")
    frame_tab.pack(fill="both", expand=True, padx=10, pady=10)

    colunas = ("id", "hora", "forma", "total")
    tree = ttk.Treeview(frame_tab, columns=colunas, show="headings", height=15)
    tree.heading("id", text="ID")
    tree.heading("hora", text="Hora")
    tree.heading("forma", text="Forma Pagto")
    tree.heading("total", text="Total (R$)")

    tree.column("id", width=50, anchor="center")
    tree.column("hora", width=120, anchor="center")
    tree.column("forma", width=150, anchor="center")
    tree.column("total", width=120, anchor="e")

    tree.pack(side="left", fill="both", expand=True)

    scrollbar = ttk.Scrollbar(frame_tab, orient="vertical", command=tree.yview)
    scrollbar.pack(side="right", fill="y")
    tree.configure(yscrollcommand=scrollbar.set)

    for v in vendas:
        hora = v["data_hora"][11:]  # pega só HH:MM:SS
        tree.insert(
            "",
            "end",
            values=(
                v["id"],
                hora,
                v["forma_pagamento"],
                f"{v['total']:.2f}",
            ),
        )

    btn_fechar = tk.Button(janela, text="Fechar", command=janela.destroy)
    btn_fechar.pack(pady=5)


if __name__ == "__main__":
    abrir_relatorio_caixa_dia()

