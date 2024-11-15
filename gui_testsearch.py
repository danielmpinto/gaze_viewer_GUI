


import tkinter as tk
import tkinter.filedialog as tkFileDialog
from tkinter.ttk import Label
from tkinter import ttk

root=tk.Tk()    

ent1=tk.Entry(root,font=40)
ent1.grid(row=2,column=1)
label = Label(root, text='Give the directory for processing overlayed')
label.grid(row=1, column=1)

start_button=tk.Button(root,text="START Processing",font=40)
start_button.grid(row=3,column=1)

progressbar = ttk.Progressbar(orient=tk.HORIZONTAL, length=160)
progressbar.grid(row=4, column=1)
progressbar.step(50)
b1=tk.Button(root,text="PATH",font=40,command=browsefunc)
b1.grid(row=2,column=4)

# ask for directory for compiling the overlayed movie
def browsefunc():
    # [] label asking the directory
    # [] directory selection
    # [] start button
    # [] progress bar
    
    filename =tkFileDialog.askdirectory()
    ent1.insert(tk.END, filename) 
    print(ent1.get())




root.mainloop()