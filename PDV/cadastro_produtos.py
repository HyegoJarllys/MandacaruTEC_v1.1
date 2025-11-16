import tkinter as tk
from tkinter import ttk, messagebox

from db import get_connection


# =====================================================================
# BANCO
# =====================================================================
def _get_conn():
    return get_connection()


def _garantir_colunas_produtos():
    """
    Garante que a tabela produtos tenha:
      - codigo_barras (unique)
      - nome
      - preco
      - estoque
      - custo
      - validade
    """
    conn = _get_conn()
    cur = conn.cursor()

    # Cria se não existir (básica)
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS produtos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo_barras TEXT UNIQUE,
            nome TEXT,
            preco REAL DEFAULT 0
        );
        """
    )

    # Garante colunas adicionais
    cur.execute("PRAGMA table_info(produtos);")
    cols = {row[1] for row in cur.fetchall()}

    if "estoque" not in cols:
        cur.execute("ALTER TABLE produtos ADD COLUMN estoque REAL DEFAULT 0;")

    if "custo" not in cols:
        cur.execute("ALTER TABLE produtos ADD COLUMN custo REAL DEFAULT 0;")

    if "validade" not in cols:
        cur.execute("ALTER TABLE produtos ADD COLUMN validade TEXT;")

    conn.commit()
    conn.close()


def _buscar_produto(codigo_barras):
    conn = _get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT id, codigo_barras, nome, preco, estoque, custo, validade
        FROM produtos
        WHERE codigo_barras = ?;
        """,
        (codigo_barras,),
    )
    row = cur.fetchone()
    conn.close()
    return row


