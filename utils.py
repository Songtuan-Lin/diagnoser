class DGraph:
    def __init__(self, v):
        self.v = v
        self.e = 0
        self.adj = [[] for i in range(self.v)]

    def add_edge(self, v, w):
        self.adj[v].append(w)
        self.e += 1

    def reverse(self):
        g = DGraph(self.v)
        for v, ns in enumerate(self.adj):
            for w in ns:
                g.add_edge(w, v)
        return g

    def connected(self, v, w):
        queue = [v]
        marked = [False] * self.v
        while len(queue) != 0:
            s = queue.pop(0)
            if s == w:
                return True
            if not marked[s]:
                marked[s] = True
                for n in self.adj[s]:
                    queue.append(n)
        return False

class TypeDGraph(DGraph):
    def __init__(self, types):
        self.v_map = {t.name: idx for idx, t in enumerate(types)}
        super().__init__(len(types))
        for t in types:
            if t.basetype_name:
                super().add_edge(self.v_map[t.name], self.v_map[t.basetype_name]) 

    def subtype(self, x, y):
        return super().connected(self.v_map[x], self.v_map[y])


def find_all_tuples(all_combs):
    if len(all_combs) == 0:
        return [tuple()]
    results = set()
    tail = all_combs.pop(-1)
    heads = find_all_tuples(all_combs)
    for e in tail:
        for t in heads:
            t= list(t)
            t.append(e)
            results.add(tuple(t))
    return results