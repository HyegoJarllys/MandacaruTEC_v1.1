import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox

import pdv_functions as pf
from cadastro_produtos import abrir_cadastro_produtos
from relatorios import abrir_relatorio_caixa_dia
<<<<<<< HEAD
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

=======
from config_empresa import abrir_config_empresa
from cupom import gerar_cupom, gerar_qrcode_pix
>>>>>>> 2a8eb57eeecf608a6a2004611831a41f917b38e4

# Lista global de itens da venda
LISTA_ITENS = []


# ============================================================
# ESTILO DARK PREMIUM
# ============================================================
def configurar_tema_escuro(root: tk.Tk):
    """
    Configura um tema escuro estilo 'Black Premium'
    para Treeview, botões e labels.
    """
    root.configure(bg="#121212")

    style = ttk.Style(root)
    # Usa um tema que permita customização
    try:
        style.theme_use("clam")
    except Exception:
        pass

    # Treeview dark
    style.configure(
        "Treeview",
        background="#1E1E1E",
        foreground="#FFFFFF",
        fieldbackground="#1E1E1E",
        rowheight=26,
        borderwidth=0,
    )
    style.map(
        "Treeview",
        background=[("selected", "#2D89EF")],
        foreground=[("selected", "#FFFFFF")],
    )

    style.configure(
        "Treeview.Heading",
        background="#222222",
        foreground="#FFFFFF",
        relief="flat",
        font=("Segoe UI", 9, "bold"),
    )

    # Botões "flat" escuros
    style.configure(
        "TButton",
        font=("Segoe UI", 9),
        padding=6,
    )


def format_money(valor: float) -> str:
    return f"R$ {valor:.2f}".replace(".", ",")


# ============================================================
# ATUALIZAR TABELA / TOTAL
# ============================================================
def atualizar_tabela(tree, label_total):
    """Atualiza tabela e total do carrinho."""
    for item in tree.get_children():
        tree.delete(item)

    for i, item in enumerate(LISTA_ITENS):
        tree.insert(
            "",
            "end",
            iid=str(i),
            values=(
                item["codigo"],
                item["descricao"],
                f"{item['quantidade']}",
                format_money(item["preco_unit"]),
                format_money(item["subtotal"]),
            ),
        )

    total = pf.calcular_total(LISTA_ITENS)
    label_total.config(text=f"TOTAL: {format_money(total)}")


# ============================================================
# CLASSE PRINCIPAL DO PDV
# ============================================================
class PDVApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Mandacaru TEC – PDV")
        self.root.geometry("1024x680")
        self.root.minsize(900, 600)

<<<<<<< HEAD
    janela.title("Mandacaru TEC – PDV")
    janela.geometry("1000x700")
    janela.configure(bg="#1a237e")
    
    # Aplicar ícone de cacto
    aplicar_icone_cacto(janela)
=======
        configurar_tema_escuro(self.root)
