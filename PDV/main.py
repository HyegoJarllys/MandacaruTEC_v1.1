import tkinter as tk
from tkinter import messagebox
from ui_pdv import abrir_pdv  # importa a função nova do ui_pdv


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

