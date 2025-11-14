import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
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



def abrir_relatorio_caixa_dia(parent=None):
    """Abre uma janela com o resumo de caixa do dia atual."""

    hoje_str = datetime.now().strftime("%d/%m/%Y")

    conn = get_connection()
    cur = conn.cursor()

    # Busca vendas do dia
    cur.execute(
        """
        SELECT id, data_hora, total, forma_pagamento, valor_recebido, troco, lucro_total
        FROM vendas
        WHERE substr(data_hora, 1, 10) = ?
        ORDER BY id DESC;
        """,
        (hoje_str,),
    )
    vendas = cur.fetchall()
    conn.close()

    if not vendas:
        messagebox.showinfo(
            "Relatório de Caixa",
            f"Não há vendas registradas em {hoje_str}."
        )
        return

    # Cálculos de resumo
    total_geral = sum(v["total"] for v in vendas)
    qtd_vendas = len(vendas)
    total_dinheiro = sum(
        v["total"] for v in vendas if v["forma_pagamento"].lower() == "dinheiro"
    )
    total_pix = sum(
        v["total"] for v in vendas if v["forma_pagamento"].lower() == "pix"
    )
    lucro_geral = sum(v["lucro_total"] for v in vendas)

    ticket_medio_venda = total_geral / qtd_vendas if qtd_vendas else 0.0
    ticket_medio_lucro = lucro_geral / qtd_vendas if qtd_vendas else 0.0
    margem_media = (lucro_geral / total_geral * 100) if total_geral > 0 else 0.0

    # Janela do relatório
    if parent is None:
        janela = tk.Toplevel()
    else:
        janela = tk.Toplevel(parent)

    janela.title(f"Relatório de Caixa - {hoje_str}")
    janela.geometry("900x650")
    janela.configure(bg="#1a237e")
    
    # Aplicar ícone de cacto
    aplicar_icone_cacto(janela)

    titulo = tk.Label(
        janela,
        text=f"Relatório de Caixa - {hoje_str}",
        font=("Arial", 18, "bold"),
        bg="#1a237e",
        fg="white"
    )
    titulo.pack(pady=15)

    # Frame para o resumo com fundo destacado
    frame_resumo = tk.Frame(janela, bg="#3949ab", relief="raised", bd=2)
    frame_resumo.pack(fill="x", padx=15, pady=10)
    
    resumo_lbl = tk.Label(
        frame_resumo,
        text=(
            f"Total Geral: R$ {total_geral:.2f}   |   "
            f"Vendas: {qtd_vendas}   |   "
            f"Ticket Médio Venda: R$ {ticket_medio_venda:.2f}\n"
            f"Lucro Total: R$ {lucro_geral:.2f}   |   "
            f"Ticket Médio Lucro: R$ {ticket_medio_lucro:.2f}   |   "
            f"Margem Média: {margem_media:.1f}%\n"
            f"Dinheiro: R$ {total_dinheiro:.2f}   |   "
            f"PIX: R$ {total_pix:.2f}"
        ),
        bg="#3949ab",
        fg="white",
        font=("Arial", 11, "bold"),
        justify="left",
    )
    resumo_lbl.pack(pady=12, padx=10)

    # Tabela de vendas
    frame_tab = tk.Frame(janela, bg="#283593")
    frame_tab.pack(fill="both", expand=True, padx=15, pady=10)

    colunas = ("id", "hora", "forma", "total", "lucro")
    tree = ttk.Treeview(frame_tab, columns=colunas, show="headings", height=18)
    
    # Configurar estilo da tabela
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("Treeview", font=("Arial", 10), background="white", foreground="black", fieldbackground="white")
    style.configure("Treeview.Heading", font=("Arial", 11, "bold"), background="#3949ab", foreground="white")
    style.map("Treeview.Heading", background=[("active", "#5c6bc0")])
    
    tree.heading("id", text="ID")
    tree.heading("hora", text="Hora")
    tree.heading("forma", text="Forma Pagto")
    tree.heading("total", text="Total (R$)")
    tree.heading("lucro", text="Lucro (R$)")

    tree.column("id", width=60, anchor="center")
    tree.column("hora", width=140, anchor="center")
    tree.column("forma", width=180, anchor="center")
    tree.column("total", width=150, anchor="e")
    tree.column("lucro", width=150, anchor="e")

    tree.pack(side="left", fill="both", expand=True)

    scrollbar = ttk.Scrollbar(frame_tab, orient="vertical", command=tree.yview)
    scrollbar.pack(side="right", fill="y")
    tree.configure(yscrollcommand=scrollbar.set)

    for v in vendas:
        hora = v["data_hora"][11:]  # pega só HH:MM:SS
        tree.insert(
            "",
            "end",
            values=(
                v["id"],
                hora,
                v["forma_pagamento"],
                f"{v['total']:.2f}",
                f"{v['lucro_total']:.2f}",
            ),
        )

    btn_fechar = tk.Button(
        janela, 
        text="❌ Fechar", 
        command=janela.destroy,
        font=("Arial", 11, "bold"),
        relief="raised",
        bd=2,
        padx=20,
        pady=8,
        cursor="hand2",
        bg="#555555",
        fg="white"
    )
    btn_fechar.pack(pady=15)
