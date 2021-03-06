import tkinter as tk
import random
import time
import pickle
from operator import itemgetter
from solver import IDAStar, slide_solved_state, slide_neighbours, slide_wd
import threading



class SaveThread(threading.Thread):
    def __init__(self, callback, *args, **kwargs):
        threading.Thread.__init__(self, *args, **kwargs)
        self.callback = callback
        run_original = self.run

        def run_with_except_hook():
            try:
                run_original()
            except Exception as e:
                data = 'with error {}'.format(e)
                self.callback(data)
            else:
                data = 'successful'
                self.callback(data)

        self.run = run_with_except_hook


class Records():
    def __init__(self):
        self.data = {'moves': [], 'time': []}
        self.load()

    def save(self):
        self.sort_records()
        with open('records.pickle', 'wb') as f:
            pickle.dump(self.data, f)

    def load(self):
        try:
            with open('records.pickle', 'rb') as f:
                self.data = pickle.load(f)
        except IOError:
            self.data = {'moves': [], 'time': []}

    def sort_records(self):
        self.data['time'] = sorted(self.data['time'],
                                   key=itemgetter('time', 'moves'))
        self.data['moves'] = sorted(self.data['moves'],
                                    key=itemgetter('moves', 'time'))
        self.data['time'] = self.data['time'][:10]
        self.data['moves'] = self.data['moves'][:10]


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
        self.records = Records()
        self.is_solving = False
        self.is_solve = False
        self.s_moves = []

        # -----------------------Widgets-------------------------
        mainmenu = tk.Menu(root)
        root.config(menu=mainmenu)
        gamemenu = tk.Menu(mainmenu, tearoff=0)
        gamemenu.add_command(label="New game", command=self.create_cells)
        gamemenu.add_command(label="Decrease cell size",
                             command=lambda: self.resize(self.cell_size - 25))
        gamemenu.add_command(label="Increase cell size",
                             command=lambda: self.resize(self.cell_size + 25))
        gamemenu.add_command(label="Solve", command=self.solve)
        gamemenu.add_command(label="Exit", command=lambda: root.destroy())
        infomenu = tk.Menu(mainmenu, tearoff=0)
        infomenu.add_command(label="Records", command=self.show_records)
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
        self.is_solving = False
        self.is_solve = False
        self.s_moves = []

    def create_cells(self):
        if self.is_solving:
            return
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
        if self.is_solving:
            return
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
        elif self.is_pause:
            self.show_start_screen()

    def save_record(self):
        record = {'moves': self.moves, 'time': self.str_time}
        self.records.data['moves'].append(record)
        self.records.data['time'].append(record)
        self.records.save()

    def time_from_seconds(self, t):
        hours, seconds = divmod(t, 3600)
        minutes, seconds = divmod(seconds, 60)
        hours, minutes = int(hours), int(minutes)
        return '{:0>2}'.format(hours) + ':' + '{:0>2}'.format(minutes) + \
            ':' + '{:05.2f}'.format(seconds)

    def get_click(self, x, y):
        self.canvas.event_generate('<ButtonPress-1>', x=x, y=y)
        self.canvas.event_generate('<ButtonRelease-1>', x=x, y=y)

    def move_freecell(self, direction):
        fci = self.cells.index(0)
        args = {'left': [fci - 1, 'right'],
                'right': [fci + 1, 'left'],
                'up': [fci - 4, 'down'],
                'down': [fci + 4, 'up']}

        if 0 <= args[direction][0] <= 15:
            current = self.cells[args[direction][0]]
            self.moves += 1
            current.move(args[direction][1])
            self.cells[fci] = current
            self.freecell = self.canvas.coords(current.cell_id)
            self.cells[args[direction][0]] = 0
            time.sleep(.3)

    def solve(self):
        if self.is_solving:
            return
        if self.is_play:
            self.show_ask_screen()

    def do_solve(self):
        solved_state = slide_solved_state(4)
        neighbours = slide_neighbours(4)
        is_goal = lambda p: p == solved_state
        board = tuple([int(i.number) if i != 0 else 0 for i in self.cells])
        slide_solver = IDAStar(slide_wd(4, solved_state), neighbours)
        _, moves, *_ = slide_solver.solve(board, is_goal, 80)

        self.s_moves = [{-1: "left", 1: "right", -4: "up", 4: "down"}
                        [move[1]] for move in moves]

    def change_letters(self, text):
        dots = ['.' * i for i in range(1, 20)]
        i = 0
        while True:
            if self.is_solve:
                break
            s = dots[i % len(dots)]
            self.canvas.itemconfig(text, text=s)
            i += 1
            time.sleep(.5)

    def callback(self, data):
        self.is_solve = True
        self.canvas.delete('all')
        if data == 'successful':
            button = tk.Button(text='Show solution',
                               command=self.show_solution,
                               justify=tk.CENTER,
                               font=f"Consolas {self._size(6)}")
            self.canvas.create_window(
                self._size(1, 2),
                self._size(1, 2),
                window=button)
        else:
            self.canvas.create_text(
                self._size(1, 2),
                self._size(1, 2),
                text='Error while solving puzzle',
                justify=tk.CENTER,
                font=f"Consolas {self._size(6)}")

    def show_solution(self):
        self.unpause()
        threading.Thread(target=self.do_moves, daemon=True).start()

    def do_moves(self):
        for move in self.s_moves:
            self.move_freecell(move)
        if self.is_win():
            self.win()

    # ------------------------Game Methods------------------------------
    def click_on_cell(self, event):
        if self.is_solving:
            return
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
                self.win()

    def win(self):
        self.is_solving = False
        self.is_play = False
        self.finish_time = time.time()
        self.game_time += self.finish_time - self.start_time
        self.str_time = self.time_from_seconds(self.game_time)
        self.save_record()
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
                if self.is_solving:
                    current_time = time.time()
                    self.game_time += current_time - self.start_time
                    self.start_time = None
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
        if self.is_solving:
            return
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

    def show_records(self, param='time'):
        if self.is_solving:
            return
        self.pause()
        self.canvas.delete('all')
        param2 = 'moves' if param == 'time' else 'time'
        text = ''
        self.canvas.create_text(
            self._size(1, 2), self._size(7, 1.8), text=f'Top 10 (by {param}):',
            justify=tk.CENTER, font=f"Consolas {self._size(6)}")
        if self.records.data[param]:
            for i, r in enumerate(self.records.data[param]):
                if param == 'time':
                    text = f'{i + 1}. Time: {r["time"]} Moves: {r["moves"]}'
                else:
                    text = f'{i + 1}. Moves: {r["moves"]} Time: {r["time"]}'

                self.canvas.create_text(
                    self._size(1, 2),
                    self._size(2, 1.3) + self._size(7, 1.8) * i,
                    text=text, justify=tk.CENTER,
                    font=f"Consolas {self._size(7)}")

        button = tk.Button(text='OK', command=self.unpause,
                           justify=tk.CENTER,
                           font=f"Consolas {self._size(6)}")
        button2 = tk.Button(text=f'by {param2}',
                            command=lambda: self.show_records(param2),
                            justify=tk.CENTER,
                            font=f"Consolas {self._size(6)}")
        self.canvas.create_window(
            self._size(1, 1.5), self._size(1, 3.5), window=button)
        self.canvas.create_window(
            self._size(1, 3), self._size(1, 3.5), window=button2)

    def show_win_screen(self):
        self.is_solving = False
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
        if self.is_play:
            text = 'Continue play'
            fn = self.unpause
        else:
            text = 'Start play'
            fn = self.create_cells
        button = tk.Button(text=text, command=fn, justify=tk.CENTER,
                           font=f"Consolas {self._size(6)}")
        self.canvas.create_window(self._size(1, 2), self._size(1, 2),
                                  window=button)

    def show_ask_screen(self):
        self.pause()
        self.canvas.delete('all')
        button = tk.Button(text='Yes', command=self.show_solve_screen,
                           justify=tk.CENTER,
                           font=f"Consolas {self._size(6)}")
        button2 = tk.Button(text='No', command=self.unpause,
                            justify=tk.CENTER,
                            font=f"Consolas {self._size(6)}")
        text = ['Solve a puzzle?', 'This can take a long time',
                '(from 10 seconds to', '15 minutes or more).',
                'Time depends on the power of',
                'the computer and the complexity',
                'of the layout']
        for i, s in enumerate(text):
            self.canvas.create_text(
                self._size(1, 2),
                self._size(2, 1.3) + self._size(7, 1.8) * i,
                text=s, justify=tk.CENTER,
                font=f"Consolas {self._size(7)}")

        self.canvas.create_window(
            self._size(1, 1.5),
            self._size(1, 3),
            window=button)
        self.canvas.create_window(
            self._size(1, 2.5),
            self._size(1, 3),
            window=button2)

    def show_solve_screen(self):
        self.is_solving = True
        self.start_time = time.time()
        self.canvas.delete('all')
        self.canvas.create_text(
            self._size(1, 2),
            self._size(1, 1.7),
            text='Solving the puzzle', justify=tk.CENTER,
            font=f"Consolas {self._size(6)}")
        text = self.canvas.create_text(
            self._size(1, 2),
            self._size(1, 2),
            text='', justify=tk.CENTER,
            font=f"Consolas {self._size(6)}")
        threading.Thread(target=self.change_letters, args=[text],
                         daemon=True).start()
        SaveThread(self.callback, target=self.do_solve, daemon=True).start()


if __name__ == '__main__':
    root = tk.Tk()
    root.title('Game 15')
    root.resizable(False, False)
    Application(root)
    root.mainloop()
