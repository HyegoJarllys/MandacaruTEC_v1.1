import tkinter as tk
from tkinter import messagebox
<<<<<<< HEAD
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
=======
from ui_pdv import abrir_pdv  # importa a função nova do ui_pdv
>>>>>>> 2a8eb57eeecf608a6a2004611831a41f917b38e4


if __name__ == "__main__":
    try:
        # Abre o PDV principal
        abrir_pdv()

    except Exception as e:
        # Se der um erro muito grave, mostra uma caixinha
        root = tk.Tk()
        root.withdraw()  # esconde janela principal
        messagebox.showerror("Erro Fatal", f"Ocorreu um erro ao iniciar o PDV:\n{e}")
        root.destroy()

