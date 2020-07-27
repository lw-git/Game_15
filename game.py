import tkinter as tk
import random


class Cell():
    def __init__(self, canvas, size, color, number, x, y):
        self.cell_id = None
        self.text_id = None
        self.canvas = canvas
        self.size = size
        self.color = color
        self.number = number
        self.x = x * self.size
        self.y = y * self.size
        self.create()

    def create(self):
        self.cell_id = self.canvas.create_rectangle(
            self.x, self.y, self.x + self.size, self.y + self.size,
            fill=self.color)
        self.text_id = self.canvas.create_text(
            self.x + self.size // 2, self.y + self.size // 2,
            text=self.number, justify=tk.CENTER, font="Consolas 25")


class Application(tk.Frame):

    def __init__(self, *args, **kwargs):
        tk.Frame.__init__(self, *args, **kwargs)

        # ---------------------Variables-------------------------
        self.cell_size = 150
        self.cells = []
        self.colors = ["green", "lightgreen", "gray", "silver",
                       "spring green", "rosybrown", "lawngreen", "deep pink",
                       "cyan", "lightblue", "lime", "violet",
                       "gold", "orange", "firebrick1", "deepskyblue"]
        self.numbers = ['1', '2', '3', '4', '5', '6', '7', '8', '9',
                        '10', '11', '12', '13', '14', '15']
        self.freecell = None

        # -----------------------Widgets-------------------------
        self.canvas = tk.Canvas(root, width=4 * self.cell_size,
                                height=4 * self.cell_size, bg='white')
        self.canvas.pack()

        # ------------------------Start--------------------------
        self.create_cells()

    # --------------------------Methods------------------------------
    def set_start_values(self):
        self.cells = []
        self.canvas.delete('all')

    def create_cells(self):
        freecell = False
        freecell_row = None
        numbers = self.numbers[:]
        self.set_start_values()
        for i in range(0, 16):
            if (random.randint(0, 5000) > 4000 or i == 15) and not freecell:
                self.add_freecell(i % 4, i // 4)
                freecell = True
                freecell_row = i // 4 + 1
            else:
                number = numbers.pop(random.randint(0, len(numbers) - 1))
                self.cells.append(Cell(self.canvas, self.cell_size,
                                       random.choice(self.colors),
                                       number, i % 4, i // 4))

        if not self.test_puzzle(freecell_row):
            self.create_cells()

    def add_freecell(self, row, col):
        self.cells.append(0)
        self.freecell = [row * self.cell_size, col * self.cell_size,
                         (row + 1) * self.cell_size,
                         (col + 1) * self.cell_size]

    def test_puzzle(self, fcr):
        even = 0
        for i, item in enumerate(self.cells):
            for j, item in enumerate(self.cells):
                if j > i:
                    if self.cells[j] != 0 and self.cells[i] != 0:
                        if (int(self.cells[i].number) >
                            int(self.cells[j].number)):
                                even += 1
        even += fcr
        if even % 2 != 0:
            return False
        return True


if __name__ == '__main__':
    root = tk.Tk()
    root.title('Game 15')
    root.resizable(False, False)
    Application(root)
    root.mainloop()
