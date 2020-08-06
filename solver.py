# https://codegolf.stackexchange.com/questions/6884/solve-the-15-puzzle-the-tile-sliding-puzzle
class IDAStar:
    def __init__(self, h, neighbours):
        self.h = h
        self.neighbours = neighbours
        self.FOUND = object()

    def solve(self, root, is_goal, max_cost=None):
        self.is_goal = is_goal
        self.path = [root]
        self.is_in_path = {root}
        self.path_descrs = []
        self.nodes_evaluated = 0

        bound = self.h(root)

        while True:
            t = self._search(0, bound)
            if t is self.FOUND:
                return self.path, self.path_descrs, bound, self.nodes_evaluated
            if t is None:
                return None
            bound = t

    def _search(self, g, bound):
        self.nodes_evaluated += 1

        node = self.path[-1]
        f = g + self.h(node)
        if f > bound:
            return f
        if self.is_goal(node):
            return self.FOUND

        m = None
        for cost, n, descr in self.neighbours(node):
            if n in self.is_in_path:
                continue

            self.path.append(n)
            self.is_in_path.add(n)
            self.path_descrs.append(descr)
            t = self._search(g + cost, bound)

            if t == self.FOUND:
                return self.FOUND
            if m is None or (t is not None and t < m):
                m = t

            self.path.pop()
            self.path_descrs.pop()
            self.is_in_path.remove(n)

        return m


def slide_solved_state(n):
    return tuple(i % (n * n) for i in range(1, n * n + 1))


def slide_neighbours(n):
    movelist = []
    for gap in range(n * n):
        x, y = gap % n, gap // n
        moves = []
        if x > 0:
            moves.append(-1)
        if x < n - 1:
            moves.append(+1)
        if y > 0:
            moves.append(-n)
        if y < n - 1:
            moves.append(+n)
        movelist.append(moves)

    def neighbours(p):
        gap = p.index(0)
        l = list(p)

        for m in movelist[gap]:
            l[gap] = l[gap + m]
            l[gap + m] = 0
            yield (1, tuple(l), (l[gap], m))
            l[gap + m] = l[gap]
            l[gap] = 0

    return neighbours


def encode_cfg(cfg, n):
    r = 0
    b = n.bit_length()
    for i in range(len(cfg)):
        r |= cfg[i] << (b * i)
    return r


def gen_wd_table(n):
    goal = [[0] * i + [n] + [0] * (n - 1 - i) for i in range(n)]
    goal[-1][-1] = n - 1
    goal = tuple(sum(goal, []))

    table = {}
    to_visit = [(goal, 0, n - 1)]
    while to_visit:
        cfg, cost, e = to_visit.pop(0)
        enccfg = encode_cfg(cfg, n)
        if enccfg in table:
            continue
        table[enccfg] = cost

        for d in [-1, 1]:
            if 0 <= e + d < n:
                for c in range(n):
                    if cfg[n * (e + d) + c] > 0:
                        ncfg = list(cfg)
                        ncfg[n * (e + d) + c] -= 1
                        ncfg[n * e + c] += 1
                        to_visit.append((tuple(ncfg), cost + 1, e + d))
    return table


def slide_wd(n, goal):
    wd = gen_wd_table(n)
    goals = {i: goal.index(i) for i in goal}
    b = n.bit_length()

    def h(p):
        ht = 0
        vt = 0
        d = 0
        for i, c in enumerate(p):
            if c == 0:
                continue
            g = goals[c]
            xi, yi = i % n, i // n
            xg, yg = g % n, g // n
            ht += 1 << (b * (n * yi + yg))
            vt += 1 << (b * (n * xi + xg))

            if yg == yi:
                for k in range(i + 1, i - i % n + n):
                    if p[k] and goals[p[k]] // n == yi and goals[p[k]] < g:
                        d += 2
            if xg == xi:
                for k in range(i + n, n * n, n):
                    if p[k] and goals[p[k]] % n == xi and goals[p[k]] < g:
                        d += 2
        d += wd[ht] + wd[vt]
        return d
    return h
