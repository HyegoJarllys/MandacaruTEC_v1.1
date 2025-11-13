import tkinter as tk
from tkinter import ttk, messagebox
from db import get_connection


def buscar_produto_por_codigo(codigo_barras):
    """Busca 1 produto no banco pelo código de barras."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT id, codigo_barras, nome, preco FROM produtos WHERE codigo_barras = ?;",
        (codigo_barras,),
    )
    row = cur.fetchone()
    conn.close()
    return row


def abrir_etiquetas(parent=None):
    """
    Tela de geração de etiquetas.
    - Fundo amarelo, texto preto, 'OFERTA' em vermelho.
    - Sem logo, sem QRCode.
    """

    if parent is None:
        janela = tk.Toplevel()
    else:
        janela = tk.Toplevel(parent)

    janela.title("Mandacaru TEC - Etiquetas")
    janela.geometry("900x600")
    janela.configure(bg="#f7f7f7")

    # ====== FRAME DE CONTROLE (ESQUERDA) ======
    frame_left = tk.Frame(janela, bg="#f7f7f7")
    frame_left.pack(side="left", fill="y", padx=10, pady=10)

    # Código de Barras
    tk.Label(frame_left, text="Código de Barras:", bg="#f7f7f7").grid(
        row=0, column=0, sticky="w"
    )
    entry_codigo = tk.Entry(frame_left, width=25)
    entry_codigo.grid(row=0, column=1, padx=5, pady=5)

    def on_buscar():
        codigo = entry_codigo.get().strip()
        if not codigo:
            messagebox.showwarning("Aviso", "Digite um código de barras.")
            return
        prod = buscar_produto_por_codigo(codigo)
        if not prod:
            messagebox.showerror("Erro", "Produto não encontrado.")
            return
        entry_nome.delete(0, tk.END)
        entry_nome.insert(0, prod["nome"])
        entry_preco.delete(0, tk.END)
        entry_preco.insert(0, f"{prod['preco']:.2f}")

    btn_buscar = tk.Button(frame_left, text="Buscar", command=on_buscar)
    btn_buscar.grid(row=0, column=2, padx=5, pady=5)

    # Nome do produto
    tk.Label(frame_left, text="Nome do Produto:", bg="#f7f7f7").grid(
        row=1, column=0, sticky="w"
    )
    entry_nome = tk.Entry(frame_left, width=40)
    entry_nome.grid(row=1, column=1, columnspan=2, padx=5, pady=5, sticky="w")

    # Preço principal (normal ou oferta)
    tk.Label(frame_left, text="Preço (R$):", bg="#f7f7f7").grid(
        row=2, column=0, sticky="w"
    )
    entry_preco = tk.Entry(frame_left, width=15)
    entry_preco.grid(row=2, column=1, padx=5, pady=5, sticky="w")

    # Checkbox de oferta
    var_oferta = tk.BooleanVar(value=False)
    chk_oferta = tk.Checkbutton(
        frame_left,
        text="Etiqueta de OFERTA",
        bg="#f7f7f7",
        variable=var_oferta,
    )
    chk_oferta.grid(row=3, column=0, columnspan=2, sticky="w", pady=5)

    # Quantidade de etiquetas
    tk.Label(frame_left, text="Qtd de Etiquetas:", bg="#f7f7f7").grid(
        row=4, column=0, sticky="w"
    )
    entry_qtd = tk.Entry(frame_left, width=10)
    entry_qtd.insert(0, "1")
    entry_qtd.grid(row=4, column=1, padx=5, pady=5, sticky="w")

    # Lista de etiquetas configuradas (tabela)
    tk.Label(frame_left, text="Etiquetas na Fila:", bg="#f7f7f7", font=("Arial", 10, "bold")).grid(
        row=5, column=0, columnspan=3, sticky="w", pady=(15, 5)
    )

    tree_cols = ("produto", "preco", "oferta", "qtd")
    tree_etq = ttk.Treeview(frame_left, columns=tree_cols, show="headings", height=8)
    tree_etq.heading("produto", text="Produto")
    tree_etq.heading("preco", text="Preço")
    tree_etq.heading("oferta", text="OFERTA")
    tree_etq.heading("qtd", text="Qtd")

    tree_etq.column("produto", width=220)
    tree_etq.column("preco", width=80)
    tree_etq.column("oferta", width=60, anchor="center")
    tree_etq.column("qtd", width=40, anchor="center")

    tree_etq.grid(row=6, column=0, columnspan=3, pady=5, sticky="nsew")

    # Ajusta weight da linha 6 para a tabela crescer
    frame_left.grid_rowconfigure(6, weight=1)

    ETIQUETAS = []  # lista de dicionários com as etiquetas

    def on_adicionar_etiqueta():
        nome = entry_nome.get().strip()
        preco_str = entry_preco.get().strip()
        qtd_str = entry_qtd.get().strip()
        oferta = var_oferta.get()

        if not nome or not preco_str or not qtd_str:
            messagebox.showwarning("Aviso", "Preencha nome, preço e quantidade.")
            return

        try:
            preco = float(preco_str.replace(",", "."))
        except ValueError:
            messagebox.showerror("Erro", "Preço inválido.")
            return

        try:
            qtd = int(qtd_str)
            if qtd <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Erro", "Quantidade inválida.")
            return

        etq = {
            "nome": nome,
            "preco": preco,
            "oferta": oferta,
            "qtd": qtd,
        }
        ETIQUETAS.append(etq)

        tree_etq.insert(
            "",
            "end",
            values=(
                nome,
                f"R$ {preco:.2f}",
                "SIM" if oferta else "NÃO",
                qtd,
            ),
        )

        # limpa apenas quantidade (para adicionar mais rápido)
        entry_qtd.delete(0, tk.END)
        entry_qtd.insert(0, "1")

    btn_add_etq = tk.Button(
        frame_left,
        text="Adicionar Etiqueta",
        command=on_adicionar_etiqueta,
        bg="#4CAF50",
        fg="white",
    )
    btn_add_etq.grid(row=7, column=0, columnspan=3, pady=10, sticky="ew")

    def on_limpar_fila():
        ETIQUETAS.clear()
        for item in tree_etq.get_children():
            tree_etq.delete(item)

    btn_limpar = tk.Button(
        frame_left,
        text="Limpar Fila",
        command=on_limpar_fila,
        bg="#f44336",
        fg="white",
    )
    btn_limpar.grid(row=8, column=0, columnspan=3, pady=5, sticky="ew")

    # ====== FRAME DE PRÉ-VISUALIZAÇÃO (DIREITA) ======
    frame_right = tk.Frame(janela, bg="#dddddd")
    frame_right.pack(side="right", fill="both", expand=True, padx=10, pady=10)

    tk.Label(
        frame_right,
        text="Pré-visualização das Etiquetas (para impressão):",
        bg="#dddddd",
        font=("Arial", 10, "bold"),
    ).pack(anchor="w", pady=5, padx=5)

    canvas = tk.Canvas(frame_right, bg="white")
    canvas.pack(fill="both", expand=True, padx=5, pady=5)

    def desenhar_etiquetas():
        canvas.delete("all")

        if not ETIQUETAS:
            canvas.create_text(
                10,
                10,
                anchor="nw",
                text="Nenhuma etiqueta na fila.",
                fill="black",
                font=("Arial", 12),
            )
            return

        # Configuração de grade de etiquetas
        margem_x = 20
        margem_y = 20
        largura = 200
        altura = 100
        espac_x = 10
        espac_y = 10
        colunas = 3  # 3 etiquetas por linha

        x = margem_x
        y = margem_y
        count = 0

        for etq in ETIQUETAS:
            for _ in range(etq["qtd"]):
                # Fundo amarelo
                canvas.create_rectangle(
                    x,
                    y,
                    x + largura,
                    y + altura,
                    fill="#FFF176",  # amarelo clarinho
                    outline="black",
                )

                # Se for oferta, escreve OFERTA em vermelho no topo
                if etq["oferta"]:
                    canvas.create_text(
                        x + largura / 2,
                        y + 20,
                        text="OFERTA",
                        fill="red",
                        font=("Arial", 14, "bold"),
                    )
                    offset_nome = 40
                else:
                    offset_nome = 25

                # Nome do produto (preto)
                canvas.create_text(
                    x + 10,
                    y + offset_nome,
                    anchor="w",
                    text=etq["nome"],
                    fill="black",
                    font=("Arial", 10, "bold"),
                )

                # Preço grande
                canvas.create_text(
                    x + largura / 2,
                    y + altura - 30,
                    text=f"R$ {etq['preco']:.2f}",
                    fill="black",
                    font=("Arial", 16, "bold"),
                )

                # Avança posição
                count += 1
                if count % colunas == 0:
                    x = margem_x
                    y += altura + espac_y
                else:
                    x += largura + espac_x

        # Ajusta scroll (se fosse usar scrollbar futuramente)
        canvas.config(scrollregion=canvas.bbox("all"))

    btn_preview = tk.Button(
        frame_left,
        text="Gerar Pré-visualização",
        command=desenhar_etiquetas,
    )
    btn_preview.grid(row=9, column=0, columnspan=3, pady=10, sticky="ew")

    # Ao abrir a tela, já mostra vazio
    desenhar_etiquetas()
