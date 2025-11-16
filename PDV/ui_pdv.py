import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox

import pdv_functions as pf
from cadastro_produtos import abrir_cadastro_produtos
from relatorios import abrir_relatorio_caixa_dia
from config_empresa import abrir_config_empresa
from cupom import gerar_cupom, gerar_qrcode_pix


# ============================================================
# TEMA MANDACARU TEC – WHITE & BLACK
# ============================================================

THEME = {
    "colors": {
        "bg_page": "#F5F5F7",
        "bg_surface": "#FFFFFF",
        "bg_surface_alt": "#F8F8FA",
        "bg_surface_muted": "#F2F2F4",
        "text_primary": "#111111",
        "text_secondary": "#4A4A4A",
        "text_muted": "#8C8C8C",
        "text_inverse": "#FFFFFF",
        "border_subtle": "#E5E5E8",
        "border_strong": "#D1D1D6",
        "border_focus": "#111111",
        "accent_primary": "#111111",
        "accent_secondary": "#F2F2F4",
        "accent_secondary_hover": "#E4E4E7",
        "feedback_success": "#16A34A",
        "feedback_error": "#DC2626",
    },
    "font": {
        "family": "Segoe UI",
        "size_xs": 11,
        "size_sm": 13,
        "size_md": 15,
        "size_lg": 17,
        "size_xl": 20,
        "size_xxl": 26,
    },
}


LISTA_ITENS = []  # carrinho global


def format_money(valor: float) -> str:
    return f"R$ {valor:.2f}".replace(".", ",")


def configurar_tema_claro(root: tk.Tk):
    """Aplica estilos tipo 'Apple clean' usando ttk.Style."""
    c = THEME["colors"]
    f = THEME["font"]

    root.configure(bg=c["bg_page"])

    style = ttk.Style(root)
    try:
        style.theme_use("clam")
    except Exception:
        pass

    # Treeview (tabela)
    style.configure(
        "Treeview",
        background=c["bg_surface"],
        foreground=c["text_primary"],
        fieldbackground=c["bg_surface"],
        rowheight=26,
        borderwidth=0,
        font=(f["family"], f["size_md"]),
    )
    style.map(
        "Treeview",
        background=[("selected", "#E4E4E7")],
        foreground=[("selected", c["text_primary"])],
    )

    style.configure(
        "Treeview.Heading",
        background=c["bg_surface_alt"],
        foreground=c["text_secondary"],
        relief="flat",
        font=(f["family"], f["size_sm"], "bold"),
    )

    # Scrollbar discreta
    style.configure(
        "Vertical.TScrollbar",
        background=c["bg_surface_alt"],
        troughcolor=c["bg_surface"],
        bordercolor=c["border_subtle"],
    )

    style.configure(
        "TButton",
        font=(f["family"], f["size_md"]),
        padding=6,
    )


# ============================================================
# WRAPPER DE SEGURANÇA PARA BOTÕES
# ============================================================

