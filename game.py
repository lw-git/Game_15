import tkinter as tk
import random
import time


class Cell():
    def __init__(self, canvas, size, color, number, x, y, fn):
        self.cell_id = None
        self.text_id = None
        self.canvas = canvas
        self.size = size
        self.color = color
        self.number = number
        self.x = x * self.size
        self.y = y * self.size
        self.fn = fn
        self.create()

    def create(self):
        self.cell_id = self.canvas.create_rectangle(
            self.x, self.y, self.x + self.size, self.y + self.size,
            fill=self.color)
        self.text_id = self.canvas.create_text(
            self.x + self.size // 2, self.y + self.size // 2,
            text=self.number, justify=tk.CENTER,
            font=f"Consolas {self.size // 3}")
        self.canvas.tag_bind(self.cell_id, "<Button-1>", self.fn)
        self.canvas.tag_bind(self.text_id, "<Button-1>", self.fn)

    def move(self, direction):
        delta = {'left': [-self.size, 0], 'right': [self.size, 0],
                 'up': [0, -self.size], 'down': [0, self.size]}

        self.canvas.move(self.cell_id, *delta[direction])
        self.canvas.move(self.text_id, *delta[direction])
        self.x, self.y, *_ = self.canvas.coords(self.cell_id)

    def resize(self, new_size, x, y):
        self.size = new_size
        self.x = x * self.size
        self.y = y * self.size
        font_size = self.size // 3
        self.canvas.coords(self.cell_id, self.x, self.y,
                           self.x + self.size, self.y + self.size)
        self.canvas.coords(self.text_id, self.x + self.size // 2,
                           self.y + self.size // 2)
        self.canvas.itemconfigure(self.text_id, font=f"Consolas {font_size}")


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
        self.is_pause = False

        # -----------------------Widgets-------------------------
        mainmenu = tk.Menu(root)
        root.config(menu=mainmenu)
        gamemenu = tk.Menu(mainmenu, tearoff=0)
        gamemenu.add_command(label="New game", command=self.create_cells)
        gamemenu.add_command(label="Decrease cell size",
                             command=lambda: self.resize(self.cell_size - 25))
        gamemenu.add_command(label="Increase cell size",
                             command=lambda: self.resize(self.cell_size + 25))
        gamemenu.add_command(label="Exit", command=lambda: root.destroy())
        infomenu = tk.Menu(mainmenu, tearoff=0)
        infomenu.add_command(label="Records", command=None)
        infomenu.add_command(label="About", command=self.show_about)
        mainmenu.add_cascade(label="Game", menu=gamemenu)
        mainmenu.add_cascade(label="Info", menu=infomenu)

        self.canvas = tk.Canvas(root, width=4 * self.cell_size,
                                height=4 * self.cell_size, bg='white')
        self.canvas.pack()

        # ------------------------Start--------------------------
        self.show_start_screen()

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
                                       number, i % 4, i // 4,
                                       self.click_on_cell))

        if not self.test_puzzle(freecell_row):
            self.create_cells()
        else:
            self.start_time = time.time()
            self.is_play = True

    def add_freecell(self, row, col):
        self.cells.append(0)
        self.freecell = [self._size(1, row), self._size(1, col),
                         self._size(1, row + 1), self._size(1, col + 1)]

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
    def _size(self, num, mul=1):
        return self.cell_size // num * mul

    def resize(self, size):
        size = size if size >= 100 else 100
        size = size if size <= 200 else 200
        self.cell_size = size

        for i, cell in enumerate(self.cells):
            if cell != 0:
                x = i % 4
                y = i // 4
                cell.resize(self.cell_size, x, y)
            else:
                self.freecell = [self._size(1, i % 4),
                                 self._size(1, i // 4),
                                 self._size(1, i % 4 + 1),
                                 self._size(1, i % 4 + 1)]
        self.canvas['height'] = self._size(1, 4)
        self.canvas['width'] = self._size(1, 4)
        if not self.is_play:
            self.show_start_screen()

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

    def pause(self):
        if not self.is_pause:
            self.is_pause = True
            if self.is_play:
                current_time = time.time()
                self.game_time += current_time - self.start_time
                self.start_time = None

    def unpause(self):
        if self.is_pause:
            self.is_pause = False
            if self.is_play:
                self.start_time = time.time()
                self.canvas.delete('all')
                [cell.create() for cell in self.cells if cell != 0]
            else:
                self.show_start_screen()

    def is_win(self):
        return ([i.number if i != 0 else 0 for i in self.cells] ==
                self.numbers + [0])

    # --------------------------Screens---------------------------------
    def show_about(self):
        self.pause()
        self.canvas.delete('all')
        button = tk.Button(text='OK', command=self.unpause,
                           justify=tk.CENTER,
                           font=f"Consolas {self._size(7)}")
        self.canvas.create_text(
            self._size(1, 2),
            self._size(1, 1.5),
            text='This is a simple puzzle\n "Game 15".',
            justify=tk.CENTER,
            font=f"Consolas {self._size(6)}")
        self.canvas.create_window(
            self._size(1, 2),
            self._size(1, 2),
            window=button)

    def show_win_screen(self):
        self.canvas.delete('all')
        button = tk.Button(text='Play again',
                           command=self.create_cells,
                           justify=tk.CENTER, font=f"Consolas {self._size(6)}")
        self.canvas.create_text(self._size(1, 2),
                                self._size(1),
                                text='You Win', justify=tk.CENTER,
                                font=f"Consolas {self._size(6)}")
        self.canvas.create_text(self._size(1, 2),
                                self._size(1, 1.5),
                                text=f'Moves: {self.moves}',
                                justify=tk.CENTER,
                                font=f"Consolas {self._size(6)}")
        self.canvas.create_text(self._size(1, 2),
                                self._size(1, 2),
                                text=f'Time: {self.str_time}',
                                justify=tk.CENTER,
                                font=f"Consolas {self._size(7)}")
        self.canvas.create_window(self._size(1, 2),
                                  self._size(1, 2.5),
                                  window=button)

    def show_start_screen(self):
        self.canvas.delete('all')
        button = tk.Button(text='Start play',
                           command=self.create_cells,
                           justify=tk.CENTER, font=f"Consolas {self._size(6)}")
        self.canvas.create_window(self._size(1, 2), self._size(1, 2),
                                  window=button)


if __name__ == '__main__':
    root = tk.Tk()
    root.title('Game 15')
    root.resizable(False, False)
    Application(root)
    root.mainloop()
