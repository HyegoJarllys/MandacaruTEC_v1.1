import tkinter as tk
from tkinter import messagebox
from db import get_connection

_janela_config = None  # para não abrir mais de uma janela


def carregar_dados_empresa():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM empresa_config WHERE id = 1;")
    row = cur.fetchone()
    conn.close()
    return row


def salvar_dados_empresa(campos):
    (
        entry_nome_fantasia,
        entry_razao_social,
        entry_cnpj,
        entry_ie,
        entry_endereco,
        entry_bairro,
        entry_cidade,
        entry_uf,
        entry_telefone,
        entry_pix_chave,
    ) = campos

    nome_fantasia = entry_nome_fantasia.get().strip()
    razao_social = entry_razao_social.get().strip()
    cnpj = entry_cnpj.get().strip()
    ie = entry_ie.get().strip()
    endereco = entry_endereco.get().strip()
    bairro = entry_bairro.get().strip()
    cidade = entry_cidade.get().strip()
    uf = entry_uf.get().strip()
    telefone = entry_telefone.get().strip()
    pix_chave = entry_pix_chave.get().strip()

    if not nome_fantasia:
        messagebox.showwarning("Aviso", "Informe pelo menos o Nome Fantasia.")
        return

    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        UPDATE empresa_config
        SET nome_fantasia = ?, razao_social = ?, cnpj = ?, ie = ?,
            endereco = ?, bairro = ?, cidade = ?, uf = ?, telefone = ?, pix_chave = ?
        WHERE id = 1;
        """,
        (
            nome_fantasia,
            razao_social,
            cnpj,
            ie,
            endereco,
            bairro,
            cidade,
            uf,
            telefone,
            pix_chave,
        ),
    )
    conn.commit()
    conn.close()

    messagebox.showinfo("Sucesso", "Dados da empresa salvos com sucesso.")


def abrir_config_empresa(parent=None):
    global _janela_config

    # Se já estiver aberta, só traz pra frente
    if _janela_config is not None:
        try:
            if _janela_config.winfo_exists():
                _janela_config.lift()
                _janela_config.focus_force()
                return
        except tk.TclError:
            _janela_config = None

    if parent is None:
        janela = tk.Tk()
    else:
        janela = tk.Toplevel(parent)

    _janela_config = janela

    def on_close():
        global _janela_config
        try:
            janela.destroy()
        finally:
            _janela_config = None

    janela.protocol("WM_DELETE_WINDOW", on_close)

    janela.title("Configuração da Empresa")
    janela.geometry("700x450")
    janela.configure(bg="#f7f7f7")

    frame = tk.Frame(janela, bg="#f7f7f7")
    frame.pack(fill="both", expand=True, padx=10, pady=10)

    # Linhas de campos
    linha = 0

    tk.Label(frame, text="Nome Fantasia:", bg="#f7f7f7").grid(row=linha, column=0, sticky="w")
    entry_nome_fantasia = tk.Entry(frame, width=50)
    entry_nome_fantasia.grid(row=linha, column=1, padx=5, pady=3, sticky="w")
    linha += 1

    tk.Label(frame, text="Razão Social:", bg="#f7f7f7").grid(row=linha, column=0, sticky="w")
    entry_razao_social = tk.Entry(frame, width=50)
    entry_razao_social.grid(row=linha, column=1, padx=5, pady=3, sticky="w")
    linha += 1

    tk.Label(frame, text="CNPJ:", bg="#f7f7f7").grid(row=linha, column=0, sticky="w")
    entry_cnpj = tk.Entry(frame, width=30)
    entry_cnpj.grid(row=linha, column=1, padx=5, pady=3, sticky="w")
    linha += 1

    tk.Label(frame, text="Inscrição Estadual (IE):", bg="#f7f7f7").grid(row=linha, column=0, sticky="w")
    entry_ie = tk.Entry(frame, width=30)
    entry_ie.grid(row=linha, column=1, padx=5, pady=3, sticky="w")
    linha += 1

    tk.Label(frame, text="Endereço:", bg="#f7f7f7").grid(row=linha, column=0, sticky="w")
    entry_endereco = tk.Entry(frame, width=50)
    entry_endereco.grid(row=linha, column=1, padx=5, pady=3, sticky="w")
    linha += 1

    tk.Label(frame, text="Bairro:", bg="#f7f7f7").grid(row=linha, column=0, sticky="w")
    entry_bairro = tk.Entry(frame, width=30)
    entry_bairro.grid(row=linha, column=1, padx=5, pady=3, sticky="w")
    linha += 1

    tk.Label(frame, text="Cidade:", bg="#f7f7f7").grid(row=linha, column=0, sticky="w")
    entry_cidade = tk.Entry(frame, width=30)
    entry_cidade.grid(row=linha, column=1, padx=5, pady=3, sticky="w")
    linha += 1

    tk.Label(frame, text="UF:", bg="#f7f7f7").grid(row=linha, column=0, sticky="w")
    entry_uf = tk.Entry(frame, width=5)
    entry_uf.grid(row=linha, column=1, padx=5, pady=3, sticky="w")
    linha += 1

    tk.Label(frame, text="Telefone:", bg="#f7f7f7").grid(row=linha, column=0, sticky="w")
    entry_telefone = tk.Entry(frame, width=20)
    entry_telefone.grid(row=linha, column=1, padx=5, pady=3, sticky="w")
    linha += 1

    tk.Label(frame, text="Chave PIX:", bg="#f7f7f7").grid(row=linha, column=0, sticky="w")
    entry_pix_chave = tk.Entry(frame, width=40)
    entry_pix_chave.grid(row=linha, column=1, padx=5, pady=3, sticky="w")
    linha += 1

    campos = (
        entry_nome_fantasia,
        entry_razao_social,
        entry_cnpj,
        entry_ie,
        entry_endereco,
        entry_bairro,
        entry_cidade,
        entry_uf,
        entry_telefone,
        entry_pix_chave,
    )

    # Botão salvar
    btn_salvar = tk.Button(
        frame,
        text="Salvar",
        bg="#4CAF50",
        fg="white",
        command=lambda: salvar_dados_empresa(campos),
    )
    btn_salvar.grid(row=linha, column=1, pady=15, sticky="w")

    # Carregar dados existentes
    dados = carregar_dados_empresa()
    if dados:
        (
            _id,
            nome_fantasia,
            razao_social,
            cnpj,
            ie,
            endereco,
            bairro,
            cidade,
            uf,
            telefone,
            pix_chave,
        ) = dados

        entry_nome_fantasia.insert(0, nome_fantasia or "")
        entry_razao_social.insert(0, razao_social or "")
        entry_cnpj.insert(0, cnpj or "")
        entry_ie.insert(0, ie or "")
        entry_endereco.insert(0, endereco or "")
        entry_bairro.insert(0, bairro or "")
        entry_cidade.insert(0, cidade or "")
        entry_uf.insert(0, uf or "")
        entry_telefone.insert(0, telefone or "")
        entry_pix_chave.insert(0, pix_chave or "")

    entry_nome_fantasia.focus_set()

    if parent is None:
        janela.mainloop()


if __name__ == "__main__":
    abrir_config_empresa()