>>>>>>> 2a8eb57eeecf608a6a2004611831a41f917b38e4

        self.entry_codigo = None
        self.entry_qtd = None
        self.tree = None
        self.label_total = None

        self._criar_layout()
        self._criar_menu()
        self._configurar_binds()

        atualizar_tabela(self.tree, self.label_total)

    # --------------------------------------------------------
    # LAYOUT PRINCIPAL
    # --------------------------------------------------------
    def _criar_layout(self):
        # CABEÇALHO SUPERIOR
        frame_header = tk.Frame(self.root, bg="#181818", height=60)
        frame_header.pack(fill="x", side="top")

        lbl_logo = tk.Label(
            frame_header,
            text="Mandacaru TEC",
            bg="#181818",
            fg="#00E5FF",
            font=("Segoe UI Semibold", 16, "bold"),
        )
        lbl_logo.pack(side="left", padx=15, pady=10)

        lbl_sub = tk.Label(
            frame_header,
            text="PDV Black Premium",
            bg="#181818",
            fg="#BBBBBB",
            font=("Segoe UI", 10),
        )
        lbl_sub.pack(side="left", pady=10)

        self.label_total = tk.Label(
            frame_header,
            text="TOTAL: R$ 0,00",
            bg="#181818",
            fg="#4CAF50",
            font=("Segoe UI", 18, "bold"),
        )
        self.label_total.pack(side="right", padx=20)

        # CONTEÚDO PRINCIPAL (ESQUERDA: PDV / DIREITA: ATALHOS)
        frame_main = tk.Frame(self.root, bg="#121212")
        frame_main.pack(fill="both", expand=True)

        frame_left = tk.Frame(frame_main, bg="#121212")
        frame_left.pack(side="left", fill="both", expand=True, padx=(10, 5), pady=10)

        frame_right = tk.Frame(frame_main, bg="#181818", width=200)
        frame_right.pack(side="right", fill="y", padx=(5, 10), pady=10)

        # ----------- TOPO ESQUERDO: CAMPOS DE ENTRADA --------------
        frame_top = tk.Frame(frame_left, bg="#121212")
        frame_top.pack(fill="x", pady=(0, 10))

        tk.Label(
            frame_top,
            text="CÓDIGO",
            bg="#121212",
            fg="#FFFFFF",
            font=("Segoe UI", 9, "bold"),
        ).pack(side="left", padx=(0, 5))
        self.entry_codigo = tk.Entry(
            frame_top,
            width=26,
            font=("Consolas", 11),
            bg="#1E1E1E",
            fg="#FFFFFF",
            insertbackground="#FFFFFF",
            relief="flat",
        )
        self.entry_codigo.pack(side="left")
        self.entry_codigo.focus()

        tk.Label(
            frame_top,
            text="QTD",
            bg="#121212",
            fg="#FFFFFF",
            font=("Segoe UI", 9, "bold"),
        ).pack(side="left", padx=(15, 5))
        self.entry_qtd = tk.Entry(
            frame_top,
            width=5,
            font=("Consolas", 11),
            bg="#1E1E1E",
            fg="#FFFFFF",
            insertbackground="#FFFFFF",
            relief="flat",
        )
        self.entry_qtd.insert(0, "1")
        self.entry_qtd.pack(side="left")

        btn_add = tk.Button(
            frame_top,
            text="ADICIONAR (F2)",
            bg="#00C853",
            fg="#FFFFFF",
            font=("Segoe UI", 9, "bold"),
            relief="flat",
            padx=15,
            pady=4,
            command=self._adicionar_item_ui,
        )
        btn_add.pack(side="left", padx=(20, 0))

        # ----------- TABELA (TREEVIEW) --------------
        frame_table = tk.Frame(frame_left, bg="#121212")
        frame_table.pack(fill="both", expand=True)

        colunas = ("codigo", "descricao", "qtd", "unit", "sub")
        self.tree = ttk.Treeview(
            frame_table, columns=colunas, show="headings", height=18
        )
        self.tree.pack(side="left", fill="both", expand=True)

        self.tree.heading("codigo", text="CÓDIGO")
        self.tree.heading("descricao", text="DESCRIÇÃO")
        self.tree.heading("qtd", text="QTD")
        self.tree.heading("unit", text="UNITÁRIO")
        self.tree.heading("sub", text="SUBTOTAL")

        self.tree.column("codigo", width=120, anchor="w")
        self.tree.column("descricao", width=420, anchor="w")
        self.tree.column("qtd", width=60, anchor="e")
        self.tree.column("unit", width=90, anchor="e")
        self.tree.column("sub", width=110, anchor="e")

        scroll = ttk.Scrollbar(
            frame_table, orient="vertical", command=self.tree.yview
        )
        self.tree.configure(yscroll=scroll.set)
        scroll.pack(side="right", fill="y")

        # ----------- BARRA INFERIOR DE BOTÕES --------------
        frame_bottom = tk.Frame(frame_left, bg="#121212")
        frame_bottom.pack(fill="x", pady=(10, 0))

        def make_btn(text, bg, command, side="left"):
            return tk.Button(
                frame_bottom,
                text=text,
                bg=bg,
                fg="#FFFFFF",
                font=("Segoe UI", 9, "bold"),
                relief="flat",
                padx=18,
                pady=6,
                command=command,
            ).pack(side=side, padx=5)

        make_btn("REMOVER ITEM (Del)", "#E53935", self._remover_item_ui)
        make_btn("LIMPAR CARRINHO (F4)", "#424242", self._limpar)
        make_btn("FINALIZAR VENDA (F5)", "#1976D2", self._abrir_tela_pagamento, "right")
        make_btn("FECHAR (ESC)", "#757575", self.root.destroy, "right")

        # ----------- PAINEL DIREITO: ATALHOS / STATUS --------------
        tk.Label(
            frame_right,
            text="ATALHOS",
            bg="#181818",
            fg="#FFFFFF",
            font=("Segoe UI", 10, "bold"),
        ).pack(anchor="w", padx=10, pady=(5, 0))

        atalhos = [
            ("F2", "Adicionar item"),
            ("Del", "Remover item"),
            ("F4", "Limpar carrinho"),
            ("F5", "Finalizar venda"),
            ("ESC", "Fechar PDV"),
        ]

        for tecla, desc in atalhos:
            linha = tk.Frame(frame_right, bg="#181818")
            linha.pack(anchor="w", padx=10, pady=3, fill="x")

            lbl_key = tk.Label(
                linha,
                text=tecla,
                bg="#2D2D2D",
                fg="#FFFFFF",
                font=("Segoe UI", 8, "bold"),
                padx=6,
                pady=2,
            )
            lbl_key.pack(side="left")

            lbl_desc = tk.Label(
                linha,
                text=desc,
                bg="#181818",
                fg="#BBBBBB",
                font=("Segoe UI", 9),
            )
            lbl_desc.pack(side="left", padx=6)

        # Espaço
        tk.Label(frame_right, bg="#181818").pack(fill="x", pady=10)

        # Ações rápidas
        tk.Label(
            frame_right,
            text="AÇÕES RÁPIDAS",
            bg="#181818",
            fg="#FFFFFF",
            font=("Segoe UI", 10, "bold"),
        ).pack(anchor="w", padx=10)

        def make_side_btn(text, cmd):
            tk.Button(
                frame_right,
                text=text,
                bg="#263238",
                fg="#FFFFFF",
                font=("Segoe UI", 9),
                relief="flat",
                anchor="w",
                padx=10,
                pady=4,
                command=cmd,
            ).pack(fill="x", padx=10, pady=3)

        make_side_btn("Cadastro de Produtos", lambda: abrir_cadastro_produtos(self.root))
        make_side_btn("Modo Etiquetas", self._abrir_modo_etiquetas)
        make_side_btn(
            "Relatório Caixa (Dia)",
            lambda: abrir_relatorio_caixa_dia(self.root),
        )
        make_side_btn(
            "Config. da Empresa",
            lambda: abrir_config_empresa(self.root),
        )

    # --------------------------------------------------------
    # MENU SUPERIOR
    # --------------------------------------------------------
    def _criar_menu(self):
        menu_bar = tk.Menu(self.root)

        menu_pdv = tk.Menu(menu_bar, tearoff=0)
        menu_pdv.add_command(label="Tela de Vendas")
        menu_bar.add_cascade(label="PDV", menu=menu_pdv)

        menu_prod = tk.Menu(menu_bar, tearoff=0)
        menu_prod.add_command(label="Cadastro de Produtos", command=lambda: abrir_cadastro_produtos(self.root))
        menu_prod.add_command(label="Modo Etiquetas", command=self._abrir_modo_etiquetas)
        menu_bar.add_cascade(label="Produtos", menu=menu_prod)

        menu_rel = tk.Menu(menu_bar, tearoff=0)
        menu_rel.add_command(
            label="Relatório de Caixa (Dia)",
            command=lambda: abrir_relatorio_caixa_dia(self.root),
        )
        menu_bar.add_cascade(label="Relatórios", menu=menu_rel)

        menu_conf = tk.Menu(menu_bar, tearoff=0)
        menu_conf.add_command(
            label="Configurações da Empresa",
            command=lambda: abrir_config_empresa(self.root),
        )
        menu_bar.add_cascade(label="Configurações", menu=menu_conf)

        self.root.config(menu=menu_bar)

