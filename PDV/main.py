import tkinter as tk
from tkinter import messagebox
from ui_pdv import abrir_pdv

if __name__ == "__main__":
    try:
        abrir_pdv()
    except Exception as e:
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("Erro Fatal", f"Ocorreu um erro ao iniciar o PDV:\n{e}")
        root.destroy()
