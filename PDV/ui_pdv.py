import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import pdv_functions as pf
from cadastro_produtos import abrir_cadastro_produtos
from relatorios import abrir_relatorio_caixa_dia
from etiquetas import abrir_etiquetas
import os
import tempfile


def criar_icone_cacto():
    """Cria um ícone de cacto e retorna o caminho do arquivo temporário."""
    try:
        from PIL import Image, ImageDraw
        
        # Criar imagem 32x32 para o ícone
        img = Image.new('RGBA', (32, 32), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Cores da marca
        verde_principal = (76, 175, 80)  # #4CAF50
        verde_brilhante = (0, 230, 118)  # #00E676
        azul_ciano = (0, 188, 212)  # #00BCD4
        azul_brilhante = (0, 229, 255)  # #00E5FF
        
        # Corpo principal do cacto (retângulo vertical)
        draw.rectangle([10, 4, 22, 20], outline=verde_principal, fill=verde_principal, width=1)
        
        # Braço esquerdo
        draw.rectangle([6, 10, 10, 12], outline=verde_brilhante, fill=verde_brilhante)
        
        # Braço direito
        draw.rectangle([22, 14, 26, 16], outline=verde_brilhante, fill=verde_brilhante)
        
        # Chip central (coração do cacto)
        draw.rectangle([13, 10, 19, 14], outline=azul_brilhante, fill=azul_ciano)
        
        # Pontos de conexão
        draw.ellipse([5, 9, 7, 11], outline=azul_brilhante, fill=azul_brilhante)
        draw.ellipse([25, 13, 27, 15], outline=azul_brilhante, fill=azul_brilhante)
        
        # Salvar como arquivo temporário .ico
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.ico')
        img.save(temp_file.name, format='ICO', sizes=[(32, 32)])
        temp_file.close()
        
        return temp_file.name
    except ImportError:
        # Se PIL não estiver disponível, retorna None
        return None
    except Exception:
        return None


def aplicar_icone_cacto(janela):
    """Aplica o ícone de cacto na janela."""
    try:
        icon_path = criar_icone_cacto()
        if icon_path and os.path.exists(icon_path):
            janela.iconbitmap(icon_path)
            # Não deletar o arquivo imediatamente, deixar para o sistema limpar
    except Exception:
        pass  # Se falhar, apenas ignora


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
    janela.geometry("1000x700")
    janela.configure(bg="#1a237e")
    
    # Aplicar ícone de cacto
    aplicar_icone_cacto(janela)

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
    topo = tk.Frame(janela, bg="#283593")
    topo.pack(fill="x", padx=15, pady=15)

    tk.Label(
        topo, 
        text="Código de Barras:", 
        bg="#283593",
        fg="white",
        font=("Arial", 11, "bold")
    ).pack(side="left", padx=5)
    entry_codigo = tk.Entry(topo, width=25, font=("Arial", 11), bg="white", fg="black")
    entry_codigo.pack(side="left", padx=8)

    # foco inicial no campo de código (para uso com bip)
    entry_codigo.focus_set()

    tk.Label(
        topo, 
        text="Qtd:", 
        bg="#283593",
        fg="white",
        font=("Arial", 11, "bold")
    ).pack(side="left", padx=10)
    entry_qtd = tk.Entry(topo, width=8, font=("Arial", 11), bg="white", fg="black")
    entry_qtd.insert(0, "1")
    entry_qtd.pack(side="left", padx=8)

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

        # Verificar estoque disponível (se houver controle)
        estoque = produto.get("estoque")
        if estoque is not None:
            # Somar o que já está no carrinho desse mesmo produto
            qtd_no_carrinho = sum(
                item["quantidade"] for item in LISTA_ITENS if item["codigo"] == codigo
            )
            if qtd + qtd_no_carrinho > estoque:
                messagebox.showerror(
                    "Estoque insuficiente",
                    f"Estoque disponível: {estoque:.2f}\n"
                    f"Quantidade no carrinho: {qtd_no_carrinho:.2f}\n"
                    f"Tentando adicionar: {qtd:.2f}",
                )
                return

        item = {
            "codigo": codigo,
            "descricao": produto["nome"],
            "quantidade": qtd,
            "preco_unit": produto["preco"],   # venda
            "custo_unit": produto["custo"],   # custo
            "subtotal": produto["preco"] * qtd,
        }

        pf.adicionar_item(LISTA_ITENS, item)
        atualizar_tabela(tree, label_total)

        # limpa o campo de código e volta o foco pra ele (ideal para bip em sequência)
        entry_codigo.delete(0, tk.END)
        entry_codigo.focus_set()


    btn_add = tk.Button(
        topo,
        text="➕ Adicionar",
        command=on_adicionar,
        bg="#00E676",
        fg="white",
        font=("Arial", 11, "bold"),
        relief="raised",
        bd=2,
        padx=15,
        pady=5,
        cursor="hand2",
        activebackground="#4CAF50"
    )
    btn_add.pack(side="left", padx=12)

    # ENTER no campo de código adiciona o item (modo bip)
    entry_codigo.bind("<Return>", lambda event: on_adicionar())

    # --------- TABELA ---------
    frame_tabela = tk.Frame(janela, bg="#283593")
    frame_tabela.pack(fill="both", expand=True, padx=15, pady=10)
    
    colunas = ("codigo", "descricao", "qtd", "preco_unit", "subtotal")
    tree = ttk.Treeview(frame_tabela, columns=colunas, show="headings", height=18)

    # Configurar estilo da tabela
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("Treeview", font=("Arial", 10), background="white", foreground="black", fieldbackground="white")
    style.configure("Treeview.Heading", font=("Arial", 11, "bold"), background="#3949ab", foreground="white")
    style.map("Treeview.Heading", background=[("active", "#5c6bc0")])

    tree.heading("codigo", text="Código")
    tree.heading("descricao", text="Descrição")
    tree.heading("qtd", text="Qtd")
    tree.heading("preco_unit", text="Preço Unit.")
    tree.heading("subtotal", text="Subtotal")

    tree.column("codigo", width=150)
    tree.column("descricao", width=350)
    tree.column("qtd", width=100, anchor="center")
    tree.column("preco_unit", width=150, anchor="e")
    tree.column("subtotal", width=150, anchor="e")

    tree.pack(side="left", fill="both", expand=True)
    
    scrollbar = ttk.Scrollbar(frame_tabela, orient="vertical", command=tree.yview)
    scrollbar.pack(side="right", fill="y")
    tree.configure(yscrollcommand=scrollbar.set)

    # --------- TOTAL ---------
    frame_total = tk.Frame(janela, bg="#3949ab", relief="raised", bd=3)
    frame_total.pack(fill="x", padx=15, pady=10)
    
    label_total = tk.Label(
        frame_total,
        text="TOTAL: R$ 0.00",
        font=("Arial", 22, "bold"),
        bg="#3949ab",
        fg="white"
    )
    label_total.pack(pady=12)

    # --------- BOTÕES INFERIORES ---------
    footer = tk.Frame(janela, bg="#283593")
    footer.pack(fill="x", pady=15, padx=15)

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
        text="🗑️ Remover Item",
        command=on_remover,
        bg="#f44336",
        fg="white",
        font=("Arial", 11, "bold"),
        relief="raised",
        bd=2,
        padx=15,
        pady=8,
        cursor="hand2"
    )
    btn_rem.pack(side="left", padx=5)

    btn_clear = tk.Button(
        footer,
        text="🧹 Limpar",
        command=on_limpar,
        bg="#555555",
        fg="white",
        font=("Arial", 11, "bold"),
        relief="raised",
        bd=2,
        padx=15,
        pady=8,
        cursor="hand2"
    )
    btn_clear.pack(side="left", padx=10)

    btn_fin = tk.Button(
        footer,
        text="✅ Finalizar Venda",
        command=on_finalizar,
        bg="#00BCD4",
        fg="white",
        font=("Arial", 13, "bold"),
        relief="raised",
        bd=3,
        padx=25,
        pady=10,
        cursor="hand2",
        activebackground="#00E5FF"
    )
    btn_fin.pack(side="right", padx=5)

    # Atalho: F2 volta o foco para o campo de código (ajuda no caixa)
    def focar_codigo(event=None):
        entry_codigo.focus_set()

    janela.bind("<F2>", focar_codigo)
