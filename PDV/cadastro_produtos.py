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
    cur.execute("SELECT id, codigo_barras, nome, preco FROM produtos ORDER BY id DESC;")
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
                f"R$ {row['preco']:.2f}",
            ),
        )


def salvar_produto(entry_codigo, entry_nome, entry_preco, tree):
    codigo = entry_codigo.get().strip()
    nome = entry_nome.get().strip()
    preco_str = entry_preco.get().strip()

    if not codigo or not nome or not preco_str:
        messagebox.showwarning("Aviso", "Preencha todos os campos.")
        return

    try:
        preco = float(preco_str.replace(",", "."))
    except ValueError:
        messagebox.showerror("Erro", "Preço inválido.")
        return

    conn = get_connection()
    cur = conn.cursor()

    try:
        cur.execute(
            """
            INSERT OR REPLACE INTO produtos (codigo_barras, nome, preco)
            VALUES (?, ?, ?);
            """,
            (codigo, nome, preco),
        )
        conn.commit()
    except Exception as e:
        conn.close()
        messagebox.showerror("Erro", f"Erro ao salvar produto:\n{e}")
        return

    conn.close()
    messagebox.showinfo("Sucesso", "Produto salvo com sucesso!")

    # Limpar campos
    entry_codigo.delete(0, tk.END)
    entry_nome.delete(0, tk.END)
    entry_preco.delete(0, tk.END)

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
    janela.geometry("700x500")
    janela.configure(bg="#f7f7f7")

    # --------- TOPO: FORMULÁRIO ---------
    frame_form = tk.Frame(janela, bg="#f7f7f7")
    frame_form.pack(fill="x", padx=10, pady=10)

    tk.Label(frame_form, text="Código de Barras:", bg="#f7f7f7").grid(row=0, column=0, sticky="w")
    entry_codigo = tk.Entry(frame_form, width=30)
    entry_codigo.grid(row=0, column=1, padx=5, pady=5)

    tk.Label(frame_form, text="Nome do Produto:", bg="#f7f7f7").grid(row=1, column=0, sticky="w")
    entry_nome = tk.Entry(frame_form, width=50)
    entry_nome.grid(row=1, column=1, padx=5, pady=5)

    tk.Label(frame_form, text="Preço (R$):", bg="#f7f7f7").grid(row=2, column=0, sticky="w")
    entry_preco = tk.Entry(frame_form, width=15)
    entry_preco.grid(row=2, column=1, padx=5, pady=5, sticky="w")

    # Botão salvar
    btn_salvar = tk.Button(
        frame_form,
        text="Salvar / Atualizar",
        bg="#4CAF50",
        fg="white",
        command=lambda: salvar_produto(entry_codigo, entry_nome, entry_preco, tree),
    )
    btn_salvar.grid(row=3, column=1, pady=10, sticky="w")

    # --------- TABELA ---------
    frame_tab = tk.Frame(janela, bg="#f7f7f7")
    frame_tab.pack(fill="both", expand=True, padx=10, pady=10)

    colunas = ("codigo", "nome", "preco")
    tree = ttk.Treeview(frame_tab, columns=colunas, show="headings", height=10)
    tree.heading("codigo", text="Código de Barras")
    tree.heading("nome", text="Nome")
    tree.heading("preco", text="Preço")

    tree.column("codigo", width=180)
    tree.column("nome", width=350)
    tree.column("preco", width=100)

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

