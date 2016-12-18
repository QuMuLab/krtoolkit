
from krrt.utils import read_file
from krrt.sat import CNF

class Node:

    def __init__(self, childs = []):
        assert None not in childs, str(childs)
        self.children = childs
        self._count = -1
        self._replacement = None

    @property
    def usedvars(self):
        if self._replacement is None:
            self._replacement = set()
            for ch in self.children:
                if bool != type(ch):
                    self._replacement |= ch.usedvars
        return self._replacement

    def reset(self):
        if (-1 != self._count) or (self._replacement is not None):
            for ch in self.children:
                if ch not in [True, False]:
                    ch.reset()
            self._count = -1
            self._replacement = None

    def crawl(self, seen):
        if self not in seen:
            seen.add(self)
            for ch in self.children:
                if ch not in [True,False]:
                    ch.crawl(seen)

    def condition(self, lits):
        if self._replacement is None:
            def recursively_apply(ch):
                if ch in [True, False]:
                    return ch
                else:
                    return ch.condition(lits)
            vals = [recursively_apply(ch) for ch in self.children]
            self._replacement = self._compress(vals)
        return self._replacement

    def simplify(self):
        if self._replacement is None:
            def recursively_apply(ch):
                if ch in [True, False]:
                    return ch
                else:
                    return ch.simplify()
            vals = [recursively_apply(ch) for ch in self.children]
            self._replacement = self._compress(vals)
        return self._replacement


class And(Node):

    def count(self, vars):
        if -1 == self._count:
            self._count = {v:1 for v in vars}
            self._count[-1] = 1
            counts = {ch: ch.count(vars) for ch in self.children}
            for v in self._count:
                for ch in counts:
                    self._count[v] *= counts[ch][v]
        return self._count

    def _compress(self, vals):
        new_vals = filter(lambda x: x != True, vals)
        if False in new_vals:
            return False
        elif 0 == len(new_vals):
            return True
        elif 1 == len(new_vals):
            return new_vals[0]
        else:
            return And(new_vals)

    def is_smooth(self):
        if self._replacement is None:
            chs = filter(lambda x: x not in [True,False], self.children)
            chvals = [ch.is_smooth() for ch in chs]
            if False in chvals:
                return False
            subvars = chs[0]._replacement
            for ch in chs:
                subvars = subvars | ch._replacement
            self._replacement = subvars
        return True


class Or(Node):

    def count(self, vars):
        if -1 == self._count:
            self._count = {v:0 for v in vars}
            self._count[-1] = 0
            counts = {ch: ch.count(vars) for ch in self.children}
            for v in self._count:
                for ch in counts:
                    self._count[v] += counts[ch][v]
        return self._count

    def _compress(self, vals):
        new_vals = filter(lambda x: x != False, vals)
        if True in new_vals:
            return True
        elif 0 == len(new_vals):
            return False
        elif 1 == len(new_vals):
            return new_vals[0]
        else:
            return Or(vals)

    def is_smooth(self):
        if self._replacement is None:
            chs = filter(lambda x: x not in [True,False], self.children)
            chvals = [ch.is_smooth() for ch in chs]
            if False in chvals:
                return False
            subvars = chs[0]._replacement
            for ch in chs:
                if (len(ch._replacement) != len(subvars)) or \
                   (len(ch._replacement | subvars) != len(subvars)):
                    return False
            self._replacement = subvars
        return True


class Lit(Node):

    def __init__(self, lit):
        self.lit = lit
        self.reset()

    @property
    def usedvars(self):
        return set([self.lit.var])

    def reset(self):
        self._count = -1
        self._replacement = None

    def crawl(self, seen):
        seen.add(self)

    def count(self, vars):
        toret = {v: 1 for v in vars}
        toret[-1] = 1
        if self.lit.negate() in vars:
            toret[self.lit.negate()] = 0
        return toret

    def condition(self, lits):
        if self._replacement is None:
            if self.lit in lits:
                self._replacement = True
            elif self.lit.negate() in lits:
                self._replacement = False
            else:
                self._replacement = Lit(self.lit)
        return self._replacement

    def simplify(self):
        if self._replacement is None:
            self._replacement = Lit(self.lit)
        return self._replacement

    def is_smooth(self):
        self._replacement = set([self.lit.var])
        return True


class dDNNF:

    def __init__(self, root, allvars):
        self.root = root
        self.allvars = allvars
        self.usedvars = set()
        if bool != type(self.root):
            self.root.reset()
            self.usedvars = self.root.usedvars
            self.root.reset()

    def size(self):
        seen = set()
        if bool != type(self.root):
            self.root.crawl(seen)
        return len(seen)

    def count(self, vars = set()):
        if bool == type(self.root):
            count = int(self.root) * (2**len(self.allvars))
            if vars:
                return {v: (count/2) for v in vars}
            else:
                return count

        self.root.reset()

        counts = self.root.count(vars)

        if vars:
            assert vars <= self.allvars
        else:
            return counts[-1]

        toret = {v: 2**len(self.allvars - self.root.usedvars) * counts[v] for v in vars}

        for var in (vars - self.usedvars):
            toret[var] = counts[-1] / 2

        return toret

    def condition(self, lits):
        if bool == type(self.root):
            return dDNNF(self.root, self.allvars - set([l.var for l in lits]))
        self.root.reset()
        return dDNNF(self.root.condition(lits), self.allvars - set([l.var for l in lits]))

    def simplify(self):
        if bool == type(self.root):
            return dDNNF(self.root, self.allvars)
        self.root.reset()
        return dDNNF(self.root.simplify(), self.allvars)

    def is_smooth(self):
        if bool == type(self.root):
            return True
        self.root.reset()
        return self.root.is_smooth()


def parseNNF(fname):

    lines = read_file(fname)
    (nNodes, nEdges, nVars) = map(int, lines.pop(0).split()[1:])
    assert nNodes == len(lines)

    # TODO: Double check that this badlist isn't included in the final d-DNNF
    badlist = set()
    allvars = set()
    nodes = []

    for line in lines:

        parts = line.split()

        if 'A 0' == line:
            nodes.append(True)

        elif 'O 0 0' == line:
            nodes.append(False)

        elif 'L' == parts[0]:
            num = int(parts[1])
            lit = CNF.Variable(abs(num))
            allvars.add(lit)
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

    return dDNNF(nodes[-1], allvars)
