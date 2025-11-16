import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date

from db import get_connection


# ============================================================
# BUSCAS NO BANCO
# ============================================================
def _get_conn():
    return get_connection()


def buscar_vendas_no_dia(data_ref: date):
    """
    Retorna lista de vendas no dia informado.

    Cada item:
      {
        "id": int,
        "data_hora": str,
        "hora": "HH:MM",
        "total": float,
        "forma_pagamento": str ou None
      }
    """
    data_iso = data_ref.strftime("%Y-%m-%d")

    conn = _get_conn()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT id, data_hora, total, forma_pagamento
        FROM vendas
        WHERE substr(data_hora, 1, 10) = ?
        ORDER BY data_hora ASC;
        """,
        (data_iso,),
    )

    rows = cur.fetchall()
    conn.close()

    vendas = []
    for row in rows:
        vid, dh, total, fpag = row
        hora = dh[11:16] if dh and len(dh) >= 16 else "--:--"
        vendas.append(
            {
                "id": vid,
                "data_hora": dh,
                "hora": hora,
                "total": float(total),
                "forma_pagamento": (fpag or "").upper() if fpag else "OUTROS",
            }
        )
    return vendas


def buscar_itens_da_venda(venda_id: int):
    """
    Retorna itens da venda:
      {
        "codigo": str,
        "descricao": str,
        "quantidade": float,
        "preco_unit": float,
        "subtotal": float,
        "custo_unit": float,
        "lucro": float
      }
    """
    conn = _get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT codigo, descricao, quantidade, preco_unit, subtotal,
               custo_unit, lucro
        FROM itens_venda
        WHERE venda_id = ?
        ORDER BY id ASC;
        """,
        (venda_id,),
    )
    rows = cur.fetchall()
    conn.close()

    itens = []
    for row in rows:
        itens.append(
            {
                "codigo": row[0],
                "descricao": row[1],
                "quantidade": float(row[2]),
                "preco_unit": float(row[3]),
                "subtotal": float(row[4]),
                "custo_unit": float(row[5]),
                "lucro": float(row[6]),
            }
        )
    return itens


