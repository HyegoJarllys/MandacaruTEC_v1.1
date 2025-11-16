import os
from datetime import datetime
from tkinter import messagebox

from db import get_connection

# Tenta importar biblioteca de QR Code (pip install qrcode[pil])
try:
    import qrcode
except ImportError:
    qrcode = None


# ============================================================
# CARREGAR DADOS DA EMPRESA (para cabeçalho e PIX)
# ============================================================
def carregar_dados_empresa():
    """
    Tenta carregar os dados da empresa da tabela empresa_config.
    Se der erro ou não existir, usa dados genéricos.
    """
    dados = {
        "nome_fantasia": "SUA EMPRESA",
        "cnpj": "00.000.000/0000-00",
        "endereco": "Endereço não configurado",
        "cidade_uf": "Cidade/UF",
        "telefone": "(00) 0000-0000",
        "pix_chave": None,
    }

    try:
        conn = get_connection()
        cur = conn.cursor()
        # Ajuste conforme seu schema se necessário
        cur.execute(
            """
            SELECT nome_fantasia, cnpj, endereco, cidade_uf, telefone, pix_chave
            FROM empresa_config
            ORDER BY id DESC
            LIMIT 1;
            """
        )
        row = cur.fetchone()
        conn.close()

        if row:
            dados["nome_fantasia"] = row[0] or dados["nome_fantasia"]
            dados["cnpj"] = row[1] or dados["cnpj"]
            dados["endereco"] = row[2] or dados["endereco"]
            dados["cidade_uf"] = row[3] or dados["cidade_uf"]
            dados["telefone"] = row[4] or dados["telefone"]
            dados["pix_chave"] = row[5]

    except Exception:
        # Se der qualquer erro, usamos os dados default
        pass

    return dados


# ============================================================
# GERAR QR CODE PIX
# ============================================================
def gerar_qrcode_pix(total: float):
    """
    Gera um QR Code simples a partir da chave PIX da empresa.
    - Não é payload EMV completo homologado, mas serve para testes
      e muitos apps aceitam como “chave PIX dentro do QR”.
    Retorna o caminho do arquivo PNG ou None se não for possível.
    """
    dados = carregar_dados_empresa()
    chave = dados.get("pix_chave")

    if not chave or not qrcode:
        return None  # sem chave ou sem lib de qrcode

    # Texto que vai codificado no QR
    payload = f"PIX:{chave}|VALOR:{total:.2f}"

    pasta = os.path.join(os.path.dirname(__file__), "cupons")
    os.makedirs(pasta, exist_ok=True)

    filename = f"pix_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    caminho = os.path.join(pasta, filename)

    img = qrcode.make(payload)
    img.save(caminho)

    return caminho


# ============================================================
# GERAR CUPOM ESTILO MAQUININHA
# ============================================================
def gerar_cupom(resumo_venda: dict, tipo: str = "CLIENTE"):
    """
    Gera um cupom estilo maquininha (cliente ou caixa).
    - Salva em arquivo .txt na pasta /cupons
    - Formatação em largura fixa para impressão em bobina
    """
    dados = carregar_dados_empresa()

    pasta = os.path.join(os.path.dirname(__file__), "cupons")
    os.makedirs(pasta, exist_ok=True)

    venda_id = resumo_venda.get("id_venda") or "SEM_ID"
    filename = f"cupom_{venda_id}_{tipo.upper()}.txt"
    caminho = os.path.join(pasta, filename)

    largura = 40  # caracteres por linha (estilo bobina)
    linhas = []

    def linha(texto=""):
        linhas.append(texto[:largura])

    def centro(texto):
        texto = texto[:largura]
        espacos = (largura - len(texto)) // 2
        linhas.append(" " * espacos + texto)

    def separador():
        linhas.append("-" * largura)

    # Cabeçalho
    centro(dados["nome_fantasia"])
    linha(f"CNPJ: {dados['cnpj']}")
    linha(dados["endereco"])
    linha(dados["cidade_uf"])
    linha(f"Tel: {dados['telefone']}")
    separador()

    # Dados venda
    linha(f"VENDA: {venda_id}")
    linha(f"DATA: {resumo_venda.get('data_hora', '-')}")
    separador()

    # Itens
    linha("ITENS")
    linha("QTD DESC          VL.UN   VL.TOT")
    separador()
    for item in resumo_venda.get("itens", []):
        desc = item["descricao"][:12].upper()
        qtd = f"{item['quantidade']:.0f}"
        unit = f"{item['preco_unit']:.2f}"
        sub = f"{item['subtotal']:.2f}"

        linha(f"{qtd:>3} {desc:<12} {unit:>7} {sub:>7}")

    separador()
    total = resumo_venda.get("total", 0.0)
    linha(f"TOTAL: R$ {total:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    fpag = resumo_venda.get("forma_pagamento") or "-"
    linha(f"PAGAMENTO: {fpag}")

    valor_recebido = resumo_venda.get("valor_recebido")
    troco = resumo_venda.get("troco")

    if valor_recebido is not None:
        linha(
            "RECEBIDO: R$ "
            + f"{valor_recebido:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        )
    if troco is not None:
        linha(
            "TROCO:    R$ "
            + f"{troco:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        )

    separador()
    centro("OBRIGADO PELA PREFERÊNCIA!")
    centro("SISTEMA MANDACARU TEC")
    separador()

    # Salvar em arquivo
    with open(caminho, "w", encoding="utf-8") as f:
        f.write("\n".join(linhas))

    # Aviso rápido (sem travar a venda)
    try:
        messagebox.showinfo(
            "Cupom gerado",
            f"Cupom ({tipo}) salvo em:\n{caminho}",
        )
    except Exception:
        pass

    return caminho
