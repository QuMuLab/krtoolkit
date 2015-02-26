from krrt.utils import write_file

class Formula:
    def __init__(self, clauses = None):
        self.clauses = []
        self.mapping = {}
        self.unmapping = [None]
        self.varnum = 1
        self.comments = []

        if clauses:
            for c in clauses:
                self.addClause(c)

    @property
    def num_vars(self):
        return self.varnum - 1

    @property
    def num_clauses(self):
        return len(self.clauses)

    @property
    def variables(self):
        return self.mapping.keys()

    def copy(self):
        """Return a deep copy of the CNF representation."""
        newTheory = Formula([cls.copy() for cls in self.clauses])
        return newTheory

    def add_comment(self, c):
        self.comments.append(str(c))

    def addClause(self, cls):
        """Add a new clause to the CNF representation"""
        new_clause = set()
        for l in cls:

            if isinstance(l, Not):
                var = Variable(l.obj)
                lit = Not(var)

            else:
                var = Variable(l)
                lit = var

            if var not in self.mapping:
                self.addVariable(var)

            new_clause.add(lit)

        self.clauses.append(new_clause)

    def addVariable(self, var):
        self.mapping[var] = self.varnum
        self.unmapping.append(var)
        self.varnum += 1

    def getUnitClauses(self):
        """Return all of the unit clauses in the CNF representation."""
        return filter(lambda x: 1 == len(x), self.clauses)

    def getClauseWidth(self, avg = False):
        """
        Return the clause width of the ordered clauses in this CNF.

        The clause width is a notion that tries to characterize the
        relationship between clauses in a total ordering of the CNF.
        The width of a variable v is defined as the index of the last
        clause v appears in minus the index of the first clause v
        appears in. The clause width is typically defined as the max
        or average over all variable widths. This function can optionally
        be called with 'avg = True' to return the average variation
        of clause width.
        """
        max = 0
        for var in self.variables:
            low_index = -1
            high_index = -1
            for clsNum in range(self.num_clauses):
                if (var in self.clauses[clsNum]) or (Not(var) in self.clauses[clsNum]):
                    if low_index == -1:
                        low_index = clsNum

                    high_index = clsNum

            if avg:
                max += high_index - low_index
            else:
                if (high_index - low_index) > max:
                    max = high_index - low_index

        if avg:
            return float(max) / float(self.num_vars)
        else:
            return max

    def minimizeClauseWidth(self, method = 'all', invert = False, avg = False):
        """
        Minimize the clause width of the CNF syntactic representation
        Parameters:
            method: Which method of minimization should be used. Currently
                    supported for 'all', 'random', and 'litsort'

            invert: If true, maximize the clause width

            avg:    Use the avg clause width rather than the max


        Methods:
            all:        Take the best minimization (or maximization) over all
                        methods available.

            random:     Randomly sort the clauses 200 times and pick the best
                        sorting

            litsort:    Sort the clauses based on the smallest variable in each
                        clause. This is a crude heuristic that has the effect
                        of minimizing the clause-width
        """
        if 'all' == method:
            self._minimizeClauseWidth_Random(invert, avg)
            self._minimizeClauseWidth_LitSort(invert, avg)
        elif 'random' == method:
            self._minimizeClauseWidth_Random(invert, avg)
        elif 'litsort' == method:
            self._minimizeClauseWidth_LitSort(invert, avg)
        else:
            print "Error: Unknown clause-width minimization technique -- " + method



    def _minimizeClauseWidth_Random(self, invert, avg):
        import random

        best_list = self.clauses
        best_score = self.getClauseWidth(avg=avg)

        self.clauses = []
        for each in best_list:
            self.clauses.append(each)

        for i in range(200):
            random.shuffle(self.clauses)

            score = self.getClauseWidth(avg=avg)

            #print "Score:" + str(score)

            if (invert and score > best_score) or (not invert and score < best_score):
                best_list = self.clauses
                best_score = score

                self.clauses = []
                for each in best_list:
                    self.clauses.append(each)

        self.clauses = best_list

    def _minimizeClauseWidth_LitSort(self, invert, avg):

        def sortClause(cls1, cls2):
            return minLit(cls1) - minLit(cls2)

        def minLit(clause):
            return min([self.mapping[lit.var] for lit in clause])

        best_list = self.clauses
        best_score = self.getClauseWidth(avg=avg)

        self.clauses = []
        for each in best_list:
            self.clauses.append(each)

        self.clauses.sort(sortClause)
        score = self.getClauseWidth(avg=avg)

        #print "Sorted Score:" + str(score)

        if (invert and score > best_score) or (not invert and score < best_score):
            best_list = self.clauses
            best_score = score

            self.clauses = []
            for each in best_list:
                self.clauses.append(each)

        self.clauses = best_list

    def writeCNF(self, sourceFile):
        output = ''
        output += 'c\n'
        output += 'c SAT instance in DIMACS CNF input format.\n'
        for comment in self.comments:
            output += 'c ' + comment + '\n'
        output += 'c\n'
        output += "p cnf %d %d" % (self.num_vars, self.num_clauses)
        output += '\n'

        for cls in self.clauses:
            for lit in cls:
                if isinstance(lit, Not):
                    output += "-%d" % self.mapping[lit.obj]
                else:
                    output += "%d" % self.mapping[lit]
                output += ' '

            output += '0\n'

        write_file(sourceFile, output)

    def writeMapping(self, sourceFile):
        write_file(sourceFile, ["%d %s" % (k,v) for (k,v) in sorted([(self.mapping[var], str(var)) for var in self.variables])])


