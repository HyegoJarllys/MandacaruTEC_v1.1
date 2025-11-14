import tkinter as tk
from tkinter import ttk, messagebox
from db import get_connection


def carregar_produtos(tree):
    """Carrega os produtos do banco e joga na tabela."""
    # Limpar tabela
    for item in tree.get_children():
        tree.delete(item)

    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT id, codigo_barras, nome, preco, preco_custo, estoque FROM produtos ORDER BY id DESC;"
    )
    rows = cur.fetchall()
    conn.close()

    for row in rows:
        tree.insert(
            "",
            "end",
            iid=str(row["id"]),
            values=(
                row["codigo_barras"],
                row["nome"],
                f"R$ {row['preco']:.2f}",          # preço de venda
                f"R$ {row['preco_custo']:.2f}",    # custo
                row["estoque"] if row["estoque"] is not None else 0,
            ),
        )


def salvar_produto(entry_codigo, entry_nome, entry_preco_venda,
                   entry_preco_custo, entry_estoque_somar,
                   entry_estoque_min, tree):
    codigo = entry_codigo.get().strip()
    nome = entry_nome.get().strip()
    preco_venda_str = entry_preco_venda.get().strip()
    preco_custo_str = entry_preco_custo.get().strip()
    estoque_str = entry_estoque_somar.get().strip()
    estoque_min_str = entry_estoque_min.get().strip()

    if not codigo or not nome or not preco_venda_str or not preco_custo_str:
        messagebox.showwarning(
            "Aviso",
            "Preencha pelo menos código, nome, preço de venda e custo."
        )
        return

    try:
        preco_venda = float(preco_venda_str.replace(",", "."))
    except ValueError:
        messagebox.showerror("Erro", "Preço de venda inválido.")
        return

    try:
        preco_custo = float(preco_custo_str.replace(",", "."))
    except ValueError:
        messagebox.showerror("Erro", "Preço de custo inválido.")
        return

    try:
        qtd_informada = float(estoque_str.replace(",", ".")) if estoque_str else 0.0
    except ValueError:
        messagebox.showerror("Erro", "Quantidade para somar ao estoque inválida.")
        return

    try:
        estoque_minimo = float(estoque_min_str.replace(",", ".")) if estoque_min_str else 0.0
    except ValueError:
        messagebox.showerror("Erro", "Estoque mínimo inválido.")
        return

    conn = get_connection()
    cur = conn.cursor()

    # Verifica se já existe produto com esse código
    cur.execute(
        "SELECT id, estoque FROM produtos WHERE codigo_barras = ? ORDER BY id DESC LIMIT 1;",
        (codigo,),
    )
    existente = cur.fetchone()

    try:
        if existente:
            # Já existe produto com esse código → SOMA estoque
            estoque_atual = existente["estoque"] if existente["estoque"] is not None else 0.0
            estoque_novo = estoque_atual + qtd_informada

            cur.execute(
                """
                UPDATE produtos
                SET nome = ?, preco = ?, preco_custo = ?, estoque = ?, estoque_minimo = ?
                WHERE id = ?;
                """,
                (nome, preco_venda, preco_custo, estoque_novo, estoque_minimo, existente["id"]),
            )
            mensagem = (
                f"Produto atualizado.\n\n"
                f"Estoque anterior: {estoque_atual:.2f}\n"
                f"Quantidade adicionada: {qtd_informada:.2f}\n"
                f"Novo estoque: {estoque_novo:.2f}"
            )
        else:
            # Não existe → cadastra novo produto
            cur.execute(
                """
                INSERT INTO produtos
                    (codigo_barras, nome, preco, preco_custo, estoque, estoque_minimo)
                VALUES (?, ?, ?, ?, ?, ?);
                """,
                (codigo, nome, preco_venda, preco_custo, qtd_informada, estoque_minimo),
            )
            mensagem = (
                "Produto cadastrado com sucesso.\n\n"
                f"Estoque inicial: {qtd_informada:.2f}"
            )

        conn.commit()
    except Exception as e:
        conn.close()
        messagebox.showerror("Erro", f"Erro ao salvar produto:\n{e}")
        return

    conn.close()
    messagebox.showinfo("Sucesso", mensagem)

    # Limpar campos
    entry_codigo.delete(0, tk.END)
    entry_nome.delete(0, tk.END)
    entry_preco_venda.delete(0, tk.END)
    entry_preco_custo.delete(0, tk.END)
    entry_estoque_somar.delete(0, tk.END)
    entry_estoque_min.delete(0, tk.END)

    carregar_produtos(tree)


def deletar_produto(tree):
    selec = tree.selection()
    if not selec:
        messagebox.showwarning("Aviso", "Selecione um produto na tabela.")
        return

    iid = selec[0]
    resposta = messagebox.askyesno(
        "Confirmação", "Tem certeza que deseja excluir este produto?"
    )
    if not resposta:
        return

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM produtos WHERE id = ?;", (iid,))
    conn.commit()
    conn.close()

    tree.delete(iid)
    messagebox.showinfo("Sucesso", "Produto excluído.")


