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


def buscar_produto_por_codigo(codigo_barras):
    """Busca 1 produto no banco pelo código de barras."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT id, codigo_barras, nome, preco FROM produtos WHERE codigo_barras = ?;",
        (codigo_barras,),
    )
    row = cur.fetchone()
    conn.close()
    return row


def abrir_etiquetas(parent=None):
    """
    Tela de geração de etiquetas.
    - Fundo amarelo, texto preto, 'OFERTA' em vermelho.
    - Sem logo, sem QRCode.
    """

    if parent is None:
        janela = tk.Toplevel()
    else:
        janela = tk.Toplevel(parent)

    janela.title("Mandacaru TEC - Etiquetas")
    janela.geometry("1000x700")
    janela.configure(bg="#1a237e")
    
    # Aplicar ícone de cacto
    aplicar_icone_cacto(janela)

    # ====== FRAME DE CONTROLE (ESQUERDA) ======
    frame_left = tk.Frame(janela, bg="#283593")
    frame_left.pack(side="left", fill="y", padx=15, pady=15)

    # Código de Barras
    tk.Label(
        frame_left, 
        text="Código de Barras:", 
        bg="#283593",
        fg="white",
        font=("Arial", 11, "bold")
    ).grid(row=0, column=0, sticky="w", pady=8)
    entry_codigo = tk.Entry(frame_left, width=28, font=("Arial", 11), bg="white", fg="black")
    entry_codigo.grid(row=0, column=1, padx=8, pady=8)

    def on_buscar():
        codigo = entry_codigo.get().strip()
        if not codigo:
            messagebox.showwarning("Aviso", "Digite um código de barras.")
            return
        prod = buscar_produto_por_codigo(codigo)
        if not prod:
            messagebox.showerror("Erro", "Produto não encontrado.")
            return
        entry_nome.delete(0, tk.END)
        entry_nome.insert(0, prod["nome"])
        entry_preco.delete(0, tk.END)
        entry_preco.insert(0, f"{prod['preco']:.2f}")

    btn_buscar = tk.Button(
        frame_left, 
        text="🔍 Buscar", 
        command=on_buscar,
        bg="#5c6bc0",
        fg="white",
        font=("Arial", 10, "bold"),
        relief="raised",
        bd=2,
        padx=10,
        pady=5,
        cursor="hand2"
    )
    btn_buscar.grid(row=0, column=2, padx=8, pady=8)

    # Nome do produto
    tk.Label(
        frame_left, 
        text="Nome do Produto:", 
        bg="#283593",
        fg="white",
        font=("Arial", 11, "bold")
    ).grid(row=1, column=0, sticky="w", pady=8)
    entry_nome = tk.Entry(frame_left, width=45, font=("Arial", 11), bg="white", fg="black")
    entry_nome.grid(row=1, column=1, columnspan=2, padx=8, pady=8, sticky="w")

    # Preço principal (normal ou oferta)
    tk.Label(
        frame_left, 
        text="Preço (R$):", 
        bg="#283593",
        fg="white",
        font=("Arial", 11, "bold")
    ).grid(row=2, column=0, sticky="w", pady=8)
    entry_preco = tk.Entry(frame_left, width=18, font=("Arial", 11), bg="white", fg="black")
    entry_preco.grid(row=2, column=1, padx=8, pady=8, sticky="w")

    # Checkbox de oferta
    var_oferta = tk.BooleanVar(value=False)
    chk_oferta = tk.Checkbutton(
        frame_left,
        text="Etiqueta de OFERTA",
        bg="#283593",
        fg="white",
        selectcolor="#3949ab",
        activebackground="#283593",
        activeforeground="white",
        font=("Arial", 11, "bold"),
        variable=var_oferta,
    )
    chk_oferta.grid(row=3, column=0, columnspan=2, sticky="w", pady=10)

    # Quantidade de etiquetas
    tk.Label(
        frame_left, 
        text="Qtd de Etiquetas:", 
        bg="#283593",
        fg="white",
        font=("Arial", 11, "bold")
    ).grid(row=4, column=0, sticky="w", pady=8)
    entry_qtd = tk.Entry(frame_left, width=12, font=("Arial", 11), bg="white", fg="black")
    entry_qtd.insert(0, "1")
    entry_qtd.grid(row=4, column=1, padx=8, pady=8, sticky="w")

    # Lista de etiquetas configuradas (tabela)
    tk.Label(
        frame_left, 
        text="Etiquetas na Fila:", 
        bg="#283593",
        fg="white", 
        font=("Arial", 12, "bold")
    ).grid(row=5, column=0, columnspan=3, sticky="w", pady=(15, 8))

    tree_cols = ("produto", "preco", "oferta", "qtd")
    tree_etq = ttk.Treeview(frame_left, columns=tree_cols, show="headings", height=10)
    
    # Configurar estilo da tabela
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("Treeview", font=("Arial", 10), background="white", foreground="black", fieldbackground="white")
    style.configure("Treeview.Heading", font=("Arial", 11, "bold"), background="#3949ab", foreground="white")
    style.map("Treeview.Heading", background=[("active", "#5c6bc0")])
    
    tree_etq.heading("produto", text="Produto")
    tree_etq.heading("preco", text="Preço")
    tree_etq.heading("oferta", text="OFERTA")
    tree_etq.heading("qtd", text="Qtd")

    tree_etq.column("produto", width=240)
    tree_etq.column("preco", width=90)
    tree_etq.column("oferta", width=70, anchor="center")
    tree_etq.column("qtd", width=50, anchor="center")

    tree_etq.grid(row=6, column=0, columnspan=3, pady=5, sticky="nsew")

    # Ajusta weight da linha 6 para a tabela crescer
    frame_left.grid_rowconfigure(6, weight=1)

    ETIQUETAS = []  # lista de dicionários com as etiquetas

    def on_adicionar_etiqueta():
        nome = entry_nome.get().strip()
        preco_str = entry_preco.get().strip()
        qtd_str = entry_qtd.get().strip()
        oferta = var_oferta.get()

        if not nome or not preco_str or not qtd_str:
            messagebox.showwarning("Aviso", "Preencha nome, preço e quantidade.")
            return

        try:
            preco = float(preco_str.replace(",", "."))
        except ValueError:
            messagebox.showerror("Erro", "Preço inválido.")
            return

        try:
            qtd = int(qtd_str)
            if qtd <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Erro", "Quantidade inválida.")
            return

        etq = {
            "nome": nome,
            "preco": preco,
            "oferta": oferta,
            "qtd": qtd,
        }
        ETIQUETAS.append(etq)

        tree_etq.insert(
            "",
            "end",
            values=(
                nome,
                f"R$ {preco:.2f}",
                "SIM" if oferta else "NÃO",
                qtd,
            ),
        )

        # limpa apenas quantidade (para adicionar mais rápido)
        entry_qtd.delete(0, tk.END)
        entry_qtd.insert(0, "1")

    btn_add_etq = tk.Button(
        frame_left,
        text="➕ Adicionar Etiqueta",
        command=on_adicionar_etiqueta,
        bg="#00E676",
        fg="white",
        font=("Arial", 11, "bold"),
        relief="raised",
        bd=2,
        padx=10,
        pady=8,
        cursor="hand2",
        activebackground="#4CAF50"
    )
    btn_add_etq.grid(row=7, column=0, columnspan=3, pady=12, sticky="ew")

    def on_limpar_fila():
        ETIQUETAS.clear()
        for item in tree_etq.get_children():
            tree_etq.delete(item)

    btn_limpar = tk.Button(
        frame_left,
        text="🧹 Limpar Fila",
        command=on_limpar_fila,
        bg="#f44336",
        fg="white",
        font=("Arial", 11, "bold"),
        relief="raised",
        bd=2,
        padx=10,
        pady=8,
        cursor="hand2"
    )
    btn_limpar.grid(row=8, column=0, columnspan=3, pady=8, sticky="ew")

    # ====== FRAME DE PRÉ-VISUALIZAÇÃO (DIREITA) ======
    frame_right = tk.Frame(janela, bg="#3949ab")
    frame_right.pack(side="right", fill="both", expand=True, padx=15, pady=15)

    tk.Label(
        frame_right,
        text="Pré-visualização das Etiquetas (para impressão):",
        bg="#3949ab",
        fg="white",
        font=("Arial", 12, "bold"),
    ).pack(anchor="w", pady=10, padx=10)

    canvas = tk.Canvas(frame_right, bg="white")
    canvas.pack(fill="both", expand=True, padx=5, pady=5)

    def desenhar_etiquetas():
        canvas.delete("all")

        if not ETIQUETAS:
            canvas.create_text(
                10,
                10,
                anchor="nw",
                text="Nenhuma etiqueta na fila.",
                fill="black",
                font=("Arial", 12),
            )
            return

        # Configuração de grade de etiquetas
        margem_x = 20
        margem_y = 20
        largura = 200
        altura = 100
        espac_x = 10
        espac_y = 10
        colunas = 3  # 3 etiquetas por linha

        x = margem_x
        y = margem_y
        count = 0

        for etq in ETIQUETAS:
            for _ in range(etq["qtd"]):
                # Fundo amarelo
                canvas.create_rectangle(
                    x,
                    y,
                    x + largura,
                    y + altura,
                    fill="#FFF176",  # amarelo clarinho
                    outline="black",
                )

                # Se for oferta, escreve OFERTA em vermelho no topo
                if etq["oferta"]:
                    canvas.create_text(
                        x + largura / 2,
                        y + 20,
                        text="OFERTA",
                        fill="red",
                        font=("Arial", 14, "bold"),
                    )
                    offset_nome = 40
                else:
                    offset_nome = 25

                # Nome do produto (preto)
                canvas.create_text(
                    x + 10,
                    y + offset_nome,
                    anchor="w",
                    text=etq["nome"],
                    fill="black",
                    font=("Arial", 10, "bold"),
                )

                # Preço grande
                canvas.create_text(
                    x + largura / 2,
                    y + altura - 30,
                    text=f"R$ {etq['preco']:.2f}",
                    fill="black",
                    font=("Arial", 16, "bold"),
                )

                # Avança posição
                count += 1
                if count % colunas == 0:
                    x = margem_x
                    y += altura + espac_y
                else:
                    x += largura + espac_x

        # Ajusta scroll (se fosse usar scrollbar futuramente)
        canvas.config(scrollregion=canvas.bbox("all"))

    btn_preview = tk.Button(
        frame_left,
        text="👁️ Gerar Pré-visualização",
        command=desenhar_etiquetas,
        font=("Arial", 11, "bold"),
        relief="raised",
        bd=2,
        padx=10,
        pady=8,
        cursor="hand2"
    )
    btn_preview.grid(row=9, column=0, columnspan=3, pady=12, sticky="ew")

    # Ao abrir a tela, já mostra vazio
    desenhar_etiquetas()