class WeightedFormula(Formula):
    def __init__(self, clauses = None):
        Formula.__init__(self, None)

        if clauses:
            for c in clauses:
                self.addClause(c[0], c[1])

    @property
    def top_weight(self):
        return 1 + sum([cls[1] for cls in self.getSoftClauses()])

    def copy(self):
        """Return a deep copy of the CNF representation."""
        newTheory = WeightedFormula([(cls[0].copy(), cls[1]) for cls in self.clauses])
        return newTheory

    def addClause(self, cls, weight):
        """Add a new clause to the CNF representation"""
        new_clause = set()
        for l in cls:

            if isinstance(l, Not):
                var = Variable(l.obj)
                lit = Not(var)

            else:
                var = Variable(l)
                lit = var

            if var not in self.mapping:
                self.addVariable(var)

            new_clause.add(lit)

        self.clauses.append((new_clause, weight))

    def getUnitClauses(self):
        """Return all of the unit clauses in the CNF representation."""
        return filter(lambda x: 1 == len(x[0]), self.clauses)

    def getHardClauses(self):
        """Return all of the hard clauses in the theory."""
        return filter(lambda x: -1 == x[1], self.clauses)

    def getSoftClauses(self):
        """Return all of the soft clauses in the theory."""
        return filter(lambda x: -1 != x[1], self.clauses)

    def writeCNF(self, sourceFile):
        output = ''
        output += 'c\n'
        output += 'c SAT instance in DIMACS CNF input format.\n'
        output += 'c\n'
        output += "p wcnf %d %d %d" % (self.num_vars, self.num_clauses, self.top_weight)
        output += '\n'

        for (cls, weight) in self.clauses:
            if -1 == weight:
                output += "%d " % self.top_weight
            else:
                output += "%d " % weight

            for lit in cls:
                if isinstance(lit, Not):
                    output += "-%d" % self.mapping[lit.obj]
                else:
                    output += "%d" % self.mapping[lit]
                output += ' '

            output += '0\n'

        write_file(sourceFile, output)