<<<<<<< HEAD
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
=======
    # --------------------------------------------------------
    # BINDS
    # --------------------------------------------------------
    def _configurar_binds(self):
        self.entry_codigo.bind("<Return>", lambda e: self._adicionar_item_ui())
        self.entry_qtd.bind("<Return>", lambda e: self._adicionar_item_ui())

        self.root.bind("<F2>", lambda e: self._adicionar_item_ui())
        self.root.bind("<Delete>", lambda e: self._remover_item_ui())
        self.root.bind("<F4>", lambda e: self._limpar())
        self.root.bind("<F5>", lambda e: self._abrir_tela_pagamento())
        self.root.bind("<Escape>", lambda e: self.root.destroy())
>>>>>>> 2a8eb57eeecf608a6a2004611831a41f917b38e4

    # --------------------------------------------------------
    # FUNÇÕES DO PDV
    # --------------------------------------------------------
    def _adicionar_item_ui(self):
        codigo = self.entry_codigo.get().strip()
        if not codigo:
            messagebox.showwarning("Atenção", "Informe o código.")
            return

        qtd_txt = self.entry_qtd.get().strip() or "1"
        try:
            qtd = int(qtd_txt)
        except ValueError:
            messagebox.showerror("Erro", "Quantidade inválida.")
            return

        resultado = pf.adicionar_item(LISTA_ITENS, codigo, qtd)

        if isinstance(resultado, dict) and resultado.get("erro"):
            messagebox.showerror("Erro", resultado["erro"])
            return

        atualizar_tabela(self.tree, self.label_total)

        self.entry_codigo.delete(0, tk.END)
        self.entry_qtd.delete(0, tk.END)
        self.entry_qtd.insert(0, "1")
        self.entry_codigo.focus()

