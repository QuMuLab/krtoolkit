
from krrt.utils import read_file
from krrt.sat import CNF

class Node:

    def __init__(self, childs = []):
        self.children = childs
        self._count = -1
        self._conditioned = None

    def reset(self):
        if -1 != self._count:
            for ch in self.children:
                ch.reset()
            self._count = -1
            self._conditioned = None


class And(Node):

    def count(self, lits):
        if -1 == self._count:
            self._count = reduce(lambda x,y: x*y, [ch.count(lits) for ch in self.children])
        return self._count

    def condition(self, lits):
        if self.conditioned is None:
            vals = [ch.condition(lits) for ch in self.children]
            vals = filter(lambda x: x != True, vals)
            if False in vals:
                self.conditioned = False
            elif 0 == len(vals):
                self.conditioned = True
            elif 1 == len(vals):
                self.conditioned = vals[0]
            else:
                self.conditioned = And(vals)
        return self.conditioned


class Or(Node):

    def count(self, lits):
        if -1 == self._count:
            self._count = sum([ch.count(lits) for ch in self.children])
        return self._count

    def condition(self, lits):
        if self.conditioned is None:
            vals = [ch.condition(lits) for ch in self.children]
            vals = filter(lambda x: x != False, vals)
            if True in vals:
                self.conditioned = True
            elif 0 == len(vals):
                self.conditioned = False
            elif 1 == len(vals):
                self.conditioned = vals[0]
            else:
                self.conditioned = Or(vals)
        return self.conditioned


class Lit(Node):

    def __init__(self, lit):
        self.lit = lit

    def count(self, lits):
        return {True: 0, False: 1}[self.lit.negate() in lits]

    def condition(self, lits):
        if self.conditioned is None:
            if self.lit in lits:
                self.conditioned = True
            elif self.lit.negate() in lits:
                self.conditioned = False
            else:
                self.conditioned = Lit(self.lit)
        return self.conditioned


class dDNNF:

    def __init__(self, root):
        self.root = root

    def count(self, lits = set()):
        self.root.reset()
        return self.count(lits)

    def condition(self, lits):
        self.root.reset()
        return dDNNF(self.root.condition(lits))



def parseNNF(fname):

    lines = read_file(fname)
    (nNodes, nEdges, nVars) = map(int, lines.pop(0).split()[1:])
    assert nNodes == len(lines)

    badlist = set()
    nodes = [None]

    for line in lines:

        parts = line.split()

        if 'L' == parts[0]:
            num = int(parts[1])
            lit = CNF.Variable(abs(num))
            if num < 0:
                lit = CNF.Not(lit)
            nodes.append(Lit(lit))

        elif 'A' == parts[0]:
            nCh = int(parts[1])
            children = map(int, parts[2:])
            assert nCh == len(children), "Bad line? %s" % line
            assert max(children) < len(nodes)
            nodes.append(And([nodes[i] for i in children]))

        elif 'O' == parts[0]:
            switch = int(parts[1])
            nCh = int(parts[2])
            children = map(int, parts[3:])
            assert nCh == len(children), "Bad line? %s" % line
            assert max(children) < len(nodes)
            nodes.append(Or([nodes[i] for i in children]))
            if 0 == switch:
                badlist.add(len(nodes) - 1)

        else:
            assert False, "Unrecognized line: %s" % line

    return dDNNF(nodes[-1])