def _listar_produtos():
    conn = _get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT codigo_barras, nome, preco, estoque, validade
        FROM produtos
        ORDER BY nome ASC;
        """
    )
    rows = cur.fetchall()
    conn.close()
    return rows


def _salvar_produto(codigo, nome, preco, qtd_add, custo, validade):
    """
    Se o produto já existe:
      - soma qtd_add ao estoque
      - atualiza nome, preco, custo, validade
    Senão:
      - cria com estoque = qtd_add
    """
    conn = _get_conn()
    cur = conn.cursor()

    cur.execute(
        "SELECT id, estoque FROM produtos WHERE codigo_barras = ?;",
        (codigo,),
    )
    row = cur.fetchone()

    if row:
        prod_id, estoque_atual = row
        novo_estoque = (estoque_atual or 0) + qtd_add

        cur.execute(
            """
            UPDATE produtos
            SET nome = ?, preco = ?, estoque = ?, custo = ?, validade = ?
            WHERE id = ?;
            """,
            (nome, preco, novo_estoque, custo, validade, prod_id),
        )
    else:
        cur.execute(
            """
            INSERT INTO produtos
                (codigo_barras, nome, preco, estoque, custo, validade)
            VALUES (?, ?, ?, ?, ?, ?);
            """,
            (codigo, nome, preco, qtd_add, custo, validade),
        )

    conn.commit()
    conn.close()


def _excluir_produto(codigo):
    conn = _get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM produtos WHERE codigo_barras = ?;", (codigo,))
    conn.commit()
    conn.close()


# =====================================================================
# INTERFACE
# =====================================================================
def abrir_cadastro_produtos(parent=None):
    _garantir_colunas_produtos()

    jan = tk.Toplevel(parent) if parent is not None else tk.Tk()
    jan.title("Mandacaru TEC - Cadastro de Produtos")
    jan.geometry("700x500")
    jan.configure(bg="#f7f7f7")

    # ----------------- CAMPOS SUPERIORES -----------------
    frame_top = tk.Frame(jan, bg="#f7f7f7")
    frame_top.pack(fill="x", padx=10, pady=10)

    # Código de barras
    tk.Label(frame_top, text="Código de Barras:", bg="#f7f7f7").grid(row=0, column=0, sticky="w")
    entry_codigo = tk.Entry(frame_top, width=25)
    entry_codigo.grid(row=0, column=1, padx=5, pady=3, sticky="w")

    # Nome
    tk.Label(frame_top, text="Nome:", bg="#f7f7f7").grid(row=1, column=0, sticky="w")
    entry_nome = tk.Entry(frame_top, width=40)
    entry_nome.grid(row=1, column=1, padx=5, pady=3, sticky="w")

    # Preço venda
    tk.Label(frame_top, text="Preço (R$):", bg="#f7f7f7").grid(row=2, column=0, sticky="w")
    entry_preco = tk.Entry(frame_top, width=10)
    entry_preco.grid(row=2, column=1, padx=5, pady=3, sticky="w")

    # Custo
    tk.Label(frame_top, text="Custo (R$):", bg="#f7f7f7").grid(row=2, column=2, sticky="w")
    entry_custo = tk.Entry(frame_top, width=10)
    entry_custo.grid(row=2, column=3, padx=5, pady=3, sticky="w")

    # Quantidade para adicionar ao estoque
    tk.Label(frame_top, text="Qtd p/ Estoque:", bg="#f7f7f7").grid(row=3, column=0, sticky="w")
    entry_qtd = tk.Entry(frame_top, width=10)
    entry_qtd.insert(0, "0")
    entry_qtd.grid(row=3, column=1, padx=5, pady=3, sticky="w")

    # Validade
    tk.Label(frame_top, text="Validade (dd/mm/aaaa):", bg="#f7f7f7").grid(row=3, column=2, sticky="w")
    entry_validade = tk.Entry(frame_top, width=12)
    entry_validade.grid(row=3, column=3, padx=5, pady=3, sticky="w")

    # ----------------- BOTÕES -----------------
    frame_btn = tk.Frame(jan, bg="#f7f7f7")
    frame_btn.pack(fill="x", padx=10, pady=5)

    def limpar_campos():
        entry_codigo.delete(0, tk.END)
        entry_nome.delete(0, tk.END)
        entry_preco.delete(0, tk.END)
        entry_custo.delete(0, tk.END)
        entry_qtd.delete(0, tk.END)
        entry_qtd.insert(0, "0")
        entry_validade.delete(0, tk.END)
        entry_codigo.focus()

    def carregar_produto():
        codigo = entry_codigo.get().strip()
        if not codigo:
            messagebox.showwarning("Aviso", "Informe o código de barras para buscar.")
            return

        row = _buscar_produto(codigo)
        if not row:
            messagebox.showinfo("Info", "Produto não cadastrado ainda. Preencha os dados.")
            entry_nome.delete(0, tk.END)
            entry_preco.delete(0, tk.END)
            entry_custo.delete(0, tk.END)
            entry_qtd.delete(0, tk.END)
            entry_qtd.insert(0, "0")
            entry_validade.delete(0, tk.END)
            return

        _, _, nome, preco, estoque, custo, validade = row
        entry_nome.delete(0, tk.END)
        entry_nome.insert(0, nome or "")

        entry_preco.delete(0, tk.END)
        entry_preco.insert(0, f"{(preco or 0):.2f}")

        entry_custo.delete(0, tk.END)
        entry_custo.insert(0, f"{(custo or 0):.2f}")

        entry_qtd.delete(0, tk.END)
        entry_qtd.insert(0, "0")  # qtd a adicionar agora

        entry_validade.delete(0, tk.END)
        if validade:
            entry_validade.insert(0, validade)

    def salvar_produto():
        codigo = entry_codigo.get().strip()
        nome = entry_nome.get().strip()
        preco_txt = entry_preco.get().strip().replace(",", ".")
        custo_txt = entry_custo.get().strip().replace(",", ".")
        qtd_txt = entry_qtd.get().strip()
        validade = entry_validade.get().strip()

        if not codigo or not nome or not preco_txt:
            messagebox.showwarning("Aviso", "Código, Nome e Preço são obrigatórios.")
            return

        try:
            preco = float(preco_txt)
        except ValueError:
            messagebox.showerror("Erro", "Preço inválido.")
            return

        try:
            custo = float(custo_txt) if custo_txt else 0.0
        except ValueError:
            messagebox.showerror("Erro", "Custo inválido.")
            return

        try:
            qtd_add = int(qtd_txt) if qtd_txt else 0
        except ValueError:
            messagebox.showerror("Erro", "Quantidade inválida.")
            return

        try:
            _salvar_produto(codigo, nome, preco, qtd_add, custo, validade)
            messagebox.showinfo("Sucesso", "Produto salvo/atualizado com sucesso.")
            carregar_tabela()
            limpar_campos()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar produto:\n{e}")

    def excluir_produto_sel():
        sel = tree.focus()
        if not sel:
            messagebox.showwarning("Aviso", "Selecione um produto na tabela.")
            return
        codigo = tree.item(sel, "values")[0]
        if not messagebox.askyesno("Confirmação", f"Excluir produto {codigo}?"):
            return
        try:
            _excluir_produto(codigo)
            carregar_tabela()
            limpar_campos()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao excluir produto:\n{e}")

    tk.Button(
        frame_btn, text="Buscar por Código", command=carregar_produto
    ).pack(side="left", padx=5)

    tk.Button(
        frame_btn, text="Salvar / Atualizar", bg="#4CAF50", fg="white",
        command=salvar_produto
    ).pack(side="left", padx=5)

    tk.Button(
        frame_btn, text="Excluir Selecionado", bg="#f44336", fg="white",
        command=excluir_produto_sel
    ).pack(side="left", padx=5)

    tk.Button(
        frame_btn, text="Limpar Campos", command=limpar_campos
    ).pack(side="left", padx=5)

    # ----------------- TABELA -----------------
    frame_table = tk.Frame(jan, bg="#f7f7f7")
    frame_table.pack(fill="both", expand=True, padx=10, pady=10)

    cols = ("codigo", "nome", "preco", "estoque", "validade")
    tree = ttk.Treeview(frame_table, columns=cols, show="headings", height=10)
    tree.pack(side="left", fill="both", expand=True)

    tree.heading("codigo", text="Código")
    tree.heading("nome", text="Nome")
    tree.heading("preco", text="Preço")
    tree.heading("estoque", text="Estoque")
    tree.heading("validade", text="Validade")

    tree.column("codigo", width=100)
    tree.column("nome", width=220)
    tree.column("preco", width=80, anchor="e")
    tree.column("estoque", width=70, anchor="e")
    tree.column("validade", width=100, anchor="center")

    scroll = ttk.Scrollbar(frame_table, orient="vertical", command=tree.yview)
    tree.configure(yscroll=scroll.set)
    scroll.pack(side="right", fill="y")

    def carregar_tabela():
        for item in tree.get_children():
            tree.delete(item)
        rows = _listar_produtos()
        for codigo, nome, preco, estoque, validade in rows:
            tree.insert(
                "",
                "end",
                values=(
                    codigo,
                    nome,
                    f"R$ {float(preco or 0):.2f}",
                    int(estoque or 0),
                    validade or "",
                ),
            )

    def on_select(event=None):
        sel = tree.focus()
        if not sel:
            return
        codigo, nome, preco_txt, estoque_txt, validade = tree.item(sel, "values")
        entry_codigo.delete(0, tk.END)
        entry_codigo.insert(0, codigo)

        entry_nome.delete(0, tk.END)
        entry_nome.insert(0, nome)

        entry_preco.delete(0, tk.END)
        entry_preco.insert(0, preco_txt.replace("R$ ", "").replace(",", "."))

        entry_qtd.delete(0, tk.END)
        entry_qtd.insert(0, "0")

        entry_validade.delete(0, tk.END)
        if validade:
            entry_validade.insert(0, validade)

        # custo não vem na tabela; se quiser, busco do banco:
        row = _buscar_produto(codigo)
        if row:
            _, _, _, _, _, custo, val_db = row
            entry_custo.delete(0, tk.END)
            entry_custo.insert(0, f"{float(custo or 0):.2f}")

            entry_validade.delete(0, tk.END)
            if val_db:
                entry_validade.insert(0, val_db)

    tree.bind("<<TreeviewSelect>>", on_select)

    carregar_tabela()
    entry_codigo.focus()

    if parent is None:
        jan.mainloop()
