import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import pdv_functions as pf
from cadastro_produtos import abrir_cadastro_produtos
from relatorios import abrir_relatorio_caixa_dia
from etiquetas import abrir_etiquetas

# Lista global da venda
LISTA_ITENS = []


def atualizar_tabela(tree, label_total):
    """Atualiza a tabela de itens e o total."""
    # Limpar tabela
    for item in tree.get_children():
        tree.delete(item)

    # Preencher tabela
    for i, item in enumerate(LISTA_ITENS):
        tree.insert(
            "",
            "end",
            iid=str(i),
            values=(
                item["codigo"],
                item["descricao"],
                f"{item['quantidade']:.2f}",
                f"R$ {item['preco_unit']:.2f}",
                f"R$ {item['subtotal']:.2f}",
            ),
        )

    total = pf.calcular_total(LISTA_ITENS)
    label_total.config(text=f"TOTAL: R$ {total:.2f}")


def criar_interface_pdv(janela):

    janela.title("Mandacaru TEC – PDV")
    janela.geometry("900x600")
    janela.configure(bg="#f7f7f7")

    # ========= FUNÇÕES DE MENU =========

    def abrir_cadastro_produtos_menu():
        """Abre o cadastro de produtos a partir do menu."""
        try:
            abrir_cadastro_produtos(janela)
        except TypeError:
            # Caso a função não aceite parent
            abrir_cadastro_produtos()
        except Exception as e:
            messagebox.showerror(
                "Erro",
                f"Erro ao abrir o Cadastro de Produtos:\n{e}"
            )

    def abrir_relatorio_caixa_dia_menu():
        """Abre o relatório de caixa do dia."""
        try:
            abrir_relatorio_caixa_dia(janela)
        except Exception as e:
            messagebox.showerror(
                "Erro",
                f"Erro ao abrir o Relatório de Caixa do Dia:\n{e}"
            )

    def abrir_etiquetas_menu():
        """Abre a tela de etiquetas."""
        try:
            abrir_etiquetas(janela)
        except Exception as e:
            messagebox.showerror(
                "Erro",
                f"Erro ao abrir o módulo de Etiquetas:\n{e}"
            )

    def em_breve():
        messagebox.showinfo(
            "Em breve",
            "Esta funcionalidade será implementada nas próximas versões do Mandacaru TEC."
        )

    # ========= MENU SUPERIOR =========
    menu_bar = tk.Menu(janela)

    # Menu PDV
    menu_pdv = tk.Menu(menu_bar, tearoff=0)
    menu_pdv.add_command(label="Tela de Vendas", command=lambda: None)
    menu_bar.add_cascade(label="PDV", menu=menu_pdv)

    # Menu Produtos
    menu_prod = tk.Menu(menu_bar, tearoff=0)
    menu_prod.add_command(
        label="Cadastro de Produtos",
        command=abrir_cadastro_produtos_menu
    )
    menu_prod.add_command(
        label="Gerar Etiquetas",
        command=abrir_etiquetas_menu
    )
    menu_bar.add_cascade(label="Produtos", menu=menu_prod)

    # Menu Relatórios
    menu_rel = tk.Menu(menu_bar, tearoff=0)
    menu_rel.add_command(
        label="Relatório de Caixa (Dia)",
        command=abrir_relatorio_caixa_dia_menu
    )
    menu_bar.add_cascade(label="Relatórios", menu=menu_rel)

    # Menu Configurações (para o futuro)
    menu_conf = tk.Menu(menu_bar, tearoff=0)
    menu_conf.add_command(label="Configurações do Sistema", command=em_breve)
    menu_bar.add_cascade(label="Configurações", menu=menu_conf)

    janela.config(menu=menu_bar)

    # --------- TOPO: CAMPOS DE VENDA ---------
    topo = tk.Frame(janela, bg="#f7f7f7")
    topo.pack(fill="x", padx=10, pady=10)

    tk.Label(topo, text="Código de Barras:", bg="#f7f7f7").pack(side="left")
    entry_codigo = tk.Entry(topo, width=20)
    entry_codigo.pack(side="left", padx=5)

    tk.Label(topo, text="Qtd:", bg="#f7f7f7").pack(side="left")
    entry_qtd = tk.Entry(topo, width=5)
    entry_qtd.insert(0, "1")
    entry_qtd.pack(side="left", padx=5)

    def on_adicionar():
        codigo = entry_codigo.get().strip()
        qtd_str = entry_qtd.get().strip()

        if not codigo:
            messagebox.showwarning("Aviso", "Digite um código de barras.")
            return

        try:
            qtd = float(qtd_str.replace(",", "."))
        except Exception:
            messagebox.showwarning("Erro", "Quantidade inválida.")
            return

        produto = pf.buscar_produto_por_codigo(codigo)

        if not produto:
            messagebox.showerror("Erro", "Produto não encontrado no cadastro.")
            return

        item = {
            "codigo": codigo,
            "descricao": produto["nome"],
            "quantidade": qtd,
            "preco_unit": produto["preco"],
            "subtotal": produto["preco"] * qtd,
        }

        pf.adicionar_item(LISTA_ITENS, item)
        atualizar_tabela(tree, label_total)

        entry_codigo.delete(0, tk.END)

    btn_add = tk.Button(
        topo,
        text="Adicionar",
        command=on_adicionar,
        bg="#4CAF50",
        fg="white"
    )
    btn_add.pack(side="left", padx=8)

    # --------- TABELA ---------
    colunas = ("codigo", "descricao", "qtd", "preco_unit", "subtotal")
    tree = ttk.Treeview(janela, columns=colunas, show="headings", height=15)

    tree.heading("codigo", text="Código")
    tree.heading("descricao", text="Descrição")
    tree.heading("qtd", text="Qtd")
    tree.heading("preco_unit", text="Preço Unit.")
    tree.heading("subtotal", text="Subtotal")

    for col in colunas:
        tree.column(col, width=150)

    tree.pack(fill="both", expand=True, padx=10, pady=10)

    # --------- TOTAL ---------
    label_total = tk.Label(
        janela,
        text="TOTAL: R$ 0.00",
        font=("Arial", 16, "bold"),
        bg="#f7f7f7"
    )
    label_total.pack(pady=5)

    # --------- BOTÕES INFERIORES ---------
    footer = tk.Frame(janela, bg="#f7f7f7")
    footer.pack(fill="x", pady=10, padx=10)

    def on_remover():
        item_selecionado = tree.selection()
        if not item_selecionado:
            messagebox.showwarning("Aviso", "Nenhum item selecionado.")
            return

        idx = int(item_selecionado[0])
        pf.remover_item(LISTA_ITENS, idx)
        atualizar_tabela(tree, label_total)

    def on_limpar():
        pf.limpar_carrinho(LISTA_ITENS)
        atualizar_tabela(tree, label_total)

    def on_finalizar():
        if not LISTA_ITENS:
            messagebox.showwarning("Aviso", "Nenhum item na venda.")
            return

        resposta = messagebox.askquestion(
            "Forma de Pagamento",
            "Pagamento em DINHEIRO?\n\nSim = Dinheiro\nNão = PIX",
            icon="question"
        )

        if resposta == "yes":
            forma = "Dinheiro"
            total = pf.calcular_total(LISTA_ITENS)
            valor_str = simpledialog.askstring(
                "Valor Recebido",
                f"Total: R$ {total:.2f}\n\nInforme o valor recebido em dinheiro:"
            )
            if not valor_str:
                return
            try:
                valor_recebido = float(valor_str.replace(",", "."))
            except Exception:
                messagebox.showerror("Erro", "Valor recebido inválido.")
                return
        else:
            forma = "PIX"
            valor_recebido = pf.calcular_total(LISTA_ITENS)

        try:
            resumo = pf.finalizar_venda(LISTA_ITENS, forma, valor_recebido)
        except Exception as e:
            messagebox.showerror("Erro", str(e))
            return

        pf.exibir_resumo_venda(resumo)
        pf.limpar_carrinho(LISTA_ITENS)
        atualizar_tabela(tree, label_total)

    btn_rem = tk.Button(
        footer,
        text="Remover Item",
        command=on_remover,
        bg="#f44336",
        fg="white"
    )
    btn_rem.pack(side="left")

    btn_clear = tk.Button(
        footer,
        text="Limpar",
        command=on_limpar,
        bg="#555555",
        fg="white"
    )
    btn_clear.pack(side="left", padx=10)

    btn_fin = tk.Button(
        footer,
        text="Finalizar Venda",
        command=on_finalizar,
        bg="#2196F3",
        fg="white"
    )
    btn_fin.pack(side="right")
