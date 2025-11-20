import tkinter as tk
from tkinter import ttk, messagebox

import pdv_functions as pf
from cadastro_produtos import abrir_cadastro_produtos
from relatorios import abrir_relatorio_caixa_dia
from config_empresa import abrir_config_empresa
from etiquetas import abrir_etiquetas
from cupom import gerar_cupom

# Lista global da venda
LISTA_ITENS = []


# ======================= TEMA / ESTILO =======================

def configurar_tema_claro(root: tk.Tk):
    """
    Aplica o tema MandacaruTEC White&Black básico no Tkinter.
    """
    bg_page = "#F5F5F7"
    bg_surface = "#FFFFFF"

    root.title("Mandacaru TEC – PDV")
    root.geometry("1200x700")
    root.configure(bg=bg_page)

    try:
        default_font = ("Segoe UI", 10)
        root.option_add("*Font", default_font)
    except Exception:
        pass

    root._mandacaru_theme = {
        "bg_page": bg_page,
        "bg_surface": bg_surface,
        "bg_surface_alt": "#F8F8FA",
        "bg_surface_muted": "#F2F2F4",
        "border_subtle": "#E5E5E8",
        "border_strong": "#D1D1D6",
        "text_primary": "#111111",
        "text_secondary": "#4A4A4A",
        "text_muted": "#8C8C8C",
        "accent_primary": "#111111",
        "accent_secondary": "#F2F2F4",
    }


def atualizar_tabela(tree: ttk.Treeview, label_total: tk.Label):
    """Recarrega a TreeView com os itens atuais e atualiza o total."""
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
                f"{item['quantidade']:.0f}",
                f"R$ {item['preco_unit']:.2f}",
                f"R$ {item['subtotal']:.2f}",
            ),
        )

    total = pf.calcular_total(LISTA_ITENS)
    label_total.config(text=f"R$ {total:.2f}")


class PDVApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        configurar_tema_claro(self.root)

        theme = self.root._mandacaru_theme
        self.bg_page = theme["bg_page"]
        self.bg_surface = theme["bg_surface"]
        self.bg_surface_alt = theme["bg_surface_alt"]
        self.bg_surface_muted = theme["bg_surface_muted"]
        self.border_subtle = theme["border_subtle"]
        self.border_strong = theme["border_strong"]
        self.text_primary = theme["text_primary"]
        self.text_secondary = theme["text_secondary"]
        self.text_muted = theme["text_muted"]
        self.accent_primary = theme["accent_primary"]
        self.accent_secondary = theme["accent_secondary"]

        self.entry_codigo: tk.Entry | None = None
        self.entry_qtd: tk.Entry | None = None
        self.tree: ttk.Treeview | None = None
        self.label_total_valor: tk.Label | None = None

        self._forma_pagamento_selecionada = None

        self._criar_layout()
        self._criar_menu()
        self._configurar_binds()

        atualizar_tabela(self.tree, self.label_total_valor)

    # ---------------------- MENU ----------------------

    def _criar_menu(self):
        menubar = tk.Menu(self.root)

        menu_pdv = tk.Menu(menubar, tearoff=0)
        menu_pdv.add_command(label="Tela de Vendas")
        menubar.add_cascade(label="PDV", menu=menu_pdv)

        menu_cadastros = tk.Menu(menubar, tearoff=0)
        menu_cadastros.add_command(
            label="Cadastro de Produtos",
            command=self._abrir_cadastro_produtos,
        )
        menubar.add_cascade(label="Cadastros", menu=menu_cadastros)

        menu_rel = tk.Menu(menubar, tearoff=0)
        menu_rel.add_command(
            label="Relatório de Caixa (Dia)",
            command=lambda: abrir_relatorio_caixa_dia(self.root),
        )
        menubar.add_cascade(label="Relatórios", menu=menu_rel)

        menu_conf = tk.Menu(menubar, tearoff=0)
        menu_conf.add_command(
            label="Configurações da Empresa",
            command=lambda: abrir_config_empresa(self.root),
        )
        menubar.add_cascade(label="Configurações", menu=menu_conf)

        self.root.config(menu=menubar)

    def _abrir_cadastro_produtos(self):
        try:
            abrir_cadastro_produtos(self.root)
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao abrir cadastro de produtos:\n{e}")

    # ---------------------- LAYOUT PRINCIPAL ----------------------

    def _criar_layout(self):
        frame_root = tk.Frame(self.root, bg=self.bg_page)
        frame_root.pack(fill="both", expand=True, padx=24, pady=(16, 12))

        frame_esq = tk.Frame(frame_root, bg=self.bg_page)
        frame_esq.pack(side="left", fill="both", expand=True)

        frame_dir = tk.Frame(frame_root, bg=self.bg_page)
        frame_dir.pack(side="right", fill="y")

        header = tk.Frame(frame_esq, bg=self.bg_page)
        header.pack(fill="x", pady=(0, 12))

        tk.Label(
            header,
            text="Mandacaru TEC – PDV",
            bg=self.bg_page,
            fg=self.text_primary,
            font=("Segoe UI", 16, "bold"),
        ).pack(anchor="w")

        tk.Label(
            header,
            text="Caixa rápido · Estoque integrado · Relatórios inteligentes",
            bg=self.bg_page,
            fg=self.text_muted,
            font=("Segoe UI", 9),
        ).pack(anchor="w")

        # ---------- CARD PRODUTO ----------
        card_prod = tk.Frame(
            frame_esq,
            bg=self.bg_surface,
            bd=1,
            relief="solid",
            highlightthickness=0,
        )
        card_prod.pack(fill="x", pady=(0, 12))

        row1 = tk.Frame(card_prod, bg=self.bg_surface)
        row1.pack(fill="x", padx=14, pady=(10, 2))

        tk.Label(
            row1,
            text="Código de barras",
            bg=self.bg_surface,
            fg=self.text_secondary,
        ).pack(side="left", anchor="w")

        tk.Label(
            row1,
            text="Qtd",
            bg=self.bg_surface,
            fg=self.text_secondary,
        ).pack(side="right", anchor="e")

        row2 = tk.Frame(card_prod, bg=self.bg_surface)
        row2.pack(fill="x", padx=14, pady=(0, 10))

        self.entry_codigo = tk.Entry(row2, bd=1, relief="solid")
        self.entry_codigo.pack(side="left", fill="x", expand=True)
        self.entry_codigo.focus()

        self.entry_qtd = tk.Entry(
            row2,
            width=5,
            bd=1,
            relief="solid",
            justify="center",
        )
        self.entry_qtd.insert(0, "1")
        self.entry_qtd.pack(side="left", padx=(8, 8))

        btn_add = tk.Button(
            row2,
            text="Adicionar (F2)",
            bg=self.accent_primary,
            fg="#FFFFFF",
            activebackground="#000000",
            activeforeground="#FFFFFF",
            bd=0,
            relief="flat",
            padx=18,
            pady=6,
            command=self._adicionar_item_ui,
        )
        btn_add.pack(side="right")

        # ---------- TABELA ----------
        frame_table = tk.Frame(
            frame_esq,
            bg=self.bg_surface,
            bd=1,
            relief="solid",
        )
        frame_table.pack(fill="both", expand=True)

        colunas = ("codigo", "descricao", "qtd", "unit", "sub")
        self.tree = ttk.Treeview(
            frame_table,
            columns=colunas,
            show="headings",
            height=15,
        )
        self.tree.pack(side="left", fill="both", expand=True)

        self.tree.heading("codigo", text="Código")
        self.tree.heading("descricao", text="Descrição")
        self.tree.heading("qtd", text="Qtd")
        self.tree.heading("unit", text="Preço Unit.")
        self.tree.heading("sub", text="Subtotal")

        self.tree.column("codigo", width=130, anchor="w")
        self.tree.column("descricao", width=300, anchor="w")
        self.tree.column("qtd", width=60, anchor="center")
        self.tree.column("unit", width=100, anchor="e")
        self.tree.column("sub", width=120, anchor="e")

        scrollbar = ttk.Scrollbar(
            frame_table, orient="vertical", command=self.tree.yview
        )
        scrollbar.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=scrollbar.set)

        # ---------- BARRA INFERIOR ----------
        frame_bottom = tk.Frame(frame_esq, bg=self.bg_page)
        frame_bottom.pack(fill="x", pady=(8, 0))

        tk.Button(
            frame_bottom,
            text="REMOVER ITEM (DEL)",
            bg=self.bg_page,
            fg=self.text_primary,
            bd=0,
            padx=10,
            pady=6,
            command=self._remover_item_ui,
        ).pack(side="left", padx=(0, 8))

        tk.Button(
            frame_bottom,
            text="LIMPAR CARRINHO (F4)",
            bg=self.bg_page,
            fg=self.text_primary,
            bd=0,
            padx=10,
            pady=6,
            command=self._limpar_carrinho,
        ).pack(side="left")

        tk.Button(
            frame_bottom,
            text="FECHAR (ESC)",
            bg=self.bg_page,
            fg=self.text_primary,
            bd=0,
            padx=10,
            pady=6,
            command=self.root.destroy,
        ).pack(side="right", padx=(8, 0))

        tk.Button(
            frame_bottom,
            text="FINALIZAR VENDA (F5)",
            bg=self.accent_primary,
            fg="#FFFFFF",
            bd=0,
            padx=18,
            pady=6,
            command=self._abrir_tela_pagamento,
        ).pack(side="right")

        # ---------- PAINEL DIREITA ----------
        card_total = tk.Frame(
            frame_dir,
            bg=self.bg_surface,
            bd=1,
            relief="solid",
        )
        card_total.pack(fill="x", pady=(0, 12))

        tk.Label(
            card_total,
            text="TOTAL A PAGAR",
            bg=self.bg_surface,
            fg=self.text_secondary,
            font=("Segoe UI", 9, "bold"),
        ).pack(anchor="w", padx=16, pady=(10, 0))

        self.label_total_valor = tk.Label(
            card_total,
            text="R$ 0,00",
            bg=self.bg_surface,
            fg=self.text_primary,
            font=("Segoe UI", 26, "bold"),
        )
        self.label_total_valor.pack(anchor="w", padx=16, pady=(0, 12))

        card_shortcuts = tk.Frame(
            frame_dir,
            bg=self.bg_surface,
            bd=1,
            relief="solid",
        )
        card_shortcuts.pack(fill="x")

        tk.Label(
            card_shortcuts,
            text="Atalhos rápidos",
            bg=self.bg_surface,
            fg=self.text_secondary,
            font=("Segoe UI", 9, "bold"),
        ).pack(anchor="w", padx=16, pady=(10, 6))

        def btn_shortcut(text, command):
            return tk.Button(
                card_shortcuts,
                text=text,
                anchor="w",
                bg=self.bg_surface_alt,
                fg=self.text_primary,
                activebackground=self.bg_surface_muted,
                activeforeground=self.text_primary,
                bd=0,
                relief="flat",
                padx=14,
                pady=6,
                command=command,
            )

        btn_shortcut("Cadastro de Produtos", self._abrir_cadastro_produtos).pack(
            fill="x", padx=12, pady=(0, 6)
        )
        btn_shortcut("Modo Etiquetas", lambda: abrir_etiquetas(self.root)).pack(
            fill="x", padx=12, pady=(0, 6)
        )
        btn_shortcut(
            "Relatório de Caixa (Dia)",
            lambda: abrir_relatorio_caixa_dia(self.root),
        ).pack(fill="x", padx=12, pady=(0, 6))
        btn_shortcut(
            "Configurações da Empresa",
            lambda: abrir_config_empresa(self.root),
        ).pack(fill="x", padx=12, pady=(0, 12))

    # ---------------------- BINDS ----------------------

    def _configurar_binds(self):
        self.root.bind("<F2>", lambda e: self._adicionar_item_ui())
        self.root.bind("<Delete>", lambda e: self._remover_item_ui())
        self.root.bind("<F4>", lambda e: self._limpar_carrinho())
        self.root.bind("<F5>", lambda e: self._abrir_tela_pagamento())
        self.root.bind("<Escape>", lambda e: self.root.destroy())

    # ---------------------- LÓGICA ----------------------

    def _adicionar_item_ui(self):
        codigo = self.entry_codigo.get().strip()
        if not codigo:
            messagebox.showwarning("Aviso", "Digite ou bip um código de barras.")
            return

        qtd_txt = self.entry_qtd.get().strip() or "1"

        try:
            qtd = int(qtd_txt)
            if qtd <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Erro", "Quantidade inválida.")
            return

        resultado = pf.adicionar_item(LISTA_ITENS, codigo, qtd)
        if resultado.get("erro"):
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
            messagebox.showwarning("Aviso", "Selecione um item para remover.")
            return

        try:
            idx = int(item_sel)
        except ValueError:
            return

        pf.remover_item(LISTA_ITENS, idx)
        atualizar_tabela(self.tree, self.label_total_valor)

    def _limpar_carrinho(self):
        if not LISTA_ITENS:
            return

        if not messagebox.askyesno(
            "Confirmar", "Deseja limpar todo o carrinho de itens?"
        ):
            return

        LISTA_ITENS.clear()
        atualizar_tabela(self.tree, self.label_total_valor)

    # ---------------------- PAGAMENTO ----------------------

    def _abrir_tela_pagamento(self):
        if not LISTA_ITENS:
            messagebox.showwarning("Aviso", "Nenhum item no carrinho.")
            return

        total = pf.calcular_total(LISTA_ITENS)

        modal = tk.Toplevel(self.root)
        modal.title("Pagamento")
        modal.transient(self.root)
        modal.grab_set()
        modal.configure(bg=self.bg_surface)
        modal.resizable(False, False)

        modal.update_idletasks()
        w, h = 420, 360
        x = self.root.winfo_rootx() + (self.root.winfo_width() // 2) - (w // 2)
        y = self.root.winfo_rooty() + (self.root.winfo_height() // 2) - (h // 2)
        modal.geometry(f"{w}x{h}+{x}+{y}")

        frame_header = tk.Frame(modal, bg=self.bg_surface)
        frame_header.pack(fill="x", padx=24, pady=(20, 10))

        tk.Label(
            frame_header,
            text="Total a receber",
            bg=self.bg_surface,
            fg=self.text_secondary,
            font=("Segoe UI", 9),
        ).pack(anchor="w")

        tk.Label(
            frame_header,
            text=f"R$ {total:.2f}",
            bg=self.bg_surface,
            fg=self.text_primary,
            font=("Segoe UI", 22, "bold"),
        ).pack(anchor="w")

        frame_buttons = tk.Frame(modal, bg=self.bg_surface)
        frame_buttons.pack(fill="x", padx=24, pady=(10, 10))

        forma_var = tk.StringVar(value="")

        def selecionar_forma(forma):
            forma_var.set(forma)
            atualizar_label_forma()

        def button_payment(texto, forma):
            return tk.Button(
                frame_buttons,
                text=texto,
                bg=self.bg_surface_alt,
                fg=self.text_primary,
                activebackground=self.bg_surface_muted,
                activeforeground=self.text_primary,
                bd=1,
                relief="solid",
                padx=16,
                pady=8,
                width=12,
                command=lambda: selecionar_forma(forma),
            )

        btn_din = button_payment("DINHEIRO", "DINHEIRO")
        btn_pix = button_payment("PIX", "PIX")
        btn_card = button_payment("CARTÃO", "CARTAO")

        btn_din.grid(row=0, column=0, padx=(0, 8), pady=(0, 6))
        btn_pix.grid(row=0, column=1, padx=(0, 8), pady=(0, 6))
        btn_card.grid(row=1, column=0, columnspan=2, sticky="we")

        frame_detail = tk.Frame(modal, bg=self.bg_surface)
        frame_detail.pack(fill="both", padx=24, pady=(10, 10), expand=True)

        label_forma = tk.Label(
            frame_detail,
            text="Selecione a forma de pagamento",
            bg=self.bg_surface,
            fg=self.text_secondary,
            font=("Segoe UI", 9),
        )
        label_forma.pack(anchor="w")

        frame_valor = tk.Frame(frame_detail, bg=self.bg_surface)
        frame_valor.pack(fill="x", pady=(10, 0))

        tk.Label(
            frame_valor,
            text="Valor recebido:",
            bg=self.bg_surface,
            fg=self.text_secondary,
        ).pack(anchor="w")

        entry_valor = tk.Entry(frame_valor, bd=1, relief="solid")
        entry_valor.pack(fill="x", pady=(2, 0))
        entry_valor.insert(0, f"{total:.2f}")

        def atualizar_label_forma():
            forma = forma_var.get()
            if forma == "DINHEIRO":
                label_forma.config(text="Pagamento em DINHEIRO")
            elif forma == "PIX":
                label_forma.config(text="Pagamento em PIX")
            elif forma == "CARTAO":
                label_forma.config(text="Pagamento em CARTÃO")
            else:
                label_forma.config(text="Selecione a forma de pagamento")

        frame_footer = tk.Frame(modal, bg=self.bg_surface)
        frame_footer.pack(fill="x", padx=24, pady=(10, 16))

        def confirmar():
            forma = forma_var.get()
            if not forma:
                messagebox.showwarning("Atenção", "Selecione a forma de pagamento.")
                return

            valor_recebido_txt = entry_valor.get().strip() or f"{total:.2f}"

            try:
                valor_recebido = float(valor_recebido_txt.replace(",", "."))
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

            try:
                gerar_cupom(resumo, tipo="CLIENTE", pasta="cupons")
                gerar_cupom(resumo, tipo="CAIXA", pasta="cupons")
            except Exception as e:
                messagebox.showwarning(
                    "Aviso",
                    f"Venda registrada, mas houve erro ao gerar cupons:\n{e}",
                )

            pf.exibir_resumo_venda(resumo)

            LISTA_ITENS.clear()
            atualizar_tabela(self.tree, self.label_total_valor)

            modal.destroy()

        tk.Button(
            frame_footer,
            text="Cancelar",
            bg=self.bg_surface_alt,
            fg=self.text_primary,
            bd=0,
            padx=16,
            pady=6,
            command=modal.destroy,
        ).pack(side="left")

        tk.Button(
            frame_footer,
            text="Confirmar pagamento",
            bg=self.accent_primary,
            fg="#FFFFFF",
            bd=0,
            padx=18,
            pady=6,
            command=confirmar,
        ).pack(side="right")

        modal.bind("<Return>", lambda e: confirmar())
        modal.bind("<Escape>", lambda e: modal.destroy())


def abrir_pdv():
    root = tk.Tk()
    PDVApp(root)
    root.mainloop()


if __name__ == "__main__":
    abrir_pdv()
