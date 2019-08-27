
from krrt.utils import read_file
from krrt.sat import CNF

class Node:

    def __init__(self, childs = []):
        assert None not in childs, str(childs)
        self.children = childs
        self._count = -1
        self._nnf_index = -1
        self._replacement = None

    @property
    def usedvars(self):
        if self._replacement is None:
            self._replacement = set()
            for ch in self.children:
                if bool != type(ch):
                    self._replacement = self._replacement | ch.usedvars
        return self._replacement
    
    @property
    def nnf_index(self):
        assert -1 != self._nnf_index
        return self._nnf_index

    def reset(self):
        if (-1 != self._count) or (self._replacement is not None) or (self._nnf_index != -1):
            for ch in self.children:
                if ch not in [True, False]:
                    ch.reset()
            self._count = -1
            self._nnf_index = -1
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
    
    def forget(self, vars):
        if self._replacement is None:
            def recursively_apply(ch):
                if ch in [True, False]:
                    return ch
                else:
                    return ch.forget(vars)
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
    
    def dual_children(self, vals):
        lits = set()
        for v in filter(lambda x: isinstance(x, Lit), vals):
            if (-1 * v.num) in lits:
                return True
            lits.add(v.num)
        return False
    
    def assign_nnf_indices(self, nlist):
        if self._nnf_index != -1:
            return
        
        for ch in self.children:
            ch.assign_nnf_indices(nlist)
        
        self._nnf_index = len(nlist)
        nlist.append(self)

    def ensure_vars(self, vars):
        if 0 == len(vars):
            return self
        elif isinstance(self, And):
            parent = self
        elif isinstance(self, Lit) or isinstance(self, Or):
            parent = And([self])
            parent = parent.smooth()
        else:
            assert False, "Not sure how to ensure variables for node type %s" % str(type(self))

        new_children = []
        for v in vars:
            new_children.append(Or([Lit(v), Lit(v.negate())]))

        new_parent = And(parent.children + new_children)
        new_parent = new_parent.smooth()

        return new_parent
        
    def gen_nnf(self):
        assert False, "Must override gen_nnf!"
    


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
        new_vals = list(filter(lambda x: x != True, vals))
        if False in new_vals:
            return False
        elif 0 == len(new_vals):
            return True
        elif 1 == len(new_vals):
            return new_vals[0]
        elif self.dual_children(new_vals):
            return False
        else:
            final_vals = []
            for ch in new_vals:
                if isinstance(ch, And):
                    final_vals.extend(ch.children)
                else:
                    final_vals.append(ch)
            return And(final_vals)

    def smooth(self):
        if self._replacement is None:
            new_vals = []
            new_vars = set()
            for ch in self.children:
                new_vals.append(ch.smooth())
                new_vars = new_vars | new_vals[-1]._vars
            self._replacement = And(new_vals)
            self._replacement._vars = new_vars
        return self._replacement

    def is_smooth(self):
        if self._replacement is None:
            chs = list(filter(lambda x: x not in [True,False], self.children))
            chvals = [ch.is_smooth() for ch in chs]
            if False in chvals:
                return False
            subvars = chs[0]._replacement
            for ch in chs:
                subvars = subvars | ch._replacement
            self._replacement = subvars
        return True
    
    def gen_nnf(self):
        return "A %d %s" % (len(self.children),
                            ' '.join(map(str, [ch.nnf_index for ch in self.children])))


