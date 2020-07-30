import tkinter as tk
import random
import time


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

    def move(self, direction):
        delta = {'left': [-self.size, 0], 'right': [self.size, 0],
                 'up': [0, -self.size], 'down': [0, self.size]}

        self.canvas.move(self.cell_id, *delta[direction])
        self.canvas.move(self.text_id, *delta[direction])


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
        self.numbers = [str(i) for i in range(1, 16)]
        self.freecell = None
        self.moves = 0
        self.start_time = None
        self.finish_time = None
        self.game_time = 0
        self.str_time = None
        self.is_play = False

        # -----------------------Widgets-------------------------
        self.canvas = tk.Canvas(root, width=4 * self.cell_size,
                                height=4 * self.cell_size, bg='white')
        self.canvas.pack()

        # ------------------------Start--------------------------
        self.create_cells()

    # -------------------------Start Methods----------------------------
    def set_start_values(self):
        self.cells = []
        self.canvas.delete('all')
        self.moves = 0
        self.start_time = None
        self.finish_time = None
        self.game_time = 0
        self.str_time = None

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
                self.canvas.tag_bind(self.cells[i].cell_id,
                                     "<Button-1>", self.click_on_cell)
                self.canvas.tag_bind(self.cells[i].text_id,
                                     "<Button-1>", self.click_on_cell)

        if not self.test_puzzle(freecell_row):
            self.create_cells()
        else:
            self.start_time = time.time()
            self.is_play = True

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

    # -----------------------Service Methods----------------------------
    def time_from_seconds(self, t):
        hours, seconds = divmod(t, 3600)
        minutes, seconds = divmod(seconds, 60)
        hours, minutes = int(hours), int(minutes)
        return '{:0>2}'.format(hours) + ':' + '{:0>2}'.format(minutes) + \
            ':' + '{:05.2f}'.format(seconds)

    # ------------------------Game Methods------------------------------
    def click_on_cell(self, event):
        x = event.x // self.cell_size
        y = event.y // self.cell_size

        current = self.cells[x + y * 4]
        if current != 0:
            self.moves += 1
            coords = self.canvas.coords(current.cell_id)
            fc = self.freecell

            if coords[0] + self.cell_size == fc[0] and coords[1] == fc[1]:
                current.move('right')
                self.cells[x + 1 + y * 4] = current
                self.freecell = coords
                self.cells[x + y * 4] = 0

            elif coords[0] - self.cell_size == fc[0] and coords[1] == fc[1]:
                current.move('left')
                self.cells[x - 1 + y * 4] = current
                self.freecell = coords
                self.cells[x + y * 4] = 0

            elif coords[1] + self.cell_size == fc[1] and coords[0] == fc[0]:
                current.move('down')
                self.cells[x + y * 4 + 4] = current
                self.freecell = coords
                self.cells[x + y * 4] = 0

            elif coords[1] - self.cell_size == fc[1] and coords[0] == fc[0]:
                current.move('up')
                self.cells[x + y * 4 - 4] = current
                self.freecell = coords
                self.cells[x + y * 4] = 0

        if self.is_win():
            self.finish_time = time.time()
            self.is_play = False
            self.game_time += self.finish_time - self.start_time
            self.str_time = self.time_from_seconds(self.game_time)
            self.show_win_screen()

    def is_win(self):
        return ([i.number if i != 0 else 0 for i in self.cells] ==
                self.numbers + [0])

    # --------------------------Screens---------------------------------
    def show_win_screen(self):
        self.canvas.delete('all')
        font_size = self.cell_size // 6
        button = tk.Button(text='Play again',
                           command=self.create_cells,
                           justify=tk.CENTER, font=f"Consolas {font_size}")
        self.canvas.create_text(self.cell_size * 2,
                                self.cell_size,
                                text='You Win', justify=tk.CENTER,
                                font=f"Consolas {font_size}")
        self.canvas.create_text(self.cell_size * 2,
                                self.cell_size * 1.5,
                                text=f'Moves: {self.moves}',
                                justify=tk.CENTER,
                                font=f"Consolas {font_size}")
        self.canvas.create_text(self.cell_size * 2,
                                self.cell_size * 2,
                                text=f'Time: {self.str_time}',
                                justify=tk.CENTER,
                                font=f"Consolas {font_size}")
        self.canvas.create_window(self.cell_size * 2,
                                  self.cell_size * 2.5,
                                  window=button)


if __name__ == '__main__':
    root = tk.Tk()
    root.title('Game 15')
    root.resizable(False, False)
    Application(root)
    root.mainloop()