class OptimizedWeightedFormula(WeightedFormula):
    def __init__(self, clauses = None):
        self.hard_clauses = []
        WeightedFormula.__init__(self, clauses)

    @property
    def num_vars(self):
        top_num = 0
        for cls in self.hard_clauses:
            top_num = max(top_num, max([abs(l) for l in cls]))
        for cls in self.clauses:
            top_num = max(top_num, max([abs(l) for l in cls[0]]))
        return top_num

    @property
    def num_clauses(self):
        return len(self.clauses) + len(self.hard_clauses)

    @property
    def variables(self):
        return list(range(1, self.num_vars + 1))

    def copy(self):
        """Return a deep copy of the CNF representation."""
        newTheory = OptimizedWeightedFormula([(cls[0].copy(), cls[1]) for cls in self.clauses] + [(cls.copy(), -1) for cls in self.hard_clauses])
        return newTheory

    def addClause(self, cls, weight = None):
        """Add a new clause to the CNF representation"""
        if weight:
            self.clauses.append((cls, weight))
        else:
            self.hard_clauses.append(cls)

    def getUnitClauses(self):
        """Return all of the unit clauses in the CNF representation."""
        return filter(lambda x: 1 == len(x[0]), self.getHardClauses() + self.getSoftClauses())

    def getHardClauses(self):
        """Return all of the hard clauses in the theory."""
        return [(cls,-1) for cls in self.hard_clauses]

    def getSoftClauses(self):
        """Return all of the soft clauses in the theory."""
        return self.clauses

    def writeCNF(self, sourceFile, hard = False):
        output = ''
        output += 'c\n'
        output += 'c SAT instance in DIMACS CNF input format.\n'
        output += 'c\n'
        if hard:
            output += "p cnf %d %d" % (self.num_vars, len(self.hard_clauses))
        else:
            output += "p wcnf %d %d %d" % (self.num_vars, self.num_clauses, self.top_weight)
        output += '\n'

        if hard:
            for cls in self.hard_clauses:
                output += "%s 0\n" % (' '.join(map(str, cls)))
            write_file(sourceFile, output)
            return

        TOPW = self.top_weight
        for cls in self.hard_clauses:
            output += "%d %s 0\n" % (TOPW, ' '.join(map(str, cls)))

        for (cls, weight) in self.clauses:
            output += "%d %s 0\n" % (weight, ' '.join(map(str, cls)))

        write_file(sourceFile, output)


class LevelWeightedFormula(WeightedFormula):
    def __init__(self, clauses = None):
        WeightedFormula.__init__(self, None)

        self._top_weight = False

        if clauses:
            for c in clauses:
                self.addClause(c[0], c[1], c[2])
        else:
            self.clauses = {}

    @property
    def top_weight(self):
        if not self._top_weight:
            total = 0
            for level in sorted(self.clauses.keys()):
                total += self.level_weight(level, total)
            self._top_weight = 1 + total

        return self._top_weight

    @property
    def num_clauses(self):
        return sum([len(self.clauses[level]) for level in self.clauses.keys()])

    def level_weight(self, level, total):
        return sum([(total + cls[1]) for cls in filter(lambda x: -1 != x[1], self.clauses[level])])

    def copy(self):
        """Return a deep copy of the CNF representation."""
        new_clauses = []
        for level in self.clauses.keys():
            new_clauses.extend([(cls[0].copy(), cls[1], level) for cls in self.clauses[level]])
        return LevelWeightedFormula(new_clauses)

    def addClause(self, cls, weight, level):
        """Add a new clause to the CNF representation"""
        self._top_weight = False
        new_clause = set()
        for l in cls:

            if isinstance(l, Not):
                var = Variable(l.obj)
                lit = Not(var)

            else:
                var = Variable(l)
                lit = var

            if var not in self.mapping:
                self.addVariable(var)

            new_clause.add(lit)

        if level not in self.clauses.keys():
            self.clauses[level] = [(new_clause, weight)]
        else:
            self.clauses[level].append((new_clause, weight))

    def getUnitClauses(self):
        """Return all of the unit clauses in the CNF representation."""
        return reduce(lambda x,y: x+y, [filter(lambda x: 1 == len(x[0]), self.clauses[level]) for level in self.clauses.keys()])

    def getHardClauses(self):
        """Return all of the hard clauses in the theory."""
        return reduce(lambda x,y: x+y, [filter(lambda x: -1 == x[1], self.clauses[level]) for level in self.clauses.keys()])

    def getSoftClauses(self):
        """Return all of the soft clauses in the theory."""
        return reduce(lambda x,y: x+y, [filter(lambda x: -1 != x[1], self.clauses[level]) for level in self.clauses.keys()])

    def writeCNF(self, sourceFile):
        output = ''
        output += 'c\n'
        output += 'c SAT instance in DIMACS CNF input format.\n'
        output += 'c\n'
        output += "p wcnf %d %d %d" % (self.num_vars, self.num_clauses, self.top_weight)
        output += '\n'

        level_weights = {}
        total = 0
        for level in sorted(self.clauses.keys()):
            level_weights[level] = total
            total += self.level_weight(level, total)

        for level in self.clauses.keys():
            for (cls, weight) in self.clauses[level]:
                if -1 == weight:
                    output += "%d " % self.top_weight
                else:
                    output += "%d " % (weight + level_weights[level])

                for lit in cls:
                    if isinstance(lit, Not):
                        output += "-%d" % self.mapping[lit.obj]
                    else:
                        output += "%d" % self.mapping[lit]
                    output += ' '

                output += '0\n'

        write_file(sourceFile, output)


