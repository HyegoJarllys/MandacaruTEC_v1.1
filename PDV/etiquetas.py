import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

from PIL import Image, ImageDraw, ImageFont, ImageTk
from reportlab.pdfgen import canvas as pdf_canvas
from reportlab.lib.pagesizes import A4

# importa conexão com o banco
from db import get_connection

# ==============================
# BUSCA PRODUTO NO BD PELO CÓDIGO
# ==============================

def buscar_produto_por_codigo(codigo_barras: str):
    """
    Retorna 1 produto pelo código de barras.
    Espera uma tabela produtos com, no mínimo:
    id, codigo_barras, nome, preco (ou preco_venda).
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT * FROM produtos WHERE codigo_barras = ?;",
        (codigo_barras,),
    )
    row = cur.fetchone()
    conn.close()
    return row

# ==============================
# FONTES (tenta Arial do Windows, senão usa padrão)
# ==============================

def carregar_fonte(nome_arquivo, tamanho):
    caminhos = [
        nome_arquivo,
        os.path.join("C:\\", "Windows", "Fonts", nome_arquivo),
        os.path.join("C:\\", "Windows", "Fonts", nome_arquivo.upper()),
    ]
    for caminho in caminhos:
        try:
            return ImageFont.truetype(caminho, tamanho)
        except Exception:
            continue
    return ImageFont.load_default()


FONT_BOLD_G = carregar_fonte("arialbd.ttf", 80)
FONT_BOLD_M = carregar_fonte("arialbd.ttf", 52)
FONT_BOLD_P = carregar_fonte("arialbd.ttf", 34)
FONT_REG_P = carregar_fonte("arial.ttf", 26)

# ==============================
# CORES PADRÃO ATACAREJO
# ==============================

COR_AMARELO = (250, 204, 21)
COR_AMARELO_CLARO = (253, 230, 138)
COR_VERMELHO = (239, 68, 68)
COR_VERMELHO_ESCURO = (185, 28, 28)
COR_AZUL = (37, 99, 235)
COR_PRETO = (0, 0, 0)
COR_BRANCO = (255, 255, 255)

# ==============================
# HELPERS
# ==============================

def rounded_rectangle(draw, xy, radius, fill):
    draw.rounded_rectangle(xy, radius=radius, fill=fill)

def texto_centro(draw, x, y, texto, font, fill):
    draw.text((x, y), texto, font=font, fill=fill, anchor="mm")

def format_preco(valor_str):
    if not valor_str:
        return ""
    try:
        v = float(str(valor_str).replace(",", "."))
    except ValueError:
        return ""
    s = f"{v:,.2f}"
    s = s.replace(",", "X").replace(".", ",").replace("X", ".")
    return f"R$ {s}"

# ==============================
# TEMPLATES / MODELOS
# ==============================

TEMPLATES = {
    "SÓ HOJE": {
        "size": (900, 450),
        "draw": "draw_so_hoje",
    },
    "OFERTA": {
        "size": (900, 450),
        "draw": "draw_oferta",
    },
    "OFERTA DA SEMANA": {
        "size": (900, 450),
        "draw": "draw_oferta_semana",
    },
    "COMBO": {
        "size": (700, 900),
        "draw": "draw_combo",
    },
    "LEVE X POR Y": {
        "size": (900, 450),
        "draw": "draw_leve_x_por_y",
    },
    "MEGA DESCONTO": {
        "size": (700, 900),
        "draw": "draw_mega_desconto",
    },
}

# ==============================
# FUNÇÕES DE DESENHO POR MODELO
# ==============================

def draw_so_hoje(dados):
    w, h = TEMPLATES["SÓ HOJE"]["size"]
    img = Image.new("RGB", (w, h), COR_BRANCO)
    d = ImageDraw.Draw(img)

    rounded_rectangle(d, (0, 0, w, h), 26, COR_BRANCO)
    d.rectangle((0, 0, w, int(h * 0.45)), fill=COR_AMARELO)

    texto_centro(d, w / 2, h * 0.20, "SÓ HOJE", FONT_BOLD_M, COR_PRETO)

    preco_fmt = format_preco(dados.get("preco"))
    texto_centro(d, w / 2, h * 0.68, preco_fmt, FONT_BOLD_G, COR_PRETO)

    und = (dados.get("unidade") or "").upper().strip()
    if und:
        texto_centro(d, w / 2, h * 0.88, und, FONT_REG_P, COR_PRETO)

    return img


def draw_oferta(dados):
    w, h = TEMPLATES["OFERTA"]["size"]
    img = Image.new("RGB", (w, h), COR_AMARELO)
    d = ImageDraw.Draw(img)

    rounded_rectangle(d, (0, 0, w, h), 26, COR_AMARELO)
    d.rectangle((0, 0, w, int(h * 0.42)), fill=COR_VERMELHO)

    texto_centro(d, w / 2, h * 0.20, "OFERTA", FONT_BOLD_M, COR_BRANCO)

    preco_fmt = format_preco(dados.get("preco"))
    texto_centro(d, w / 2, h * 0.70, preco_fmt, FONT_BOLD_G, COR_PRETO)

    und = (dados.get("unidade") or "").upper().strip()
    if und:
        texto_centro(d, w / 2, h * 0.88, und, FONT_REG_P, COR_PRETO)

    return img


def draw_oferta_semana(dados):
    w, h = TEMPLATES["OFERTA DA SEMANA"]["size"]
    img = Image.new("RGB", (w, h), COR_BRANCO)
    d = ImageDraw.Draw(img)

    rounded_rectangle(d, (0, 0, w, h), 26, COR_BRANCO)
    d.rectangle((0, 0, w, int(h * 0.40)), fill=COR_VERMELHO_ESCURO)

    texto_centro(d, w / 2, h * 0.20, "OFERTA DA SEMANA", FONT_BOLD_M, COR_BRANCO)

    preco_fmt = format_preco(dados.get("preco"))
    texto_centro(d, w * 0.25, h * 0.66, preco_fmt, FONT_BOLD_G, COR_PRETO)

    economia = dados.get("economia")
    if economia:
        econ_fmt = format_preco(economia)
        txt = f"Você economiza {econ_fmt}"
        d.text((w * 0.05, h * 0.84), txt, font=FONT_REG_P, fill=COR_PRETO, anchor="lm")

    return img


def draw_combo(dados):
    w, h = TEMPLATES["COMBO"]["size"]
    img = Image.new("RGB", (w, h), COR_BRANCO)
    d = ImageDraw.Draw(img)

    rounded_rectangle(d, (0, 0, w, h), 26, COR_BRANCO)

    texto_centro(d, w / 2, h * 0.12, "COMBO", FONT_BOLD_M, COR_PRETO)

    d.rectangle((0, int(h * 0.20), w, int(h * 0.42)), fill=COR_AMARELO)

    preco_unit = dados.get("preco_unit")
    und = (dados.get("unidade") or "UND.").upper().strip()
    if preco_unit:
        txt_unit = f"{format_preco(preco_unit)} {und}"
        texto_centro(d, w / 2, h * 0.31, txt_unit, FONT_BOLD_P, COR_PRETO)

    preco_total = dados.get("preco")
    preco_total_fmt = format_preco(preco_total)
    texto_centro(d, w / 2, h * 0.70, preco_total_fmt, FONT_BOLD_G, COR_PRETO)

    return img


def draw_leve_x_por_y(dados):
    w, h = TEMPLATES["LEVE X POR Y"]["size"]
    img = Image.new("RGB", (w, h), COR_BRANCO)
    d = ImageDraw.Draw(img)

    rounded_rectangle(d, (0, 0, w, h), 26, COR_BRANCO)

    qtd_combo = dados.get("qtd_combo") or ""
    txt_topo = f"LEVE {qtd_combo}".strip()

    d.rectangle((0, 0, w, int(h * 0.50)), fill=COR_AZUL)

    texto_centro(d, w / 2, h * 0.18, txt_topo, FONT_BOLD_M, COR_BRANCO)
    texto_centro(d, w / 2, h * 0.36, "POR", FONT_BOLD_G, COR_BRANCO)

    preco_fmt = format_preco(dados.get("preco"))
    texto_centro(d, w * 0.30, h * 0.76, preco_fmt, FONT_BOLD_G, COR_PRETO)

    return img


def draw_mega_desconto(dados):
    w, h = TEMPLATES["MEGA DESCONTO"]["size"]
    img = Image.new("RGB", (w, h), COR_VERMELHO)
    d = ImageDraw.Draw(img)

    rounded_rectangle(d, (0, 0, w, h), 26, COR_VERMELHO)

    texto_centro(d, w / 2, h * 0.18, "MEGA", FONT_BOLD_M, COR_AMARELO)
    texto_centro(d, w / 2, h * 0.34, "DESCONTO", FONT_BOLD_M, COR_AMARELO)

    preco_fmt = format_preco(dados.get("preco"))
    texto_centro(d, w / 2, h * 0.70, preco_fmt, FONT_BOLD_G, COR_AMARELO_CLARO)

    return img


DRAW_FUNCS = {
    "SÓ HOJE": draw_so_hoje,
    "OFERTA": draw_oferta,
    "OFERTA DA SEMANA": draw_oferta_semana,
    "COMBO": draw_combo,
    "LEVE X POR Y": draw_leve_x_por_y,
    "MEGA DESCONTO": draw_mega_desconto,
}

# ==============================
# EXPORTAÇÃO PARA PDF
# ==============================

def exportar_pdf(lista_imagens):
    if not lista_imagens:
        messagebox.showwarning("Aviso", "Nenhuma etiqueta gerada.")
        return

    caminho = filedialog.asksaveasfilename(
        defaultextension=".pdf",
        filetypes=[("PDF", "*.pdf")],
        title="Salvar etiquetas em PDF",
    )
    if not caminho:
        return

    largura_pagina, altura_pagina = A4
    c = pdf_canvas.Canvas(caminho, pagesize=A4)

    margem_x = 30
    margem_y = 40
    espac_x = 15
    espac_y = 15

    x = margem_x
    y = altura_pagina - margem_y

    largura_max = (largura_pagina - 2 * margem_x - 2 * espac_x) / 3  # 3 por linha

    for img in lista_imagens:
        w, h = img.size
        fator = largura_max / w
        new_w = largura_max
        new_h = h * fator

        tmp_path = "_tmp_etq.png"
        img.resize((int(new_w), int(new_h)), Image.LANCZOS).save(tmp_path)

        y_img = y - new_h
        c.drawImage(tmp_path, x, y_img, width=new_w, height=new_h)

        x += new_w + espac_x
        if x + new_w > largura_pagina - margem_x:
            x = margem_x
            y -= new_h + espac_y
            if y - new_h < margem_y:
                c.showPage()
                y = altura_pagina - margem_y

    c.save()
    if os.path.exists("_tmp_etq.png"):
        os.remove("_tmp_etq.png")

    messagebox.showinfo("Sucesso", "PDF gerado com sucesso!")

# ==============================
# JANELA TKINTER (MODO ETIQUETAS)
# ==============================

def abrir_etiquetas(parent=None):
    janela = tk.Toplevel(parent) if parent is not None else tk.Toplevel()
    janela.title("Mandacaru TEC - Modo Etiquetas")
    janela.geometry("1200x700")
    janela.configure(bg="#f5f5f5")

    frame_left = tk.Frame(janela, bg="#f5f5f5")
    frame_left.pack(side="left", fill="y", padx=10, pady=10)

    row = 0

    # ---- CÓDIGO DE BARRAS + BUSCAR ----
    tk.Label(frame_left, text="Código de Barras:", bg="#f5f5f5").grid(
        row=row, column=0, sticky="w"
    )
    entry_codigo = tk.Entry(frame_left, width=16)
    entry_codigo.grid(row=row, column=1, padx=5, pady=3, sticky="w")

    def on_buscar():
        codigo = entry_codigo.get().strip()
        if not codigo:
            messagebox.showwarning("Aviso", "Digite o código de barras.")
            return
        try:
            prod = buscar_produto_por_codigo(codigo)
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao buscar produto:\n{e}")
            return

        if not prod:
            messagebox.showerror("Erro", "Produto não encontrado.")
            return

        # tenta pegar 'preco' ou 'preco_venda'
        preco = None
        try:
            if isinstance(prod, dict) or hasattr(prod, "keys"):
                if "preco" in prod.keys():
                    preco = prod["preco"]
                elif "preco_venda" in prod.keys():
                    preco = prod["preco_venda"]
                if "unidade" in prod.keys():
                    und = (prod["unidade"] or "").upper().strip()
                    if und:
                        entry_unidade.delete(0, tk.END)
                        entry_unidade.insert(0, und)
            else:
                # fallback em caso de tupla: id, codigo, nome, preco
                if len(prod) >= 4:
                    preco = prod[3]
        except Exception:
            pass

        if preco is not None:
            try:
                preco = float(preco)
                entry_preco.delete(0, tk.END)
                entry_preco.insert(0, f"{preco:.2f}")
            except Exception:
                pass

    btn_buscar = tk.Button(frame_left, text="Buscar", command=on_buscar)
    btn_buscar.grid(row=row, column=2, padx=5, pady=3, sticky="w")

    entry_codigo.bind("<Return>", lambda e: on_buscar())

    row += 1

    # ---- CAMPOS DE CONFIGURAÇÃO ----
    tk.Label(frame_left, text="Modelo:", bg="#f5f5f5").grid(row=row, column=0, sticky="w")
    modelos = list(TEMPLATES.keys())
    combo_modelo = ttk.Combobox(frame_left, values=modelos, width=20, state="readonly")
    combo_modelo.set("OFERTA")
    combo_modelo.grid(row=row, column=1, padx=5, pady=3, sticky="w", columnspan=2)
    row += 1

    tk.Label(frame_left, text="Preço:", bg="#f5f5f5").grid(row=row, column=0, sticky="w")
    entry_preco = tk.Entry(frame_left, width=12)
    entry_preco.grid(row=row, column=1, padx=5, pady=3, sticky="w", columnspan=2)
    row += 1

    tk.Label(frame_left, text="UND/KG:", bg="#f5f5f5").grid(row=row, column=0, sticky="w")
    entry_unidade = tk.Entry(frame_left, width=12)
    entry_unidade.insert(0, "UND.")
    entry_unidade.grid(row=row, column=1, padx=5, pady=3, sticky="w", columnspan=2)
    row += 1

    tk.Label(frame_left, text="Economia (R$):", bg="#f5f5f5").grid(row=row, column=0, sticky="w")
    entry_economia = tk.Entry(frame_left, width=12)
    entry_economia.grid(row=row, column=1, padx=5, pady=3, sticky="w", columnspan=2)
    row += 1

    tk.Label(frame_left, text="Qtd. combo (LEVE X):", bg="#f5f5f5").grid(row=row, column=0, sticky="w")
    entry_qtd_combo = tk.Entry(frame_left, width=12)
    entry_qtd_combo.grid(row=row, column=1, padx=5, pady=3, sticky="w", columnspan=2)
    row += 1

    tk.Label(frame_left, text="Preço combo:", bg="#f5f5f5").grid(row=row, column=0, sticky="w")
    entry_preco_combo = tk.Entry(frame_left, width=12)
    entry_preco_combo.grid(row=row, column=1, padx=5, pady=3, sticky="w", columnspan=2)
    row += 1

    tk.Label(frame_left, text="Qtd de cópias:", bg="#f5f5f5").grid(row=row, column=0, sticky="w")
    entry_qtd_copias = tk.Entry(frame_left, width=12)
    entry_qtd_copias.insert(0, "1")
    entry_qtd_copias.grid(row=row, column=1, padx=5, pady=3, sticky="w", columnspan=2)
    row += 1

    imagens_geradas = []
    preview_img_tk = {"img": None}

    frame_preview = tk.Frame(janela, bg="#dddddd")
    frame_preview.pack(side="right", fill="both", expand=True, padx=10, pady=10)

    tk.Label(
        frame_preview,
        text="Pré-visualização da etiqueta:",
        bg="#dddddd",
        font=("Segoe UI", 10, "bold"),
    ).pack(anchor="w", pady=5, padx=5)

    canvas_preview = tk.Canvas(frame_preview, bg="white")
    canvas_preview.pack(fill="both", expand=True, padx=5, pady=5)

    def atualizar_preview(img):
        canvas_preview.delete("all")
        if img is None:
            return

        w, h = img.size
        max_w, max_h = 700, 450
        fator = min(max_w / w, max_h / h, 1)
        new_w = int(w * fator)
        new_h = int(h * fator)

        img_resized = img.resize((new_w, new_h), Image.LANCZOS)
        img_tk = ImageTk.PhotoImage(img_resized)
        preview_img_tk["img"] = img_tk

        cw = int(canvas_preview.winfo_width() or max_w)
        ch = int(canvas_preview.winfo_height() or max_h)

        canvas_preview.create_image(cw // 2, ch // 2, image=img_tk, anchor="center")

    def gerar_etiqueta():
        modelo = combo_modelo.get()

        dados = {
            "preco": entry_preco.get().strip(),
            "unidade": entry_unidade.get().strip(),
            "economia": entry_economia.get().strip(),
            "qtd_combo": entry_qtd_combo.get().strip(),
            "preco_combo": entry_preco_combo.get().strip(),
        }

        preco_combo_float = None
        qtd_combo_int = None
        try:
            if dados["preco_combo"]:
                preco_combo_float = float(dados["preco_combo"].replace(",", "."))
        except ValueError:
            preco_combo_float = None
        try:
            if dados["qtd_combo"]:
                qtd_combo_int = int(dados["qtd_combo"])
        except ValueError:
            qtd_combo_int = None

        if modelo == "COMBO" and preco_combo_float and qtd_combo_int and qtd_combo_int > 0:
            dados["preco_unit"] = preco_combo_float / qtd_combo_int
        else:
            dados["preco_unit"] = None

        func_draw = DRAW_FUNCS.get(modelo)
        if not func_draw:
            messagebox.showerror("Erro", f"Modelo '{modelo}' não suportado.")
            return

        img = func_draw(dados)
        imagens_geradas.clear()

        try:
            copias = int(entry_qtd_copias.get().strip())
        except ValueError:
            copias = 1
        copias = max(1, copias)

        for _ in range(copias):
            imagens_geradas.append(img.copy())

        atualizar_preview(img)

    def salvar_png():
        if not imagens_geradas:
            messagebox.showwarning("Aviso", "Nenhuma etiqueta gerada.")
            return
        caminho = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG", "*.png")],
            title="Salvar etiqueta em PNG",
        )
        if not caminho:
            return
        imagens_geradas[0].save(caminho)
        messagebox.showinfo("Sucesso", "PNG salvo com sucesso!")

    def salvar_pdf():
        if not imagens_geradas:
            messagebox.showwarning("Aviso", "Nenhuma etiqueta gerada.")
            return
        exportar_pdf(imagens_geradas)

    tk.Button(
        frame_left,
        text="Gerar Etiqueta",
        command=gerar_etiqueta,
        bg="#111111",
        fg="white",
    ).grid(row=row, column=0, columnspan=3, pady=(12, 4), sticky="ew")
    row += 1

    tk.Button(
        frame_left,
        text="Salvar PNG",
        command=salvar_png,
        bg="#e5e5e5",
        fg="#111111",
    ).grid(row=row, column=0, columnspan=3, pady=2, sticky="ew")
    row += 1

    tk.Button(
        frame_left,
        text="Exportar PDF (A4)",
        command=salvar_pdf,
        bg="#e5e5e5",
        fg="#111111",
    ).grid(row=row, column=0, columnspan=3, pady=2, sticky="ew")
    row += 1

    janela.after(200, lambda: atualizar_preview(None))
    return janela

# ==============================
# FUNÇÃO QUE O PDV CHAMA
# ==============================

def abrir_modo_etiquetas(parent=None):
    abrir_etiquetas(parent)
