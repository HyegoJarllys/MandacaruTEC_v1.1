import tkinter as tk
from tkinter import ttk, messagebox
from db import get_connection


# ============================================================
# BUSCA PRODUTO NO BANCO
# ============================================================
def buscar_produto_por_codigo(codigo_barras: str):
    """
    Busca 1 produto no banco pelo código de barras.
    Retorna dict {"id", "codigo_barras", "nome", "preco"} ou None.
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT id, codigo_barras, nome, preco FROM produtos WHERE codigo_barras = ?;",
        (codigo_barras,),
    )
    row = cur.fetchone()
    conn.close()

    if not row:
        return None

    return {
        "id": row[0],
        "codigo_barras": row[1],
        "nome": row[2],
        "preco": float(row[3]),
    }


# ============================================================
# TELA DE ETIQUETAS
# ============================================================
def abrir_modo_etiquetas(parent=None):
    """
    Tela de geração de etiquetas em estilo atacado.

    - Nome em MAIÚSCULO e negrito.
    - Preço grande.
    - Modo OFERTA com fundo amarelo e 'OFERTA' em vermelho.
    - Lista / fila de etiquetas.
    - Pré-visualização em grid.
    """

    # ----- Janela -----
    if parent is None:
        janela = tk.Tk()
    else:
        janela = tk.Toplevel(parent)

    janela.title("Mandacaru TEC - Modo Etiquetas")
    janela.geometry("980x650")
    janela.configure(bg="#f7f7f7")

    # ========================================================
    # LADO ESQUERDO - CONTROLE
    # ========================================================
    frame_left = tk.Frame(janela, bg="#f7f7f7")
    frame_left.pack(side="left", fill="y", padx=10, pady=10)

    # Código de Barras
    tk.Label(frame_left, text="Código de Barras:", bg="#f7f7f7").grid(
        row=0, column=0, sticky="w"
    )
    entry_codigo = tk.Entry(frame_left, width=25)
    entry_codigo.grid(row=0, column=1, padx=5, pady=5)

    def on_buscar(_evt=None):
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

    btn_buscar = tk.Button(frame_left, text="Buscar (Enter)", command=on_buscar)
    btn_buscar.grid(row=0, column=2, padx=5, pady=5)

    entry_codigo.bind("<Return>", on_buscar)

    # Nome do produto
    tk.Label(frame_left, text="Nome do Produto:", bg="#f7f7f7").grid(
        row=1, column=0, sticky="w"
    )
    entry_nome = tk.Entry(frame_left, width=40)
    entry_nome.grid(row=1, column=1, columnspan=2, padx=5, pady=5, sticky="w")

    # Preço
    tk.Label(frame_left, text="Preço (R$):", bg="#f7f7f7").grid(
        row=2, column=0, sticky="w"
    )
    entry_preco = tk.Entry(frame_left, width=15)
    entry_preco.grid(row=2, column=1, padx=5, pady=5, sticky="w")

    # Observação (ex: "POR KG", "À VISTA", etc.)
    tk.Label(frame_left, text="Observação:", bg="#f7f7f7").grid(
        row=3, column=0, sticky="w"
    )
    entry_obs = tk.Entry(frame_left, width=25)
    entry_obs.insert(0, "À VISTA")
    entry_obs.grid(row=3, column=1, columnspan=2, padx=5, pady=5, sticky="w")

    # Checkbox de oferta
    var_oferta = tk.BooleanVar(value=False)
    chk_oferta = tk.Checkbutton(
        frame_left,
        text="Etiqueta de OFERTA (destaque amarelo/vermelho)",
        bg="#f7f7f7",
        variable=var_oferta,
    )
    chk_oferta.grid(row=4, column=0, columnspan=3, sticky="w", pady=5)

    # Quantidade de etiquetas
    tk.Label(frame_left, text="Qtd de Etiquetas:", bg="#f7f7f7").grid(
        row=5, column=0, sticky="w"
    )
    entry_qtd = tk.Entry(frame_left, width=10)
    entry_qtd.insert(0, "1")
    entry_qtd.grid(row=5, column=1, padx=5, pady=5, sticky="w")

    # --------------------------------------------------------
    # Tabela da Fila de Etiquetas
    # --------------------------------------------------------
    tk.Label(
        frame_left,
        text="Etiquetas na Fila:",
        bg="#f7f7f7",
        font=("Arial", 10, "bold"),
    ).grid(row=6, column=0, columnspan=3, sticky="w", pady=(15, 5))

    tree_cols = ("produto", "preco", "oferta", "obs", "qtd")
    tree_etq = ttk.Treeview(frame_left, columns=tree_cols, show="headings", height=8)
    tree_etq.heading("produto", text="Produto")
    tree_etq.heading("preco", text="Preço")
    tree_etq.heading("oferta", text="OFERTA")
    tree_etq.heading("obs", text="Obs.")
    tree_etq.heading("qtd", text="Qtd")

    tree_etq.column("produto", width=220)
    tree_etq.column("preco", width=80, anchor="e")
    tree_etq.column("oferta", width=60, anchor="center")
    tree_etq.column("obs", width=100)
    tree_etq.column("qtd", width=40, anchor="center")

    tree_etq.grid(row=7, column=0, columnspan=3, pady=5, sticky="nsew")

    # Deixar a linha da tabela expansível
    frame_left.grid_rowconfigure(7, weight=1)

    # Lista de etiquetas na fila
    ETIQUETAS = []

    def on_adicionar_etiqueta():
        nome = entry_nome.get().strip()
        preco_str = entry_preco.get().strip()
        obs = entry_obs.get().strip()
        qtd_str = entry_qtd.get().strip()
        oferta = var_oferta.get()

        if not nome or not preco_str or not qtd_str:
            messagebox.showwarning(
                "Aviso", "Preencha nome, preço e quantidade antes de adicionar."
            )
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
            "obs": obs,
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
                obs,
                qtd,
            ),
        )

        # Deixa quantidade e oferta prontas pra próxima etiqueta
        entry_qtd.delete(0, tk.END)
        entry_qtd.insert(0, "1")

    btn_add_etq = tk.Button(
        frame_left,
        text="Adicionar à Fila",
        command=on_adicionar_etiqueta,
        bg="#4CAF50",
        fg="white",
    )
    btn_add_etq.grid(row=8, column=0, columnspan=3, pady=10, sticky="ew")

    def on_remover_selecionada():
        sel = tree_etq.selection()
        if not sel:
            return
        idx = tree_etq.index(sel[0])
        tree_etq.delete(sel[0])
        if 0 <= idx < len(ETIQUETAS):
            ETIQUETAS.pop(idx)

    btn_remover = tk.Button(
        frame_left,
        text="Remover Selecionada",
        command=on_remover_selecionada,
        bg="#f44336",
        fg="white",
    )
    btn_remover.grid(row=9, column=0, columnspan=3, pady=5, sticky="ew")

    def on_limpar_fila():
        ETIQUETAS.clear()
        for item in tree_etq.get_children():
            tree_etq.delete(item)

    btn_limpar = tk.Button(
        frame_left,
        text="Limpar Fila",
        command=on_limpar_fila,
        bg="#555555",
        fg="white",
    )
    btn_limpar.grid(row=10, column=0, columnspan=3, pady=5, sticky="ew")

    # ========================================================
    # LADO DIREITO - PRÉ-VISUALIZAÇÃO
    # ========================================================
    frame_right = tk.Frame(janela, bg="#dcdcdc")
    frame_right.pack(side="right", fill="both", expand=True, padx=10, pady=10)

    tk.Label(
        frame_right,
        text="Pré-visualização das Etiquetas (estilo atacado):",
        bg="#dcdcdc",
        font=("Arial", 10, "bold"),
    ).pack(anchor="w", pady=5, padx=5)

    canvas = tk.Canvas(frame_right, bg="white")
    canvas.pack(fill="both", expand=True, padx=5, pady=5)

    # --------------------------------------------------------
    # DESENHAR ETIQUETAS
    # --------------------------------------------------------
    def desenhar_etiquetas():
        canvas.delete("all")

        if not ETIQUETAS:
            canvas.create_text(
                20,
                20,
                anchor="nw",
                text="Nenhuma etiqueta na fila.\nAdicione etiquetas à esquerda.",
                fill="black",
                font=("Arial", 12),
            )
            return

        # Configuração do layout
        margem_x = 25
        margem_y = 25
        largura = 260
        altura = 130
        espac_x = 15
        espac_y = 15
        colunas = 3  # 3 por linha

        x = margem_x
        y = margem_y
        count = 0

        for etq in ETIQUETAS:
            for _ in range(etq["qtd"]):
                oferta = etq["oferta"]
                nome = etq["nome"].upper()  # MAIÚSCULO
                preco = etq["preco"]
                obs = etq["obs"]

                # Fundo
                if oferta:
                    bg_color = "#FFF176"  # amarelo oferta
                else:
                    bg_color = "#FFFFFF"  # branco

                canvas.create_rectangle(
                    x,
                    y,
                    x + largura,
                    y + altura,
                    fill=bg_color,
                    outline="black",
                    width=2,
                )

                # Linha superior: OFERTA (se marcado)
                if oferta:
                    # Faixa vermelha em cima
                    canvas.create_rectangle(
                        x,
                        y,
                        x + largura,
                        y + 30,
                        fill="#D32F2F",
                        outline="#D32F2F",
                    )
                    canvas.create_text(
                        x + largura / 2,
                        y + 15,
                        text="OFERTA",
                        fill="white",
                        font=("Arial", 16, "bold"),
                    )
                    offset_top = 38
                else:
                    offset_top = 12

                # Nome do produto - MAIÚSCULO, negrito
                canvas.create_text(
                    x + 8,
                    y + offset_top,
                    anchor="nw",
                    text=nome,
                    fill="black",
                    font=("Arial", 10, "bold"),
                    width=largura - 16,
                )

                # Observação (ex: POR KG / À VISTA)
                if obs:
                    canvas.create_text(
                        x + 8,
                        y + altura - 35,
                        anchor="nw",
                        text=obs.upper(),
                        fill="black",
                        font=("Arial", 9, "bold"),
                    )

                # Preço grande, centralizado
                canvas.create_text(
                    x + largura / 2,
                    y + altura - 60,
                    text=f"R$ {preco:.2f}",
                    fill="black",
                    font=("Arial", 20, "bold"),
                )

                # Avança posição na grade
                count += 1
                if count % colunas == 0:
                    x = margem_x
                    y += altura + espac_y
                else:
                    x += largura + espac_x

        canvas.config(scrollregion=canvas.bbox("all"))

    btn_preview = tk.Button(
        frame_left,
        text="Atualizar Pré-visualização",
        command=desenhar_etiquetas,
    )
    btn_preview.grid(row=11, column=0, columnspan=3, pady=10, sticky="ew")

    # Ao abrir, mostra preview vazio
    desenhar_etiquetas()

    # Fechar janela standalone
    if parent is None:
        janela.mainloop()


# ============================================================
# EXECUÇÃO DIRETA (TESTE FORA DO PDV)
# ============================================================
if __name__ == "__main__":
    abrir_modo_etiquetas()