def safe_command(fn):
    """Envolve um command de botão para mostrar erro em popup se algo quebrar."""
    def _wrapped(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except Exception as e:
            messagebox.showerror("Erro", f"Ocorreu um erro:\n{e}")
    return _wrapped


# ============================================================
# FUNÇÃO AUXILIAR: ATUALIZAR TABELA
# ============================================================
def atualizar_tabela(tree, label_total):
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
    label_total.config(text=format_money(total))


# ============================================================
# CLASSE PRINCIPAL DO PDV
# ============================================================
class PDVApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Mandacaru TEC – PDV")
        self.root.geometry("1120x700")
        self.root.minsize(950, 620)

        configurar_tema_claro(self.root)

        self.entry_codigo = None
        self.entry_qtd = None
        self.tree = None
        self.label_total_valor = None

        self._criar_layout()
        self._criar_menu()
        self._configurar_binds()

        atualizar_tabela(self.tree, self.label_total_valor)

    # --------------------------------------------------------
    # LAYOUT
    # --------------------------------------------------------
    def _criar_layout(self):
        c = THEME["colors"]
        f = THEME["font"]

        shell = tk.Frame(self.root, bg=c["bg_page"])
        shell.pack(fill="both", expand=True, padx=24, pady=16)

        # HEADER
        frame_header = tk.Frame(shell, bg=c["bg_page"])
        frame_header.pack(fill="x", pady=(0, 12))

        tk.Label(
            frame_header,
            text="Mandacaru TEC – PDV",
            bg=c["bg_page"],
            fg=c["text_primary"],
            font=(f["family"], f["size_lg"], "bold"),
        ).pack(side="left")

        tk.Label(
            frame_header,
            text="Caixa rápido • Estoque integrado • Relatórios inteligentes",
            bg=c["bg_page"],
            fg=c["text_muted"],
            font=(f["family"], f["size_sm"]),
        ).pack(side="left", padx=(10, 0), pady=(6, 0))

        # GRID
        frame_grid = tk.Frame(shell, bg=c["bg_page"])
        frame_grid.pack(fill="both", expand=True)

        frame_left = tk.Frame(frame_grid, bg=c["bg_page"])
        frame_left.pack(side="left", fill="both", expand=True, padx=(0, 12))

        frame_right = tk.Frame(frame_grid, bg=c["bg_page"], width=360)
        frame_right.pack(side="right", fill="y", padx=(12, 0))

        # ====== CARD ESQUERDO ======
        card_left = tk.Frame(
            frame_left,
            bg=c["bg_surface"],
            bd=0,
            highlightthickness=1,
            highlightbackground=c["border_subtle"],
        )
        card_left.pack(fill="both", expand=True, pady=(0, 8))

        # Inputs topo
        frame_inputs = tk.Frame(card_left, bg=c["bg_surface"])
        frame_inputs.pack(fill="x", padx=16, pady=16)

        tk.Label(
            frame_inputs,
            text="Código de barras",
            bg=c["bg_surface"],
            fg=c["text_secondary"],
            font=(f["family"], f["size_xs"]),
        ).grid(row=0, column=0, sticky="w")

        self.entry_codigo = tk.Entry(
            frame_inputs,
            width=26,
            font=(f["family"], f["size_md"]),
            bg=c["bg_surface"],
            fg=c["text_primary"],
            insertbackground=c["text_primary"],
            relief="flat",
            highlightthickness=1,
            highlightbackground=c["border_subtle"],
            highlightcolor=c["border_focus"],
        )
        self.entry_codigo.grid(row=1, column=0, sticky="we", pady=(2, 0))
        self.entry_codigo.focus()

        tk.Label(
            frame_inputs,
            text="Qtd",
            bg=c["bg_surface"],
            fg=c["text_secondary"],
            font=(f["family"], f["size_xs"]),
        ).grid(row=0, column=1, sticky="w", padx=(12, 0))

        self.entry_qtd = tk.Entry(
            frame_inputs,
            width=6,
            font=(f["family"], f["size_md"]),
            bg=c["bg_surface"],
            fg=c["text_primary"],
            insertbackground=c["text_primary"],
            relief="flat",
            highlightthickness=1,
            highlightbackground=c["border_subtle"],
            highlightcolor=c["border_focus"],
        )
        self.entry_qtd.insert(0, "1")
        self.entry_qtd.grid(row=1, column=1, sticky="w", padx=(12, 0), pady=(2, 0))

        btn_add = tk.Button(
            frame_inputs,
            text="Adicionar (F2)",
            bg=c["accent_primary"],
            fg=c["text_inverse"],
            activebackground="#000000",
            activeforeground=c["text_inverse"],
            bd=0,
            relief="flat",
            font=(f["family"], f["size_md"], "bold"),
            padx=24,
            pady=8,
            command=safe_command(self._adicionar_item_ui),
        )
        btn_add.grid(row=1, column=2, padx=(16, 0))

        frame_inputs.grid_columnconfigure(0, weight=1)

        # Tabela
        frame_table = tk.Frame(card_left, bg=c["bg_surface"])
        frame_table.pack(fill="both", expand=True, padx=16, pady=(0, 16))

        cols = ("codigo", "descricao", "qtd", "unit", "sub")
        self.tree = ttk.Treeview(frame_table, columns=cols, show="headings", height=14)
        self.tree.pack(side="left", fill="both", expand=True)

        self.tree.heading("codigo", text="Código")
        self.tree.heading("descricao", text="Descrição")
        self.tree.heading("qtd", text="Qtd")
        self.tree.heading("unit", text="Preço Unit.")
        self.tree.heading("sub", text="Subtotal")

        self.tree.column("codigo", width=110, anchor="w")
        self.tree.column("descricao", width=350, anchor="w")
        self.tree.column("qtd", width=60, anchor="e")
        self.tree.column("unit", width=90, anchor="e")
        self.tree.column("sub", width=110, anchor="e")

        scroll = ttk.Scrollbar(
            frame_table, orient="vertical", command=self.tree.yview
        )
        self.tree.configure(yscroll=scroll.set)
        scroll.pack(side="right", fill="y")

        # ====== FOOTER BOTÕES ======
        footer = tk.Frame(shell, bg=c["bg_page"])
        footer.pack(fill="x", pady=(8, 0))

        frame_footer_left = tk.Frame(footer, bg=c["bg_page"])
        frame_footer_left.pack(side="left")

        frame_footer_right = tk.Frame(footer, bg=c["bg_page"])
        frame_footer_right.pack(side="right")

        def ghost_button(parent, text, command):
            return tk.Button(
                parent,
                text=text,
                command=safe_command(command),
                bg=c["bg_page"],
                fg=c["text_primary"],
                activebackground=c["accent_secondary_hover"],
                activeforeground=c["text_primary"],
                bd=0,
                relief="flat",
                font=(THEME["font"]["family"], THEME["font"]["size_sm"]),
                padx=14,
                pady=6,
            )

        def secondary_button(parent, text, command):
            return tk.Button(
                parent,
                text=text,
                command=safe_command(command),
                bg=c["accent_secondary"],
                fg=c["text_primary"],
                activebackground=c["accent_secondary_hover"],
                activeforeground=c["text_primary"],
                bd=0,
                relief="flat",
                font=(THEME["font"]["family"], THEME["font"]["size_sm"], "bold"),
                padx=18,
                pady=8,
            )

        def primary_button(parent, text, command):
            return tk.Button(
                parent,
                text=text,
                command=safe_command(command),
                bg=c["accent_primary"],
                fg=c["text_inverse"],
                activebackground="#000000",
                activeforeground=c["text_inverse"],
                bd=0,
                relief="flat",
                font=(THEME["font"]["family"], THEME["font"]["size_sm"], "bold"),
                padx=22,
                pady=9,
            )

        ghost_button(
            frame_footer_left, "REMOVER ITEM (DEL)", self._remover_item_ui
        ).pack(side="left", padx=(0, 8))
        ghost_button(
            frame_footer_left, "LIMPAR CARRINHO (F4)", self._limpar
        ).pack(side="left")

        secondary_button(
            frame_footer_right, "FECHAR (ESC)", self.root.destroy
        ).pack(side="right", padx=(8, 0))
        primary_button(
            frame_footer_right, "FINALIZAR VENDA (F5)", self._abrir_tela_pagamento
        ).pack(side="right")

        # ====== COLUNA DIREITA – TOTAL + AÇÕES ======
        card_right = tk.Frame(
            frame_right,
            bg=c["bg_surface"],
            bd=0,
            highlightthickness=1,
            highlightbackground=c["border_subtle"],
        )
        card_right.pack(fill="y")

        frame_total = tk.Frame(card_right, bg=c["bg_surface"])
        frame_total.pack(fill="x", padx=16, pady=(16, 8))

        tk.Label(
            frame_total,
            text="TOTAL A PAGAR",
            bg=c["bg_surface"],
            fg=c["text_secondary"],
            font=(f["family"], f["size_sm"]),
        ).pack(anchor="w")

        self.label_total_valor = tk.Label(
            frame_total,
            text="R$ 0,00",
            bg=c["bg_surface"],
            fg=c["text_primary"],
            font=(f["family"], f["size_xxl"], "bold"),
        )
        self.label_total_valor.pack(anchor="w", pady=(4, 0))

        tk.Frame(
            card_right, bg=c["border_subtle"], height=1
        ).pack(fill="x", padx=16, pady=(0, 8))

        frame_actions = tk.Frame(card_right, bg=c["bg_surface"])
        frame_actions.pack(fill="x", padx=16, pady=(8, 16))

        tk.Label(
            frame_actions,
            text="Atalhos rápidos",
            bg=c["bg_surface"],
            fg=c["text_secondary"],
            font=(f["family"], f["size_sm"]),
        ).pack(anchor="w", pady=(0, 6))

        def action_button(text, cmd):
            btn = tk.Button(
                frame_actions,
                text=text,
                bg=c["accent_secondary"],
                fg=c["text_primary"],
                activebackground=c["accent_secondary_hover"],
                activeforeground=c["text_primary"],
                bd=0,
                relief="flat",
                font=(f["family"], f["size_sm"]),
                anchor="w",
                padx=12,
                pady=6,
                justify="left",
                command=safe_command(cmd),
            )
            btn.pack(fill="x", pady=3)
            return btn

        action_button(
            "Cadastro de Produtos", lambda: abrir_cadastro_produtos(self.root)
        )
        action_button("Modo Etiquetas", self._abrir_modo_etiquetas)
        action_button(
            "Relatório de Caixa (Dia)", lambda: abrir_relatorio_caixa_dia(self.root)
        )
        action_button(
            "Configurações da Empresa", lambda: abrir_config_empresa(self.root)
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
        menu_prod.add_command(
            label="Cadastro de Produtos", command=lambda: abrir_cadastro_produtos(self.root)
        )
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

    # --------------------------------------------------------
    # FUNÇÕES DO PDV
    # --------------------------------------------------------
    def _adicionar_item_ui(self):
        codigo = self.entry_codigo.get().strip()
        if not codigo:
            messagebox.showwarning("Atenção", "Informe o código de barras.")
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

        atualizar_tabela(self.tree, self.label_total_valor)

        self.entry_codigo.delete(0, tk.END)
        self.entry_qtd.delete(0, tk.END)
        self.entry_qtd.insert(0, "1")
        self.entry_codigo.focus()

    def _remover_item_ui(self):
        item_sel = self.tree.focus()
        if not item_sel:
            return
        index = self.tree.index(item_sel)
        pf.remover_item(LISTA_ITENS, index)
        atualizar_tabela(self.tree, self.label_total_valor)

    def _limpar(self):
        LISTA_ITENS.clear()
        atualizar_tabela(self.tree, self.label_total_valor)

    # =======================================================
    # TELA DE PAGAMENTO – ESTILO CLEAN
    # =======================================================
    def _abrir_tela_pagamento(self):
        if not LISTA_ITENS:
            messagebox.showwarning("Atenção", "Não há itens no carrinho.")
            return

        c = THEME["colors"]
        f = THEME["font"]

        total = pf.calcular_total(LISTA_ITENS)

        win = tk.Toplevel(self.root)
        win.title("Pagamento")
        win.configure(bg=c["bg_page"])
        win.geometry("460x420")
        win.resizable(False, False)
        win.grab_set()
        win.focus_force()

        card = tk.Frame(
            win,
            bg=c["bg_surface"],
            bd=0,
            highlightthickness=1,
            highlightbackground=c["border_subtle"],
        )
        card.pack(fill="both", expand=True, padx=32, pady=24)

        tk.Label(
            card,
            text="Total a receber",
            bg=c["bg_surface"],
            fg=c["text_secondary"],
            font=(f["family"], f["size_sm"]),
        ).pack(anchor="w", pady=(10, 0))

        tk.Label(
            card,
            text=format_money(total),
            bg=c["bg_surface"],
            fg=c["text_primary"],
            font=(f["family"], f["size_xxl"], "bold"),
        ).pack(anchor="w", pady=(0, 10))

        body = tk.Frame(card, bg=c["bg_surface"])
        body.pack(fill="both", expand=True, pady=(8, 0))

        forma_var = tk.StringVar(value="")
        win.entry_valor = None
        win.qr_label = None

        frame_buttons = tk.Frame(body, bg=c["bg_surface"])
        frame_buttons.pack(side="left", fill="y", padx=(0, 12))

        frame_detail = tk.Frame(body, bg=c["bg_surface"])
        frame_detail.pack(side="right", fill="both", expand=True)

        def limpar_detail():
            for w in frame_detail.winfo_children():
                w.destroy()
            win.entry_valor = None
            win.qr_label = None

        def button_payment(text, cmd):
            return tk.Button(
                frame_buttons,
                text=text,
                bg=c["accent_secondary"],
                fg=c["text_primary"],
                activebackground=c["accent_secondary_hover"],
                activeforeground=c["text_primary"],
                bd=0,
                relief="flat",
                font=(f["family"], f["size_sm"], "bold"),
                padx=12,
                pady=8,
                anchor="w",
                command=safe_command(cmd),
            )

        def selecionar_dinheiro():
            forma_var.set("DINHEIRO")
            limpar_detail()
            tk.Label(
                frame_detail,
                text="Pagamento em dinheiro",
                bg=c["bg_surface"],
                fg=c["text_primary"],
                font=(f["family"], f["size_md"], "bold"),
            ).pack(anchor="w", pady=(0, 4))
            tk.Label(
                frame_detail,
                text="Valor recebido do cliente:",
                bg=c["bg_surface"],
                fg=c["text_secondary"],
                font=(f["family"], f["size_sm"]),
            ).pack(anchor="w")

            entry = tk.Entry(
                frame_detail,
                width=12,
                font=(f["family"], f["size_md"]),
                bg=c["bg_surface"],
                fg=c["text_primary"],
                relief="flat",
                highlightthickness=1,
                highlightbackground=c["border_subtle"],
                highlightcolor=c["border_focus"],
                insertbackground=c["text_primary"],
            )
            entry.pack(anchor="w", pady=(4, 0))
            entry.insert(0, f"{total:.2f}")
            entry.focus()
            win.entry_valor = entry

        def selecionar_pix():
            forma_var.set("PIX")
            limpar_detail()
            tk.Label(
                frame_detail,
                text="Pagamento via PIX",
                bg=c["bg_surface"],
                fg=c["text_primary"],
                font=(f["family"], f["size_md"], "bold"),
            ).pack(anchor="w", pady=(0, 4))
            tk.Label(
                frame_detail,
                text="Mostre o QR Code ao cliente.\nA chave PIX também sairá no cupom.",
                bg=c["bg_surface"],
                fg=c["text_secondary"],
                font=(f["family"], f["size_xs"]),
                justify="left",
            ).pack(anchor="w", pady=(0, 4))

            caminho_qr = gerar_qrcode_pix(total)
            if caminho_qr and os.path.isfile(caminho_qr):
                try:
                    img = tk.PhotoImage(file=caminho_qr)
                    lbl = tk.Label(frame_detail, image=img, bg=c["bg_surface"])
                    lbl.image = img
                    lbl.pack(pady=(4, 0))
                    win.qr_label = lbl
                except Exception as e:
                    tk.Label(
                        frame_detail,
                        text=f"Não foi possível exibir o QR Code.\n{e}",
                        bg=c["bg_surface"],
                        fg=c["feedback_error"],
                        font=(f["family"], f["size_xs"]),
                        justify="left",
                    ).pack(anchor="w", pady=(4, 0))
            else:
                tk.Label(
                    frame_detail,
                    text="QR Code não gerado.\nVerifique chave PIX e biblioteca 'qrcode'.",
                    bg=c["bg_surface"],
                    fg=c["feedback_error"],
                    font=(f["family"], f["size_xs"]),
                    justify="left",
                ).pack(anchor="w", pady=(4, 0))

        def selecionar_cartao():
            forma_var.set("CARTÃO")
            limpar_detail()
            tk.Label(
                frame_detail,
                text="Pagamento no cartão",
                bg=c["bg_surface"],
                fg=c["text_primary"],
                font=(f["family"], f["size_md"], "bold"),
            ).pack(anchor="w", pady=(0, 4))
            tk.Label(
                frame_detail,
                text="Passe o cartão na maquininha e\nconfirme após a aprovação.",
                bg=c["bg_surface"],
                fg=c["text_secondary"],
                font=(f["family"], f["size_xs"]),
                justify="left",
            ).pack(anchor="w", pady=(0, 4))

        button_payment("DINHEIRO", selecionar_dinheiro).pack(fill="x", pady=2)
        button_payment("PIX", selecionar_pix).pack(fill="x", pady=2)
        button_payment("CARTÃO", selecionar_cartao).pack(fill="x", pady=2)

        # FOOTER CONFIRMAR/CANCELAR
        footer = tk.Frame(card, bg=c["bg_surface"])
        footer.pack(fill="x", pady=(12, 10))

        def confirmar():
            forma = forma_var.get()
            if not forma:
                messagebox.showwarning("Atenção", "Selecione a forma de pagamento.")
                return

            valor_recebido = None
            if forma == "DINHEIRO":
                entry = win.entry_valor
                if not entry:
                    messagebox.showerror("Erro", "Campo de valor não encontrado.")
                    return
                txt = entry.get().strip()
                if not txt:
                    messagebox.showwarning("Atenção", "Informe o valor recebido.")
                    return
                try:
                    valor_recebido = float(txt.replace(",", "."))
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
            atualizar_tabela(self.tree, self.label_total_valor)
            win.destroy()

        def cancelar():
            win.destroy()

        tk.Button(
            footer,
            text="Cancelar",
            command=safe_command(cancelar),
            bg=c["accent_secondary"],
            fg=c["text_primary"],
            activebackground=c["accent_secondary_hover"],
            activeforeground=c["text_primary"],
            bd=0,
            relief="flat",
            font=(f["family"], f["size_sm"]),
            padx=16,
            pady=6,
        ).pack(side="right", padx=(0, 6))

        tk.Button(
            footer,
            text="Confirmar pagamento",
            command=safe_command(confirmar),
            bg=c["accent_primary"],
            fg=c["text_inverse"],
            activebackground="#000000",
            activeforeground=c["text_inverse"],
            bd=0,
            relief="flat",
            font=(f["family"], f["size_sm"], "bold"),
            padx=18,
            pady=6,
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


# ============================================================
# EXECUTAR
# ============================================================
def abrir_pdv():
    root = tk.Tk()
    PDVApp(root)
    root.mainloop()


if __name__ == "__main__":
    abrir_pdv()
