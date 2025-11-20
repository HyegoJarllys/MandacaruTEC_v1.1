import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import sqlite3

from db import get_connection


# --------------------------------------------------------
#  AJUSTE AUTOMÁTICO DO BANCO (EVITA "no such column")
# --------------------------------------------------------
def ensure_columns():
    """Garante que a tabela produtos tenha todas as colunas novas
       e que a tabela categorias exista."""
    try:
        conn = get_connection()
        cur = conn.cursor()

        # Verifica colunas da tabela produtos
        cur.execute("PRAGMA table_info(produtos)")
        cols = {row[1] for row in cur.fetchall()}

        def add_column(name, type_sql, default=None):
            if name not in cols:
                sql = f"ALTER TABLE produtos ADD COLUMN {name} {type_sql}"
                if default is not None:
                    sql += f" DEFAULT {default}"
                cur.execute(sql)

        # Colunas necessárias
        add_column("preco_venda", "REAL", 0)
        add_column("preco_custo", "REAL", 0)
        add_column("validade", "TEXT", "'0000-00-00'")
        add_column("estoque_atual", "INTEGER", 0)
        add_column("estoque_minimo", "INTEGER", 0)
        add_column("unidade_venda", "TEXT", "'UNIDADE'")
        add_column("categoria", "TEXT", "''")
        add_column("descricao", "TEXT", "''")

        # Tabela de categorias
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS categorias (
                id   INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL UNIQUE
            );
            """
        )

        conn.commit()
        conn.close()
    except Exception as e:
        print("Erro em ensure_columns:", e)


class CadastroProdutosApp:
    def __init__(self, parent=None):
        self.parent = parent

        if parent is None:
            self.janela = tk.Tk()
        else:
            self.janela = tk.Toplevel(parent)

        self.janela.title("Mandacaru TEC – Cadastro de Produtos")
        self.janela.geometry("950x600")
        self.janela.minsize(900, 550)

        if parent is not None:
            self.janela.transient(parent)
            self.janela.grab_set()

        # Garante que o banco está no formato certo
        ensure_columns()

        # Variáveis
        self.var_codigo = tk.StringVar()
        self.var_nome = tk.StringVar()
        self.var_preco_venda = tk.StringVar()
        self.var_preco_custo = tk.StringVar()
        self.var_validade = tk.StringVar()
        self.var_estoque_atual = tk.StringVar()
        self.var_estoque_minimo = tk.StringVar()
        self.var_unidade_venda = tk.StringVar(value="UNIDADE")
        self.var_categoria = tk.StringVar()

        self.var_lucro_produto = tk.StringVar(value="Lucro estimado deste produto: R$ 0,00")
        self.var_lucro_total = tk.StringVar(value="Lucro estimado de TODO estoque: R$ 0,00")

        self.text_descricao = None
        self.tree = None
        self.combo_categoria = None

        self._montar_layout()
        self._carregar_categorias()
        self._carregar_produtos()
        self._atualizar_lucro_total()

        # Atalhos
        self.janela.bind("<F2>", lambda e: self._buscar_por_codigo())
        self.janela.bind("<F5>", lambda e: self._salvar_ou_atualizar())
        self.janela.bind("<Delete>", lambda e: self._excluir_selecionado())
        self.janela.bind("<Escape>", lambda e: self._limpar_campos())

    # -------------------- LAYOUT --------------------

    def _montar_layout(self):
        frame_root = tk.Frame(self.janela, bg="#F5F5F7")
        frame_root.pack(fill="both", expand=True, padx=12, pady=12)

        # Título
        header = tk.Frame(frame_root, bg="#F5F5F7")
        header.pack(fill="x", pady=(0, 10))

        tk.Label(
            header,
            text="Cadastro de Produtos",
            bg="#F5F5F7",
            fg="#111111",
            font=("Segoe UI", 16, "bold"),
        ).pack(anchor="w")

        tk.Label(
            header,
            text="Bipagem rápida, estoque integrado e lucro estimado.",
            bg="#F5F5F7",
            fg="#555555",
            font=("Segoe UI", 9),
        ).pack(anchor="w")

        # Card principal
        card = tk.Frame(frame_root, bg="#FFFFFF", bd=1, relief="solid")
        card.pack(fill="x")

        # Linha 1 - Código + Buscar
        row1 = tk.Frame(card, bg="#FFFFFF")
        row1.pack(fill="x", padx=12, pady=(10, 4))

        tk.Label(row1, text="Código de barras *", bg="#FFFFFF").pack(side="left")
        entry_codigo = tk.Entry(row1, textvariable=self.var_codigo, width=25)
        entry_codigo.pack(side="left", padx=(6, 10))
        entry_codigo.focus()

        tk.Button(
            row1,
            text="Buscar por código (F2)",
            command=self._buscar_por_codigo,
        ).pack(side="left")

        # Linha 2 - Nome
        row2 = tk.Frame(card, bg="#FFFFFF")
        row2.pack(fill="x", padx=12, pady=4)

        tk.Label(row2, text="Nome do produto *", bg="#FFFFFF").pack(anchor="w")
        tk.Entry(row2, textvariable=self.var_nome).pack(fill="x", pady=(2, 0))

        # Linha 3 - preços + validade
        row3 = tk.Frame(card, bg="#FFFFFF")
        row3.pack(fill="x", padx=12, pady=4)

        tk.Label(row3, text="Preço venda (R$) *", bg="#FFFFFF").grid(row=0, column=0, sticky="w")
        tk.Label(row3, text="Preço custo (R$)", bg="#FFFFFF").grid(row=0, column=1, sticky="w")
        tk.Label(row3, text="Validade * (dd/mm/aaaa)", bg="#FFFFFF").grid(row=0, column=2, sticky="w")

        tk.Entry(row3, textvariable=self.var_preco_venda, width=12).grid(
            row=1, column=0, padx=(0, 10), pady=(2, 0)
        )
        tk.Entry(row3, textvariable=self.var_preco_custo, width=12).grid(
            row=1, column=1, padx=(0, 10), pady=(2, 0)
        )
        tk.Entry(row3, textvariable=self.var_validade, width=14).grid(
            row=1, column=2, padx=(0, 10), pady=(2, 0)
        )

        # Linha 4 - estoque + unidade + categoria
        row4 = tk.Frame(card, bg="#FFFFFF")
        row4.pack(fill="x", padx=12, pady=4)

        tk.Label(row4, text="Estoque atual", bg="#FFFFFF").grid(row=0, column=0, sticky="w")
        tk.Label(row4, text="Estoque mínimo", bg="#FFFFFF").grid(row=0, column=1, sticky="w")
        tk.Label(row4, text="Unidade de venda", bg="#FFFFFF").grid(row=0, column=2, sticky="w")
        tk.Label(row4, text="Categoria", bg="#FFFFFF").grid(row=0, column=3, sticky="w")

        tk.Entry(row4, textvariable=self.var_estoque_atual, width=10).grid(
            row=1, column=0, padx=(0, 10), pady=(2, 0)
        )
        tk.Entry(row4, textvariable=self.var_estoque_minimo, width=10).grid(
            row=1, column=1, padx=(0, 10), pady=(2, 0)
        )

        ttk.Combobox(
            row4,
            textvariable=self.var_unidade_venda,
            values=["UNIDADE", "KG"],
            state="readonly",
            width=12,
        ).grid(row=1, column=2, padx=(0, 10), pady=(2, 0))

        self.combo_categoria = ttk.Combobox(
            row4,
            textvariable=self.var_categoria,
            state="readonly",
            width=18,
        )
        self.combo_categoria.grid(row=1, column=3, padx=(0, 4), pady=(2, 0))

        tk.Button(
            row4,
            text="Nova categoria",
            command=self._nova_categoria,
            width=14,
        ).grid(row=1, column=4, padx=(4, 0), pady=(2, 0))

        # Linha 5 - descrição
        row5 = tk.Frame(card, bg="#FFFFFF")
        row5.pack(fill="both", padx=12, pady=(6, 8))

        tk.Label(row5, text="Descrição detalhada", bg="#FFFFFF").pack(anchor="w")
        self.text_descricao = tk.Text(row5, height=4)
        self.text_descricao.pack(fill="x", pady=(2, 0))

        # Linha 6 - lucro estimado + botões
        row6 = tk.Frame(card, bg="#FFFFFF")
        row6.pack(fill="x", padx=12, pady=(6, 10))

        tk.Label(
            row6,
            textvariable=self.var_lucro_produto,
            bg="#FFFFFF",
            fg="#111111",
        ).pack(side="left")

        tk.Label(
            row6,
            textvariable=self.var_lucro_total,
            bg="#FFFFFF",
            fg="#555555",
        ).pack(side="left", padx=(20, 0))

        frame_btns = tk.Frame(row6, bg="#FFFFFF")
        frame_btns.pack(side="right")

        tk.Button(
            frame_btns,
            text="Adicionar ao estoque",
            command=self._adicionar_estoque,
        ).pack(side="left", padx=4)

        tk.Button(
            frame_btns,
            text="Salvar / Atualizar (F5)",
            command=self._salvar_ou_atualizar,
        ).pack(side="left", padx=4)

        tk.Button(
            frame_btns,
            text="Excluir selecionado (Del)",
            command=self._excluir_selecionado,
        ).pack(side="left", padx=4)

        tk.Button(
            frame_btns,
            text="Limpar campos (Esc)",
            command=self._limpar_campos,
        ).pack(side="left", padx=4)

        # Tabela de produtos
        frame_table = tk.Frame(frame_root, bg="#F5F5F7")
        frame_table.pack(fill="both", expand=True, pady=(10, 0))

        colunas = ("codigo", "nome", "preco", "estoque", "validade", "categoria")
        self.tree = ttk.Treeview(frame_table, columns=colunas, show="headings", height=10)
        self.tree.pack(side="left", fill="both", expand=True)

        self.tree.heading("codigo", text="Código")
        self.tree.heading("nome", text="Nome")
        self.tree.heading("preco", text="Preço venda")
        self.tree.heading("estoque", text="Estoque")
        self.tree.heading("validade", text="Validade")
        self.tree.heading("categoria", text="Categoria")

        self.tree.column("codigo", width=120)
        self.tree.column("nome", width=260)
        self.tree.column("preco", width=90, anchor="e")
        self.tree.column("estoque", width=70, anchor="center")
        self.tree.column("validade", width=90, anchor="center")
        self.tree.column("categoria", width=120, anchor="w")

        scrollbar = ttk.Scrollbar(frame_table, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.bind("<<TreeviewSelect>>", lambda e: self._preencher_campos_da_selecao())

    # -------------------- CATEGORIAS --------------------

    def _carregar_categorias(self):
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("SELECT nome FROM categorias ORDER BY nome;")
            rows = cur.fetchall()
            categorias = [r["nome"] for r in rows]
            self.combo_categoria["values"] = categorias
            conn.close()
        except Exception as e:
            print("Erro ao carregar categorias:", e)

    def _nova_categoria(self):
        nome = simpledialog.askstring("Nova categoria", "Nome da categoria:", parent=self.janela)
        if not nome:
            return
        nome = nome.strip()
        if not nome:
            return

        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("INSERT OR IGNORE INTO categorias (nome) VALUES (?);", (nome,))
            conn.commit()
            conn.close()
            self._carregar_categorias()
            self.var_categoria.set(nome)
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar categoria:\n{e}")

    # -------------------- CRUD PRODUTOS --------------------

    def _carregar_produtos(self):
        self.tree.delete(*self.tree.get_children())
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute(
                """
                SELECT codigo_barras, nome, preco_venda, estoque_atual, validade, categoria
                  FROM produtos
                 ORDER BY nome;
                """
            )
            for row in cur.fetchall():
                self.tree.insert(
                    "",
                    "end",
                    values=(
                        row["codigo_barras"],
                        row["nome"],
                        f"R$ {row['preco_venda']:.2f}",
                        row["estoque_atual"],
                        row["validade"],
                        row["categoria"] or "",
                    ),
                )
            conn.close()
        except sqlite3.OperationalError as e:
            # Se ainda der "no such column", força ajuste e tenta de novo
            if "no such column" in str(e):
                ensure_columns()
                self._carregar_produtos()
            else:
                messagebox.showerror("Erro", f"Erro ao carregar produtos:\n{e}")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar produtos:\n{e}")

    def _buscar_por_codigo(self):
        codigo = self.var_codigo.get().strip()
        if not codigo:
            messagebox.showwarning("Aviso", "Informe um código de barras para buscar.")
            return

        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("SELECT * FROM produtos WHERE codigo_barras = ?;", (codigo,))
            row = cur.fetchone()
            conn.close()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao buscar produto:\n{e}")
            return

        if not row:
            messagebox.showinfo("Info", "Nenhum produto encontrado com esse código.")
            return

        self._preencher_campos_com_row(row)

    def _preencher_campos_da_selecao(self):
        sel = self.tree.focus()
        if not sel:
            return
        valores = self.tree.item(sel, "values")
        if not valores:
            return
        codigo = valores[0]
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("SELECT * FROM produtos WHERE codigo_barras = ?;", (codigo,))
            row = cur.fetchone()
            conn.close()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar produto selecionado:\n{e}")
            return

        if row:
            self._preencher_campos_com_row(row)

    def _preencher_campos_com_row(self, row):
        self.var_codigo.set(row["codigo_barras"])
        self.var_nome.set(row["nome"])
        self.var_preco_venda.set(f"{row['preco_venda']:.2f}")
        self.var_preco_custo.set(f"{row['preco_custo']:.2f}")
        self.var_validade.set(row["validade"] or "")
        self.var_estoque_atual.set(str(row["estoque_atual"]))
        self.var_estoque_minimo.set(str(row["estoque_minimo"]))
        self.var_unidade_venda.set(row["unidade_venda"] or "UNIDADE")
        self.var_categoria.set(row["categoria"] or "")

        self.text_descricao.delete("1.0", tk.END)
        if row["descricao"]:
            self.text_descricao.insert("1.0", row["descricao"])

        self._atualizar_lucro_produto()

    def _salvar_ou_atualizar(self):
        codigo = self.var_codigo.get().strip()
        nome = self.var_nome.get().strip()
        preco_venda_txt = self.var_preco_venda.get().strip()
        preco_custo_txt = self.var_preco_custo.get().strip()
        validade = self.var_validade.get().strip()
        estoque_atual_txt = self.var_estoque_atual.get().strip()
        estoque_minimo_txt = self.var_estoque_minimo.get().strip()
        unidade_venda = self.var_unidade_venda.get().strip() or "UNIDADE"
        categoria = self.var_categoria.get().strip() or ""
        descricao = self.text_descricao.get("1.0", tk.END).strip()

        if not codigo:
            messagebox.showwarning("Aviso", "Campo código de barras é obrigatório.")
            return
        if not nome:
            messagebox.showwarning("Aviso", "Campo nome do produto é obrigatório.")
            return
        if not preco_venda_txt:
            messagebox.showwarning("Aviso", "Campo preço venda é obrigatório.")
            return
        if not validade:
            messagebox.showwarning("Aviso", "Campo validade é obrigatório.")
            return

        try:
            preco_venda = float(preco_venda_txt.replace(",", "."))
        except ValueError:
            messagebox.showerror("Erro", "Preço de venda inválido.")
            return

        try:
            preco_custo = float(preco_custo_txt.replace(",", ".")) if preco_custo_txt else 0.0
        except ValueError:
            messagebox.showerror("Erro", "Preço de custo inválido.")
            return

        try:
            estoque_atual = int(estoque_atual_txt) if estoque_atual_txt else 0
            estoque_minimo = int(estoque_minimo_txt) if estoque_minimo_txt else 0
        except ValueError:
            messagebox.showerror("Erro", "Valores de estoque inválidos.")
            return

        try:
            conn = get_connection()
            cur = conn.cursor()

            cur.execute("SELECT id FROM produtos WHERE codigo_barras = ?;", (codigo,))
            row = cur.fetchone()

            if row:
                cur.execute(
                    """
                    UPDATE produtos
                       SET nome          = ?,
                           preco_venda   = ?,
                           preco_custo   = ?,
                           validade      = ?,
                           estoque_atual = ?,
                           estoque_minimo= ?,
                           unidade_venda = ?,
                           categoria     = ?,
                           descricao     = ?
                     WHERE codigo_barras = ?;
                    """,
                    (
                        nome,
                        preco_venda,
                        preco_custo,
                        validade,
                        estoque_atual,
                        estoque_minimo,
                        unidade_venda,
                        categoria,
                        descricao,
                        codigo,
                    ),
                )
            else:
                cur.execute(
                    """
                    INSERT INTO produtos
                        (codigo_barras, nome, preco_venda, preco_custo,
                         validade, estoque_atual, estoque_minimo,
                         unidade_venda, categoria, descricao)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                    """,
                    (
                        codigo,
                        nome,
                        preco_venda,
                        preco_custo,
                        validade,
                        estoque_atual,
                        estoque_minimo,
                        unidade_venda,
                        categoria,
                        descricao,
                    ),
                )

            conn.commit()
            conn.close()

            self._carregar_produtos()
            self._atualizar_lucro_produto()
            self._atualizar_lucro_total()
            messagebox.showinfo("Sucesso", "Produto salvo com sucesso.")
        except sqlite3.OperationalError as e:
            if "no such column" in str(e):
                ensure_columns()
                messagebox.showwarning(
                    "Aviso",
                    "Banco foi ajustado automaticamente. Tente salvar o produto novamente.",
                )
            else:
                messagebox.showerror("Erro", f"Erro ao salvar produto:\n{e}")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar produto:\n{e}")

    def _excluir_selecionado(self):
        sel = self.tree.focus()
        if not sel:
            messagebox.showwarning("Aviso", "Selecione um produto na lista.")
            return
        valores = self.tree.item(sel, "values")
        if not valores:
            return
        codigo = valores[0]

        if not messagebox.askyesno("Confirmação", f"Excluir o produto {codigo}?"):
            return

        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("DELETE FROM produtos WHERE codigo_barras = ?;", (codigo,))
            conn.commit()
            conn.close()

            self._carregar_produtos()
            self._atualizar_lucro_total()
            self._limpar_campos()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao excluir produto:\n{e}")

    # -------------------- ESTOQUE / LUCRO --------------------

    def _adicionar_estoque(self):
        codigo = self.var_codigo.get().strip()
        if not codigo:
            messagebox.showwarning("Aviso", "Carregue um produto antes de adicionar estoque.")
            return

        qtd = simpledialog.askinteger(
            "Adicionar ao estoque",
            "Quantidade para adicionar:",
            minvalue=1,
            parent=self.janela,
        )
        if not qtd:
            return

        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute(
                "UPDATE produtos SET estoque_atual = estoque_atual + ? WHERE codigo_barras = ?;",
                (qtd, codigo),
            )
            conn.commit()
            conn.close()

            self._buscar_por_codigo()
            self._carregar_produtos()
            self._atualizar_lucro_total()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao adicionar estoque:\n{e}")

    def _atualizar_lucro_produto(self):
        try:
            preco_venda = float(self.var_preco_venda.get().replace(",", ".") or 0)
            preco_custo = float(self.var_preco_custo.get().replace(",", ".") or 0)
            estoque_atual = int(self.var_estoque_atual.get() or 0)
        except ValueError:
            self.var_lucro_produto.set("Lucro estimado deste produto: R$ 0,00")
            return

        lucro = (preco_venda - preco_custo) * estoque_atual
        self.var_lucro_produto.set(f"Lucro estimado deste produto: R$ {lucro:.2f}")

    def _atualizar_lucro_total(self):
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute(
                """
                SELECT SUM( (preco_venda - preco_custo) * estoque_atual ) AS lucro
                  FROM produtos;
                """
            )
            row = cur.fetchone()
            conn.close()
            lucro_total = row["lucro"] if row and row["lucro"] is not None else 0
        except Exception:
            lucro_total = 0

        self.var_lucro_total.set(f"Lucro estimado de TODO estoque: R$ {lucro_total:.2f}")

    # -------------------- OUTROS --------------------

    def _limpar_campos(self):
        self.var_codigo.set("")
        self.var_nome.set("")
        self.var_preco_venda.set("")
        self.var_preco_custo.set("")
        self.var_validade.set("")
        self.var_estoque_atual.set("")
        self.var_estoque_minimo.set("")
        self.var_unidade_venda.set("UNIDADE")
        self.var_categoria.set("")
        self.text_descricao.delete("1.0", tk.END)
        self.var_lucro_produto.set("Lucro estimado deste produto: R$ 0,00")


def abrir_cadastro_produtos(parent=None):
    app = CadastroProdutosApp(parent)
    if parent is None:
        app.janela.mainloop()
    return app


if __name__ == "__main__":
    abrir_cadastro_produtos()
