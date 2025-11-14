import tkinter as tk
from tkinter import messagebox
from ui_pdv import criar_interface_pdv, aplicar_icone_cacto


def iniciar_pdv():
    janela = tk.Tk()
    janela.title("Mandacaru TEC – PDV")
    janela.geometry("900x600")
    janela.configure(bg="#f7f7f7")
    
    # Aplicar ícone de cacto
    aplicar_icone_cacto(janela)

    criar_interface_pdv(janela)

    janela.mainloop()


if __name__ == "__main__":
    try:
        iniciar_pdv()
    except Exception as e:
        messagebox.showerror("Erro Fatal", f"Ocorreu um erro ao iniciar o PDV:\n{e}")