# ============================================================
# JANELA DE RELATÓRIO DE CAIXA DO DIA
# ============================================================
def abrir_relatorio_caixa_dia(parent=None):
    """
    Abre uma janela com o relatório de caixa do dia:
      - Lista de vendas do dia
      - Resumo total (por forma de pagamento)
      - Lucro bruto e líquido do dia
      - Itens da venda selecionada
    """
    jan = tk.Toplevel(parent) if parent is not None else tk.Tk()
    jan.title("Relatório de Caixa - Dia")
    jan.geometry("950x600")
    jan.configure(bg="#f7f7f7")

    # ================== TOPO: DATA E BOTÃO CARREGAR ==================
    frame_top = tk.Frame(jan, bg="#f7f7f7")
    frame_top.pack(fill="x", padx=10, pady=10)

    tk.Label(frame_top, text="Data (dd/mm/aaaa):", bg="#f7f7f7").pack(side="left")

    entry_data = tk.Entry(frame_top, width=12)
    entry_data.pack(side="left", padx=5)

    hoje = date.today()
    entry_data.insert(0, hoje.strftime("%d/%m/%Y"))

    def parse_data_entry():
        txt = entry_data.get().strip()
        if not txt:
            return hoje
        try:
            d, m, a = txt.split("/")
            return date(int(a), int(m), int(d))
        except Exception:
            messagebox.showerror("Erro", "Data inválida. Use o formato dd/mm/aaaa.")
            return None

    # ================== FRAME PRINCIPAL ==================
    frame_main = tk.Frame(jan, bg="#f7f7f7")
    frame_main.pack(fill="both", expand=True, padx=10, pady=5)

    # ---------- LADO ESQUERDO: VENDAS ----------
    frame_vendas = tk.Frame(frame_main, bg="#f7f7f7")
    frame_vendas.pack(side="left", fill="both", expand=True, padx=(0, 5))

    tk.Label(
        frame_vendas,
        text="Vendas do Dia",
        bg="#f7f7f7",
        font=("Arial", 10, "bold"),
    ).pack(anchor="w")

    cols_v = ("id", "hora", "forma", "total")
    tree_vendas = ttk.Treeview(frame_vendas, columns=cols_v, show="headings", height=10)
    tree_vendas.pack(fill="both", expand=True, pady=5)

    tree_vendas.heading("id", text="Venda")
    tree_vendas.heading("hora", text="Hora")
    tree_vendas.heading("forma", text="Forma Pagto")
    tree_vendas.heading("total", text="Total")

    tree_vendas.column("id", width=60, anchor="center")
    tree_vendas.column("hora", width=60, anchor="center")
    tree_vendas.column("forma", width=120, anchor="center")
    tree_vendas.column("total", width=100, anchor="e")

    scroll_v = ttk.Scrollbar(frame_vendas, orient="vertical", command=tree_vendas.yview)
    tree_vendas.configure(yscroll=scroll_v.set)
    scroll_v.pack(side="right", fill="y")

    # ---------- RESUMO DO DIA ----------
    frame_resumo = tk.Frame(frame_vendas, bg="#f7f7f7")
    frame_resumo.pack(fill="x", pady=5)

    lbl_total_dia = tk.Label(frame_resumo, text="Total do dia: R$ 0,00", bg="#f7f7f7")
    lbl_total_dia.pack(anchor="w")

    lbl_total_din = tk.Label(frame_resumo, text="Total DINHEIRO: R$ 0,00", bg="#f7f7f7")
    lbl_total_din.pack(anchor="w")

    lbl_total_pix = tk.Label(frame_resumo, text="Total PIX: R$ 0,00", bg="#f7f7f7")
    lbl_total_pix.pack(anchor="w")

    lbl_total_cart = tk.Label(frame_resumo, text="Total CARTÃO: R$ 0,00", bg="#f7f7f7")
    lbl_total_cart.pack(anchor="w")

    lbl_qtd_vendas = tk.Label(frame_resumo, text="Qtd vendas: 0", bg="#f7f7f7")
    lbl_qtd_vendas.pack(anchor="w")

    lbl_ticket = tk.Label(frame_resumo, text="Ticket médio: R$ 0,00", bg="#f7f7f7")
    lbl_ticket.pack(anchor="w")

    lbl_lucro_bruto = tk.Label(frame_resumo, text="Lucro BRUTO: R$ 0,00", bg="#f7f7f7")
    lbl_lucro_bruto.pack(anchor="w")

    lbl_lucro_liq = tk.Label(frame_resumo, text="Lucro LÍQUIDO: R$ 0,00", bg="#f7f7f7")
    lbl_lucro_liq.pack(anchor="w")

    # ---------- LADO DIREITO: ITENS DA VENDA ----------
    frame_itens = tk.Frame(frame_main, bg="#f7f7f7")
    frame_itens.pack(side="right", fill="both", expand=True, padx=(5, 0))

    tk.Label(
        frame_itens,
        text="Itens da Venda Selecionada",
        bg="#f7f7f7",
        font=("Arial", 10, "bold"),
    ).pack(anchor="w")

    cols_i = ("codigo", "descricao", "qtd", "unit", "sub")
    tree_itens = ttk.Treeview(frame_itens, columns=cols_i, show="headings", height=10)
    tree_itens.pack(fill="both", expand=True, pady=5)

    tree_itens.heading("codigo", text="Código")
    tree_itens.heading("descricao", text="Descrição")
    tree_itens.heading("qtd", text="Qtd")
    tree_itens.heading("unit", text="Unitário")
    tree_itens.heading("sub", text="Subtotal")

    tree_itens.column("codigo", width=80)
    tree_itens.column("descricao", width=220)
    tree_itens.column("qtd", width=60, anchor="e")
    tree_itens.column("unit", width=80, anchor="e")
    tree_itens.column("sub", width=80, anchor="e")

    scroll_i = ttk.Scrollbar(frame_itens, orient="vertical", command=tree_itens.yview)
    tree_itens.configure(yscroll=scroll_i.set)
    scroll_i.pack(side="right", fill="y")

    # ================== FUNÇÕES INTERNAS ==================
    vendas_cache = []

    def fmt(valor):
        return f"R$ {valor:.2f}".replace(".", ",")

    def carregar_vendas_para_data(data_ref: date):
        nonlocal vendas_cache
        for item in tree_vendas.get_children():
            tree_vendas.delete(item)
        for item in tree_itens.get_children():
            tree_itens.delete(item)

        vendas_cache = buscar_vendas_no_dia(data_ref)

        total_dia = 0.0
        total_din = 0.0
        total_pix = 0.0
        total_cart = 0.0
        lucro_bruto_dia = 0.0

        for v in vendas_cache:
            tree_vendas.insert(
                "",
                "end",
                iid=str(v["id"]),
                values=(
                    v["id"],
                    v["hora"],
                    v["forma_pagamento"],
                    fmt(v["total"]),
                ),
            )

            total_dia += v["total"]
            fp = v["forma_pagamento"]
            if fp == "DINHEIRO":
                total_din += v["total"]
            elif fp == "PIX":
                total_pix += v["total"]
            elif fp in ("CARTÃO", "CARTAO"):
                total_cart += v["total"]

            # Calcula lucro da venda somando lucros dos itens
            itens = buscar_itens_da_venda(v["id"])
            lucro_venda = sum(it.get("lucro", 0.0) for it in itens)
            lucro_bruto_dia += lucro_venda

        qtd_vendas = len(vendas_cache)
        ticket_medio = total_dia / qtd_vendas if qtd_vendas > 0 else 0.0
        lucro_liquido_dia = lucro_bruto_dia  # por enquanto igual (sem despesas gerais)

        lbl_total_dia.config(text=f"Total do dia: {fmt(total_dia)}")
        lbl_total_din.config(text=f"Total DINHEIRO: {fmt(total_din)}")
        lbl_total_pix.config(text=f"Total PIX: {fmt(total_pix)}")
        lbl_total_cart.config(text=f"Total CARTÃO: {fmt(total_cart)}")
        lbl_qtd_vendas.config(text=f"Qtd vendas: {qtd_vendas}")
        lbl_ticket.config(text=f"Ticket médio: {fmt(ticket_medio)}")
        lbl_lucro_bruto.config(text=f"Lucro BRUTO: {fmt(lucro_bruto_dia)}")
        lbl_lucro_liq.config(text=f"Lucro LÍQUIDO: {fmt(lucro_liquido_dia)}")

    def on_selecionar_venda(event=None):
        sel = tree_vendas.selection()
        if not sel:
            return
        venda_id = int(sel[0])

        for item in tree_itens.get_children():
            tree_itens.delete(item)

        itens = buscar_itens_da_venda(venda_id)
        for it in itens:
            tree_itens.insert(
                "",
                "end",
                values=(
                    it["codigo"],
                    it["descricao"],
                    f"{it['quantidade']:.0f}",
                    fmt(it["preco_unit"]),
                    fmt(it["subtotal"]),
                ),
            )

    tree_vendas.bind("<<TreeviewSelect>>", on_selecionar_venda)

    def on_carregar():
        data_ref = parse_data_entry()
        if data_ref is None:
            return
        carregar_vendas_para_data(data_ref)

    tk.Button(
        frame_top,
        text="Carregar",
        command=on_carregar,
        bg="#2196F3",
        fg="white",
    ).pack(side="left", padx=10)

    # Carrega o dia de hoje ao abrir
    carregar_vendas_para_data(hoje)

    if parent is None:
        jan.mainloop()