<<<<<<< HEAD
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
=======
    def _remover_item_ui(self):
        item_sel = self.tree.focus()
        if not item_sel:
>>>>>>> 2a8eb57eeecf608a6a2004611831a41f917b38e4
            return

        index = self.tree.index(item_sel)
        pf.remover_item(LISTA_ITENS, index)
        atualizar_tabela(self.tree, self.label_total)

    def _limpar(self):
        LISTA_ITENS.clear()
        atualizar_tabela(self.tree, self.label_total)

    # =======================================================
    # TELA DE PAGAMENTO BLACK PREMIUM
    # =======================================================
    def _abrir_tela_pagamento(self):
        if not LISTA_ITENS:
            messagebox.showwarning("Atenção", "Não há itens no carrinho.")
            return

        total = pf.calcular_total(LISTA_ITENS)

        janela = tk.Toplevel(self.root)
        janela.title("Pagamento")
        janela.geometry("520x460")
        janela.configure(bg="#121212")
        janela.grab_set()
        janela.focus_force()

        tk.Label(
            janela,
            text=f"TOTAL A PAGAR",
            bg="#121212",
            fg="#BBBBBB",
            font=("Segoe UI", 10),
        ).pack(pady=(15, 0))

        tk.Label(
            janela,
            text=format_money(total),
            bg="#121212",
            fg="#4CAF50",
            font=("Segoe UI", 24, "bold"),
        ).pack(pady=(0, 10))

        forma_var = tk.StringVar(value="")

        frame_botoes = tk.Frame(janela, bg="#121212")
        frame_botoes.pack(pady=10)

        frame_detalhes = tk.Frame(janela, bg="#121212")
        frame_detalhes.pack(fill="both", expand=True, padx=15, pady=10)

        janela.entry_valor = None
        janela.qr_label = None

        def limpar_detalhes():
            for w in frame_detalhes.winfo_children():
                w.destroy()
            janela.entry_valor = None
            janela.qr_label = None

        def selecionar_dinheiro():
            forma_var.set("DINHEIRO")
            limpar_detalhes()
            tk.Label(
                frame_detalhes,
                text="Pagamento em DINHEIRO",
                bg="#121212",
                fg="#FFFFFF",
                font=("Segoe UI", 11, "bold"),
            ).pack(anchor="w", pady=5)
            tk.Label(
                frame_detalhes,
                text="Valor recebido:",
                bg="#121212",
                fg="#CCCCCC",
            ).pack(anchor="w")
            entry = tk.Entry(
                frame_detalhes,
                width=15,
                font=("Consolas", 11),
                bg="#1E1E1E",
                fg="#FFFFFF",
                insertbackground="#FFFFFF",
                relief="flat",
            )
            entry.pack(anchor="w", pady=5)
            entry.insert(0, f"{total:.2f}")
            janela.entry_valor = entry
            entry.focus()

        def selecionar_pix():
            forma_var.set("PIX")
            limpar_detalhes()
            tk.Label(
                frame_detalhes,
                text="Pagamento via PIX",
                bg="#121212",
                fg="#FFFFFF",
                font=("Segoe UI", 11, "bold"),
            ).pack(anchor="w", pady=5)

            tk.Label(
                frame_detalhes,
                text="Mostre este QR Code ao cliente.\n"
                     "Se não aparecer, use a chave PIX no cupom.",
                bg="#121212",
                fg="#CCCCCC",
                justify="left",
            ).pack(anchor="w", pady=5)

            caminho_qr = gerar_qrcode_pix(total)

            if caminho_qr and os.path.isfile(caminho_qr):
                try:
                    img = tk.PhotoImage(file=caminho_qr)
                    lbl = tk.Label(frame_detalhes, image=img, bg="#121212")
                    lbl.image = img
                    lbl.pack(pady=5)
                    janela.qr_label = lbl
                except Exception as e:
                    tk.Label(
                        frame_detalhes,
                        text=f"Não foi possível exibir o QR Code.\n{e}",
                        bg="#121212",
                        fg="#FF5252",
                    ).pack(anchor="w", pady=5)
            else:
                tk.Label(
                    frame_detalhes,
                    text="QR Code não gerado.\n"
                         "Verifique chave PIX e biblioteca 'qrcode'.",
                    bg="#121212",
                    fg="#FF5252",
                ).pack(anchor="w", pady=5)

        def selecionar_cartao():
            forma_var.set("CARTÃO")
            limpar_detalhes()
            tk.Label(
                frame_detalhes,
                text="Pagamento no CARTÃO",
                bg="#121212",
                fg="#FFFFFF",
                font=("Segoe UI", 11, "bold"),
            ).pack(anchor="w", pady=5)
            tk.Label(
                frame_detalhes,
                text="Passe o cartão na maquininha\n"
                     "e clique em 'Confirmar Pagamento' após aprovação.",
                bg="#121212",
                fg="#CCCCCC",
                justify="left",
            ).pack(anchor="w", pady=5)

        btn_style = {
            "width": 12,
            "height": 2,
            "font": ("Segoe UI", 11, "bold"),
            "relief": "flat",
            "fg": "#FFFFFF",
            "padx": 8,
        }
        tk.Button(
            frame_botoes,
            text="DINHEIRO",
            bg="#FFC107",
            command=selecionar_dinheiro,
            **btn_style,
        ).grid(row=0, column=0, padx=5, pady=5)

        tk.Button(
            frame_botoes,
            text="PIX",
            bg="#00C853",
            command=selecionar_pix,
            **btn_style,
        ).grid(row=0, column=1, padx=5, pady=5)

        tk.Button(
            frame_botoes,
            text="CARTÃO",
            bg="#2962FF",
            command=selecionar_cartao,
            **btn_style,
        ).grid(row=0, column=2, padx=5, pady=5)

        # Botões confirmar / cancelar
        frame_bottom = tk.Frame(janela, bg="#121212")
        frame_bottom.pack(fill="x", pady=15)

        def confirmar_pagamento():
            forma = forma_var.get()
            if not forma:
                messagebox.showwarning("Atenção", "Selecione uma forma de pagamento.")
                return

            valor_recebido = None
            if forma == "DINHEIRO":
                entry = janela.entry_valor
                if not entry:
                    messagebox.showerror("Erro", "Campo de valor não encontrado.")
                    return
                valor_txt = entry.get().strip()
                if not valor_txt:
                    messagebox.showwarning("Atenção", "Informe o valor recebido.")
                    return
                try:
                    valor_recebido = float(valor_txt.replace(",", "."))
                except ValueError:
                    messagebox.showerror("Erro", "Valor recebido inválido.")
                    return

            resumo = pf.finalizar_venda(
                LISTA_ITENS,
                forma_pagamento=forma,
                valor_recebido=valor_recebido,
            )

            if resumo.get("erro"):
                messagebox.showerror("Erro", resumo["erro"])
                return

            pf.exibir_resumo_venda(resumo)

            try:
                gerar_cupom(resumo, "CLIENTE")
                gerar_cupom(resumo, "CAIXA")
            except Exception as e:
                messagebox.showerror(
                    "Erro Cupom",
                    f"A venda foi registrada, mas houve erro ao gerar o cupom:\n{e}",
                )

            LISTA_ITENS.clear()
            atualizar_tabela(self.tree, self.label_total)
            janela.destroy()

        def cancelar_pagamento():
            janela.destroy()

        tk.Button(
            frame_bottom,
            text="Confirmar Pagamento",
            bg="#00C853",
            fg="#FFFFFF",
            font=("Segoe UI", 10, "bold"),
            relief="flat",
            padx=18,
            pady=6,
            command=confirmar_pagamento,
        ).pack(side="right", padx=10)

        tk.Button(
            frame_bottom,
            text="Cancelar",
            bg="#E53935",
            fg="#FFFFFF",
            font=("Segoe UI", 10, "bold"),
            relief="flat",
            padx=14,
            pady=6,
            command=cancelar_pagamento,
        ).pack(side="right")

    # =======================================================
    # MODO ETIQUETAS
    # =======================================================
    def _abrir_modo_etiquetas(self):
        import subprocess

        try:
            from etiquetas import abrir_modo_etiquetas
            abrir_modo_etiquetas(self.root)
            return
        except ImportError:
            pass
        except Exception as e:
            messagebox.showerror("Erro no modo etiquetas", f"{e}")
            return

        try:
            script_path = os.path.join(os.path.dirname(__file__), "etiquetas.py")
            subprocess.Popen([sys.executable, script_path])
        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível abrir etiquetas:\n{e}")

<<<<<<< HEAD
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
=======

# ============================================================
# EXECUTAR
# ============================================================
def abrir_pdv():
    root = tk.Tk()
    PDVApp(root)
    root.mainloop()

>>>>>>> 2a8eb57eeecf608a6a2004611831a41f917b38e4

if __name__ == "__main__":
    abrir_pdv()
