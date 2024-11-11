import tkinter as tk

def main():
    root = tk.Tk()
    root.title("Minha Aplicação Tkinter")
    label = tk.Label(root, text="Olá, Tkinter!")
    label.pack(padx=20, pady=20)
    button = tk.Button(root, text="Sair", command=root.quit)
    button.pack(pady=10)
    root.mainloop()

if __name__ == "__main__":
    main()