def abrir_cadastro_produtos(parent=None):
    """
    Se parent for None: abre uma janela principal (para rodar sozinho).
    Se parent for uma janela Tk existente (PDV): abre como janela filha (Toplevel).
    """
    if parent is None:
        janela = tk.Tk()
    else:
        janela = tk.Toplevel(parent)

    janela.title("Mandacaru TEC - Cadastro de Produtos")
    janela.geometry("900x550")
    janela.configure(bg="#f7f7f7")

    # --------- TOPO: FORMULÁRIO ---------
    frame_form = tk.Frame(janela, bg="#f7f7f7")
    frame_form.pack(fill="x", padx=10, pady=10)

    tk.Label(frame_form, text="Código de Barras:", bg="#f7f7f7").grid(row=0, column=0, sticky="w")
    entry_codigo = tk.Entry(frame_form, width=30)
    entry_codigo.grid(row=0, column=1, padx=5, pady=5)

    tk.Label(frame_form, text="Nome do Produto:", bg="#f7f7f7").grid(row=1, column=0, sticky="w")
    entry_nome = tk.Entry(frame_form, width=50)
    entry_nome.grid(row=1, column=1, padx=5, pady=5, columnspan=2, sticky="w")

    tk.Label(frame_form, text="Preço de Venda (R$):", bg="#f7f7f7").grid(row=2, column=0, sticky="w")
    entry_preco_venda = tk.Entry(frame_form, width=15)
    entry_preco_venda.grid(row=2, column=1, padx=5, pady=5, sticky="w")

    tk.Label(frame_form, text="Preço de Custo (R$):", bg="#f7f7f7").grid(row=3, column=0, sticky="w")
    entry_preco_custo = tk.Entry(frame_form, width=15)
    entry_preco_custo.grid(row=3, column=1, padx=5, pady=5, sticky="w")

    tk.Label(frame_form, text="Qtd para somar ao estoque:", bg="#f7f7f7").grid(row=4, column=0, sticky="w")
    entry_estoque_somar = tk.Entry(frame_form, width=15)
    entry_estoque_somar.grid(row=4, column=1, padx=5, pady=5, sticky="w")

    tk.Label(frame_form, text="Estoque Mínimo:", bg="#f7f7f7").grid(row=5, column=0, sticky="w")
    entry_estoque_min = tk.Entry(frame_form, width=15)
    entry_estoque_min.grid(row=5, column=1, padx=5, pady=5, sticky="w")

    # Botão salvar
    btn_salvar = tk.Button(
        frame_form,
        text="Salvar / Atualizar",
        bg="#4CAF50",
        fg="white",
        command=lambda: salvar_produto(
            entry_codigo,
            entry_nome,
            entry_preco_venda,
            entry_preco_custo,
            entry_estoque_somar,
            entry_estoque_min,
            tree,
        ),
    )
    btn_salvar.grid(row=6, column=1, pady=10, sticky="w")

    # --------- TABELA ---------
    frame_tab = tk.Frame(janela, bg="#f7f7f7")
    frame_tab.pack(fill="both", expand=True, padx=10, pady=10)

    colunas = ("codigo", "nome", "preco_venda", "preco_custo", "estoque")
    tree = ttk.Treeview(frame_tab, columns=colunas, show="headings", height=10)
    tree.heading("codigo", text="Código de Barras")
    tree.heading("nome", text="Nome")
    tree.heading("preco_venda", text="Preço Venda")
    tree.heading("preco_custo", text="Custo")
    tree.heading("estoque", text="Estoque")

    tree.column("codigo", width=140)
    tree.column("nome", width=280)
    tree.column("preco_venda", width=100)
    tree.column("preco_custo", width=100)
    tree.column("estoque", width=80, anchor="center")

    tree.pack(side="left", fill="both", expand=True)

    scrollbar = ttk.Scrollbar(frame_tab, orient="vertical", command=tree.yview)
    scrollbar.pack(side="right", fill="y")
    tree.configure(yscrollcommand=scrollbar.set)

    # --------- BOTÕES INFERIORES ---------
    frame_btn = tk.Frame(janela, bg="#f7f7f7")
    frame_btn.pack(fill="x", padx=10, pady=10)

    btn_recarregar = tk.Button(
        frame_btn,
        text="Recarregar",
        command=lambda: carregar_produtos(tree),
    )
    btn_recarregar.pack(side="left")

    btn_deletar = tk.Button(
        frame_btn,
        text="Excluir Produto Selecionado",
        bg="#f44336",
        fg="white",
        command=lambda: deletar_produto(tree),
    )
    btn_deletar.pack(side="right")

    # Carregar produtos ao abrir
    carregar_produtos(tree)

    # Se estiver rodando sozinho, precisa de mainloop
    if parent is None:
        janela.mainloop()


if __name__ == "__main__":
    abrir_cadastro_produtos()