class OptimizedLevelWeightedFormula(LevelWeightedFormula):

    def __init__(self, clauses = None):
        self.hard_clauses = []
        LevelWeightedFormula.__init__(self, clauses)

    def level_weight(self, level, total):
        return sum([(total + cls[1]) for cls in self.clauses[level]])

    @property
    def num_vars(self):
        top_num = 0
        for cls in self.hard_clauses:
            top_num = max(top_num, max([abs(l) for l in cls]))
        for level in self.clauses.keys():
            for cls in self.clauses[level]:
                top_num = max(top_num, max([abs(l) for l in cls[0]]))
        return top_num

    @property
    def num_clauses(self):
        return len(self.hard_clauses) + sum([len(self.clauses[level]) for level in self.clauses.keys()])

    def copy(self):
        """Return a deep copy of the CNF representation."""
        new_clauses = []
        for level in self.clauses.keys():
            new_clauses.extend([(cls[0].copy(), cls[1], level) for cls in self.clauses[level]])
        new_clauses.extend([(cls.copy(), -1, -1) for cls in self.hard_clauses])
        return OptimizedLevelWeightedFormula(new_clauses)

    def addClause(self, cls, weight = 1, level = -1):
        """Add a new clause to the CNF representation"""
        self._top_weight = False

        if -1 == level:
            self.hard_clauses.append(cls)
            return

        if level not in self.clauses:
            self.clauses[level] = []

        self.clauses[level].append((cls, weight))

    def getHardClauses(self):
        """Return all of the hard clauses in the theory."""
        return self.hard_clauses

    def getSoftClauses(self):
        """Return all of the soft clauses in the theory."""
        return reduce(lambda x,y: x+y, [self.clauses[level] for level in self.clauses.keys()])

    def writeCNF(self, sourceFile, hard=False):
        output = ''
        output += 'c\n'
        output += 'c SAT instance in DIMACS CNF input format.\n'
        output += 'c\n'
        if hard:
            output += "p cnf %d %d" % (self.num_vars, len(self.hard_clauses))
        else:
            output += "p wcnf %d %d %d" % (self.num_vars, self.num_clauses, self.top_weight)
        output += '\n'

        if hard:
            for cls in self.hard_clauses:
                output += "%s 0\n" % (' '.join(map(str, cls)))
            write_file(sourceFile, output)
            return

        level_weights = {}
        total = 0
        for level in sorted(self.clauses.keys()):
            level_weights[level] = total
            total += self.level_weight(level, total)

        for cls in self.hard_clauses:
            output += "%d %s 0\n" % (self.top_weight, ' '.join(map(str, cls)))

        for level in self.clauses.keys():
            for (cls, weight) in self.clauses[level]:
                output += "%d %s 0\n" % (weight + level_weights[level], ' '.join(map(str, cls)))

        write_file(sourceFile, output)


class Variable(object):
    def __init__(self, obj):
        self.obj = obj
        self.hash_val = False

    @property
    def var(self):
        return self

    def __str__(self):
        return str(self.obj)

    def __repr__(self):
        return self.__str__()

    def __hash__(self):
        if not self.hash_val:
            self.hash_val = self.__str__().__hash__()
        return self.hash_val

    def __cmp__(self, other):
        return self.__hash__() == other.__hash__()

    def __eq__(self, other):
        return self.__cmp__(other)

    def __neq__(self, other):
        return not self.__cmp__(other)

class Not(Variable):

    @property
    def var(self):
        return self.obj

    def __str__(self):
        return "~" + str(self.obj)
