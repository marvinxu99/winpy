from tkinter import *
from tkinter import ttk
from tkinter import messagebox


class Window(Frame):
    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.master = master

        menu = Menu(self.master)
        self.master.config(menu=menu)

        fileMenu = Menu(menu) 
        fileMenu.add_command(label="Item")
        fileMenu.add_command(label="Exit", command=self.exitProgram)
        menu.add_cascade(label="File", menu=fileMenu)

        editMenu = Menu(menu)
        editMenu.add_command(label="Undo")
        editMenu.add_command(label="Redo")
        menu.add_cascade(label="Edit", menu=editMenu)

    def exitProgram(self):
        exit()

if __name__ == "__main__":        
    root = Tk()
    app = Window(root)
    root.wm_title("Tkinter window")
    root.mainloop()