class Or(Node):

    def __init__(self, childs=[], switch_var=0):
        super().__init__(childs=childs)
        self.switch_var = switch_var

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
        new_vals = list(filter(lambda x: x != False, vals))
        if True in new_vals:
            return True
        elif 0 == len(new_vals):
            return False
        elif 1 == len(new_vals):
            return new_vals[0]
        elif self.dual_children(new_vals):
            return True
        else:
            final_vals = []
            for ch in new_vals:
                if isinstance(ch, Or):
                    final_vals.extend(ch.children)
                else:
                    final_vals.append(ch)
            return Or(final_vals)

    def smooth(self):
        if self._replacement is None:
            new_vals = []
            new_vars = set()
            for ch in self.children:
                new_vals.append(ch.smooth())
                new_vars = new_vars | new_vals[-1]._vars
            final_vals = [ch.ensure_vars(new_vars - ch._vars) for ch in new_vals]
            self._replacement = Or(final_vals)
            self._replacement._vars = new_vars
        return self._replacement

    def is_smooth(self):
        if self._replacement is None:
            chs = list(filter(lambda x: x not in [True,False], self.children))
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
    
    def gen_nnf(self):
        return "O %d %d %s" % (self.switch_var,
                               len(self.children),
                               ' '.join(map(str, [ch.nnf_index for ch in self.children])))


class Lit(Node):

    def __init__(self, lit):
        super().__init__(childs=[])
        self.lit = lit
        self.reset()

    @property
    def usedvars(self):
        return set([self.lit.var])
    
    @property
    def num(self):
        return int(str(self.lit).replace('~','-'))

    def reset(self):
        self._count = -1
        self._nnf_index = -1
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
    
    def forget(self, vars):
        if self._replacement is None:
            if self.lit.var in vars:
                self._replacement = True
            else:
                self._replacement = Lit(self.lit)
        return self._replacement

    def simplify(self):
        if self._replacement is None:
            self._replacement = Lit(self.lit)
        return self._replacement

    def smooth(self):
        if self._replacement is None:
            self._replacement = Lit(self.lit)
            self._replacement._vars = set([self.lit.var])
        return self._replacement

    def is_smooth(self):
        self._replacement = set([self.lit.var])
        return True
    
    def gen_nnf(self):
        return "L %d" % self.num


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
    
    def forget(self, vars):
        if bool == type(self.root):
            return dDNNF(self.root, self.allvars - set(vars))
        self.root.reset()
        return dDNNF(self.root.forget(vars), self.allvars - set(vars))

    def simplify(self):
        if bool == type(self.root):
            return dDNNF(self.root, self.allvars)
        self.root.reset()
        return dDNNF(self.root.simplify(), self.allvars)

    def smooth(self):
        if bool == type(self.root):
            return dDNNF(self.root, self.allvars)

        # Simplify before smoothing
        self.root.reset()
        simp_root = self.root.simplify()

        # Smooth
        simp_root.reset()
        smooth_root = simp_root.smooth()
        smooth_root = smooth_root.ensure_vars(self.allvars - smooth_root._vars)
        smooth_root.reset()

        assert len(self.allvars) == len(smooth_root._vars)

        return dDNNF(smooth_root, self.allvars)

    def is_smooth(self):
        if bool == type(self.root):
            return True
        self.root.reset()
        return self.root.is_smooth()
    
    def gen_nnf(self):
        n_list = []
        self.root.reset()
        self.root.assign_nnf_indices(n_list)
        assert self.root == n_list[-1]
        for i in range(len(n_list)):
            assert n_list[i].nnf_index == i
        
        nNodes = len(n_list)
        nVars = len(self.usedvars)
        
        nEdges = 0
        for n in n_list:
            nEdges += len(n.children)
        
        toRet = "nnf %d %d %d\n" % (nNodes, nEdges, nVars)
        for n in n_list:
            toRet += "%s\n" % n.gen_nnf()
        
        return toRet
        




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
            children = list(map(int, parts[2:]))
            assert nCh == len(children), "Bad line? %s" % line
            assert max(children) < len(nodes)
            nodes.append(And([nodes[i] for i in children]))

        elif 'O' == parts[0]:
            switch = int(parts[1])
            nCh = int(parts[2])
            children = list(map(int, parts[3:]))
            assert nCh == len(children), "Bad line? %s" % line
            assert max(children) < len(nodes)
            nodes.append(Or([nodes[i] for i in children], switch))
            if 0 == switch:
                badlist.add(len(nodes) - 1)

        else:
            assert False, "Unrecognized line: %s" % line

    return dDNNF(nodes[-1], allvars)
