import tkinter as tk
from tkinter import ttk, messagebox
from db import get_connection
import os
import tempfile


def criar_icone_cacto():
    """Cria um ícone de cacto e retorna o caminho do arquivo temporário."""
    try:
        from PIL import Image, ImageDraw
        
        img = Image.new('RGBA', (32, 32), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        verde_principal = (76, 175, 80)
        verde_brilhante = (0, 230, 118)
        azul_ciano = (0, 188, 212)
        azul_brilhante = (0, 229, 255)
        
        draw.rectangle([10, 4, 22, 20], outline=verde_principal, fill=verde_principal, width=1)
        draw.rectangle([6, 10, 10, 12], outline=verde_brilhante, fill=verde_brilhante)
        draw.rectangle([22, 14, 26, 16], outline=verde_brilhante, fill=verde_brilhante)
        draw.rectangle([13, 10, 19, 14], outline=azul_brilhante, fill=azul_ciano)
        draw.ellipse([5, 9, 7, 11], outline=azul_brilhante, fill=azul_brilhante)
        draw.ellipse([25, 13, 27, 15], outline=azul_brilhante, fill=azul_brilhante)
        
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.ico')
        img.save(temp_file.name, format='ICO', sizes=[(32, 32)])
        temp_file.close()
        
        return temp_file.name
    except ImportError:
        return None
    except Exception:
        return None


def aplicar_icone_cacto(janela):
    """Aplica o ícone de cacto na janela."""
    try:
        icon_path = criar_icone_cacto()
        if icon_path and os.path.exists(icon_path):
            janela.iconbitmap(icon_path)
    except Exception:
        pass


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
                   entry_estoque_min, tree, janela=None):
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
    
    # Garantir que a janela de cadastro fique em primeiro plano e com foco
    if janela:
        janela.lift()
        janela.focus_force()
        janela.attributes('-topmost', True)
        janela.after(100, lambda: janela.attributes('-topmost', False))
    
    # Colocar foco no campo de código de barras para facilitar cadastro consecutivo
    entry_codigo.focus_set()


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
    janela.geometry("1000x650")
    janela.configure(bg="#1a237e")
    
    # Aplicar ícone de cacto
    aplicar_icone_cacto(janela)

    # --------- TOPO: FORMULÁRIO ---------
    frame_form = tk.Frame(janela, bg="#283593")
    frame_form.pack(fill="x", padx=15, pady=15)

    tk.Label(
        frame_form, 
        text="Código de Barras:", 
        bg="#283593",
        fg="white",
        font=("Arial", 11, "bold")
    ).grid(row=0, column=0, sticky="w", pady=8)
    entry_codigo = tk.Entry(frame_form, width=35, font=("Arial", 11), bg="white", fg="black")
    entry_codigo.grid(row=0, column=1, padx=10, pady=8, sticky="w")

    tk.Label(
        frame_form, 
        text="Nome do Produto:", 
        bg="#283593",
        fg="white",
        font=("Arial", 11, "bold")
    ).grid(row=1, column=0, sticky="w", pady=8)
    entry_nome = tk.Entry(frame_form, width=55, font=("Arial", 11), bg="white", fg="black")
    entry_nome.grid(row=1, column=1, padx=10, pady=8, columnspan=2, sticky="w")

    tk.Label(
        frame_form, 
        text="Preço de Venda (R$):", 
        bg="#283593",
        fg="white",
        font=("Arial", 11, "bold")
    ).grid(row=2, column=0, sticky="w", pady=8)
    entry_preco_venda = tk.Entry(frame_form, width=18, font=("Arial", 11), bg="white", fg="black")
    entry_preco_venda.grid(row=2, column=1, padx=10, pady=8, sticky="w")

    tk.Label(
        frame_form, 
        text="Preço de Custo (R$):", 
        bg="#283593",
        fg="white",
        font=("Arial", 11, "bold")
    ).grid(row=3, column=0, sticky="w", pady=8)
    entry_preco_custo = tk.Entry(frame_form, width=18, font=("Arial", 11), bg="white", fg="black")
    entry_preco_custo.grid(row=3, column=1, padx=10, pady=8, sticky="w")

    tk.Label(
        frame_form, 
        text="Qtd para somar ao estoque:", 
        bg="#283593",
        fg="white",
        font=("Arial", 11, "bold")
    ).grid(row=4, column=0, sticky="w", pady=8)
    entry_estoque_somar = tk.Entry(frame_form, width=18, font=("Arial", 11), bg="white", fg="black")
    entry_estoque_somar.grid(row=4, column=1, padx=10, pady=8, sticky="w")

    tk.Label(
        frame_form, 
        text="Estoque Mínimo:", 
        bg="#283593",
        fg="white",
        font=("Arial", 11, "bold")
    ).grid(row=5, column=0, sticky="w", pady=8)
    entry_estoque_min = tk.Entry(frame_form, width=18, font=("Arial", 11), bg="white", fg="black")
    entry_estoque_min.grid(row=5, column=1, padx=10, pady=8, sticky="w")

    # Botão salvar
    btn_salvar = tk.Button(
        frame_form,
        text="💾 Salvar / Atualizar",
        bg="#00E676",
        fg="white",
        font=("Arial", 12, "bold"),
        relief="raised",
        bd=2,
        padx=20,
        pady=8,
        cursor="hand2",
        activebackground="#4CAF50",
        command=lambda: salvar_produto(
            entry_codigo,
            entry_nome,
            entry_preco_venda,
            entry_preco_custo,
            entry_estoque_somar,
            entry_estoque_min,
            tree,
            janela,
        ),
    )
    btn_salvar.grid(row=6, column=1, pady=15, sticky="w", padx=10)

    # --------- TABELA ---------
    frame_tab = tk.Frame(janela, bg="#283593")
    frame_tab.pack(fill="both", expand=True, padx=15, pady=10)

    colunas = ("codigo", "nome", "preco_venda", "preco_custo", "estoque")
    tree = ttk.Treeview(frame_tab, columns=colunas, show="headings", height=12)
    
    # Configurar estilo da tabela
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("Treeview", font=("Arial", 10), background="white", foreground="black", fieldbackground="white")
    style.configure("Treeview.Heading", font=("Arial", 11, "bold"), background="#3949ab", foreground="white")
    style.map("Treeview.Heading", background=[("active", "#5c6bc0")])
    
    tree.heading("codigo", text="Código de Barras")
    tree.heading("nome", text="Nome")
    tree.heading("preco_venda", text="Preço Venda")
    tree.heading("preco_custo", text="Custo")
    tree.heading("estoque", text="Estoque")

    tree.column("codigo", width=160)
    tree.column("nome", width=350)
    tree.column("preco_venda", width=130, anchor="e")
    tree.column("preco_custo", width=130, anchor="e")
    tree.column("estoque", width=100, anchor="center")

    tree.pack(side="left", fill="both", expand=True)

    scrollbar = ttk.Scrollbar(frame_tab, orient="vertical", command=tree.yview)
    scrollbar.pack(side="right", fill="y")
    tree.configure(yscrollcommand=scrollbar.set)

    # --------- BOTÕES INFERIORES ---------
    frame_btn = tk.Frame(janela, bg="#283593")
    frame_btn.pack(fill="x", padx=15, pady=15)

    btn_recarregar = tk.Button(
        frame_btn,
        text="🔄 Recarregar",
        command=lambda: carregar_produtos(tree),
        font=("Arial", 11, "bold"),
        relief="raised",
        bd=2,
        padx=15,
        pady=8,
        cursor="hand2"
    )
    btn_recarregar.pack(side="left", padx=5)

    btn_deletar = tk.Button(
        frame_btn,
        text="🗑️ Excluir Produto Selecionado",
        bg="#f44336",
        fg="white",
        font=("Arial", 11, "bold"),
        relief="raised",
        bd=2,
        padx=15,
        pady=8,
        cursor="hand2",
        command=lambda: deletar_produto(tree),
    )
    btn_deletar.pack(side="right", padx=5)

    # Carregar produtos ao abrir
    carregar_produtos(tree)
    
    # Focar no campo de código de barras ao abrir a janela
    entry_codigo.focus_set()

    # Se estiver rodando sozinho, precisa de mainloop
    if parent is None:
        janela.mainloop()


if __name__ == "__main__":
    abrir_cadastro_produtos()
