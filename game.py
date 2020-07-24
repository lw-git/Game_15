import tkinter as tk


class Application(tk.Frame):

    def __init__(self, *args, **kwargs):
        tk.Frame.__init__(self, *args, **kwargs)

        # -----------------Variables-----------------------------
        self.cell_size = 150

        # -----------------Widgets-------------------------------
        self.canvas = tk.Canvas(root, width=4 * self.cell_size,
                                height=4 * self.cell_size, bg='white')
        self.canvas.pack()


if __name__ == '__main__':
    root = tk.Tk()
    root.title('Game 15')
    root.resizable(False, False)
    Application(root)
    root.mainloop()
