import sys

from krrt.sat.CNF import *
from krrt.sat.Dimacs import *
import random
from time import clock


def propagate(theory):
    # We assume that either unit prop or pure literal updates will change the
    #  number of clauses in the theory, so we repeat this process until the
    #  clause count converges.
    cls_count = 0

    while theory.num_clauses != cls_count:
        cls_count = theory.num_clauses
        purelit_prop(theory)
        unit_prop(theory)


def purelit_prop(theory):
    # Get all of the literals seen
    all_lits = set()
    unit_lits = set()
    for c in theory.clauses:
        if 1 == len(c):
            unit_lits.add(list(c)[0])
        for l in c:
            all_lits.add(l)

    # Find the pure non-unit clause lits
    pure_lits = set()
    for v in theory.variables:
        # Check that it isn't already a unit clause
        if (v not in unit_lits) and (v.negate() not in unit_lits):
            # Check that it is pure
            if (v in all_lits) and (v.negate() not in all_lits):
                pure_lits.add(v)
            elif (v not in all_lits) and (v.negate() in all_lits):
                pure_lits.add(v.negate())

    # Add the newly found pure literals as unit clauses
    for lit in pure_lits:
        theory.addClause([lit])


def unit_prop(theory):
    # Separate out all of the unit clauses
    nonUnitClauses = []
    literals = set([])
    for cls in theory.clauses:
        if 1 == len(cls):
            literals.add(list(cls)[0])
        else:
            nonUnitClauses.append(cls)

    # Iterate through subsuming and propagating
    stable = False
    while not stable:
        stable = True
        deleteQueue = set([])
        for i in range(len(nonUnitClauses)):
            cls = nonUnitClauses[i]
            # Check for unit
            if 1 == len(cls):
                literals.add(list(cls)[0])
                deleteQueue.add(i)
                stable = False

            else:
                # Check for subsumption
                for lit in cls:
                    if lit in literals:
                        deleteQueue.add(i)
                        stable = False

                # Check for resolution
                oldSize = len(cls)
                nonUnitClauses[i] = filter(lambda x: x.negate() not in literals, cls)
                if len(nonUnitClauses[i]) != oldSize:
                    stable = False

        deleteInds = list(deleteQueue)
        deleteInds.sort()
        deleteInds.reverse()

        for ind in deleteInds:
            nonUnitClauses.pop(ind)

    all_clauses = list(nonUnitClauses) + [[lit] for lit in literals]
    theory.clauses = all_clauses


USAGE_STRING = "\n\
Usage: python DPLL.py -<option> <argument> -<option> <argument> ... <FLAG> <FLAG> ...\n\n\
        Where options are:\n\
          -i <input-file>\n\
          -timeout <timeout>\n\
          -gui [on|off]\n\
          -showtree [on|off]\n\
          -voh [vsids|static|random]\n\n\
        And the flags include:\n\
          DEBUG\n\
          DISABLE_RESULTS\n\
        "

class DPLL:
    def __init__(self, input, _debug, _timeout, voh):

        #--- Initialize the clauses and variables
        theory = parseFile(input)
        self.clauses = theory.clauses
        self.variables = [(x+1) for x in range(theory.num_vars)]


        #--- Set up the control and statistic variables
        self.debug = _debug
        self.timedout = False

        self.TIMEOUT = _timeout
        self.TARGET_DEPTH = len(self.variables)

        self.MAX_DEPTH = 0
        self.SUM_DEPTH = 0
        self.NODE_COUNT = 0
        self.BACKTRACK_COUNT = 0
        self.DEPTH_LEVELS = []



        #--- Set up the variable ordering heuristic
        if voh == 'static':
            self.pick_var = self.static_pick_var
        elif voh == 'random':
            self.pick_var = self.random_pick_var
        elif voh == 'vsids':
            self.pick_var = self.vsids_pick_var
        else:
            print "Error: Unknown variable ordering heuristic, %s" % voh
            sys.exit(0)

    def solve(self, use_gui, display_search_tree, disable_results):


        self.start_time = clock()

        sols = self.solve_complex(self.clauses, self.variables, 0)

        if 1 == len(sols):
            print str(self.NODE_COUNT) + ",1"

        if disable_results:
            return

        print "Nodes Expanded: " + str(self.NODE_COUNT)
        print "# of Backtracks: " + str(self.BACKTRACK_COUNT)
        print "Max Depth: " + str(self.MAX_DEPTH)
        print "Avg Depth: " + str(self.SUM_DEPTH / self.NODE_COUNT)

        #if display_results:
        if False:
            from pylab import plot, xlabel, ylabel, title, show, subplot
            subplot(3,1,1)
            plot(self.PROFILE_SIZES)
            xlabel('node step')
            ylabel('pool size')
            title('Pool Variation & Solver Depth')

            subplot(3,1,2)
            plot(self.DEPTH_LEVELS)
            xlabel('node step')
            ylabel('depth')

            subplot(3,1,3)
            plot(self.CACHE_SIZES)
            xlabel('node step')
            ylabel('cache size')


            show()

        #if show_tree:
        if False:
            from Visualization.Ubigraph import TreeWindow, genDirListFromDepth
            TW = TreeWindow()

            TW.batch_bounded(genDirListFromDepth(self.DEPTH_LEVELS), 500)
            #TW.batch_unbounded(genDirListFromDepth(self.DEPTH_LEVELS))


        print "\n\nSolution:"
        if self.timedout:
            print " -timeout- "
        else:
            print sols

    def solve_complex(self, clause_list, variable_list, depth_num):
        #------------ DEBUG ---------------
        self.SUM_DEPTH += depth_num
        self.NODE_COUNT += 1
        self.DEPTH_LEVELS.append(depth_num)

        if depth_num > self.MAX_DEPTH:
            self.MAX_DEPTH = depth_num
            print str(self.NODE_COUNT) + "," + str(float(self.MAX_DEPTH) / float(self.TARGET_DEPTH))
            #print str(clock() - self.start_time) + "," + str(float(self.MAX_DEPTH) / float(self.TARGET_DEPTH))
            #print str(clock() - self.start_time) + "," + str(self.MAX_DEPTH)
            #print str(self.NODE_COUNT) + "," + str(self.MAX_DEPTH)


        #---- REMOVE THIS ----#
        if (clock() - self.start_time) > self.TIMEOUT:

            if self.timedout == False:

                print str(self.NODE_COUNT) + "," + str(float(self.MAX_DEPTH) / float(self.TARGET_DEPTH))
                #print str(clock() - self.start_time) + "," + str(self.MAX_DEPTH)
                #print str(self.NODE_COUNT) + "," + str(self.MAX_DEPTH)

            self.timedout = True

            return [0]

        #----------------------------------

        #--- See if we've finished all of the clauses
        if 0 == len(clause_list):
            return []

        #--- Consistency check
        if 0 == len(variable_list):
            print "Error: Remaining clauses and no variables.\n Clause list:"
            print clause_list
            sys.exit(0)

        #--- Pick our variable
        ind, sign = self.pick_var(clause_list, variable_list)
        var = variable_list[ind]

        if self.debug:
            print "Variable and setting picked: " + str(var * sign)

        #--- Set the variable in the clauses
        conflict, new_clause_list = self.set_variable(clause_list, var, sign)

        if conflict:
            #--- Try the other sign
            sign *= -1

            conflict, new_clause_list = self.set_variable(clause_list, var, sign)

            if conflict:
                #--- Both signs break it
                return [0]
            else:
                #--- Try to keep going
                variable_list.pop(ind)
                settings = self.solve_complex(new_clause_list, variable_list, (depth_num+1))
                variable_list.insert(ind, var)

                #--- See if we got a solution
                if len(settings) > 0 and settings[0] == 0:
                    #--- Didn't, so return
                    self.BACKTRACK_COUNT += 1
                    return settings
                else:
                    #--- Append the variable we set
                    settings.append(var * sign)
                    return settings

        else:
            #--- Give the first setting a try
            variable_list.pop(ind)
            settings = self.solve_complex(new_clause_list, variable_list, (depth_num+1))
            variable_list.insert(ind, var)

            #--- See if we got a solution
            if len(settings) > 0 and settings[0] == 0:
                self.BACKTRACK_COUNT += 1

                #--- Try the other setting
                sign *= -1

                conflict, new_clause_list = self.set_variable(clause_list, var, sign)

                if conflict:
                    #--- Both signs break it
                    return [0]
                else:
                    #--- Try to keep going
                    variable_list.pop(ind)
                    settings = self.solve_complex(new_clause_list, variable_list, (depth_num+1))
                    variable_list.insert(ind, var)

                    #--- See if we got a solution
                    if len(settings) > 0 and settings[0] == 0:
                        #--- Didn't, so return
                        self.BACKTRACK_COUNT != 1
                        return settings
                    else:
                        #--- Append the variable we set
                        settings.append(var * sign)
                        return settings

            else:
                #--- Append the variable we set
                settings.append(var * sign)
                return settings

    def set_variable(self, cls_list, var, sign):

        new_clause_list = []
        for clause in cls_list:
            #--- Check to see if the setting violates the clause
            if clause.isUnit():
                if clause.literals[0].num == var and clause.literals[0].sign * sign < 0:
                    return True, []

            #--- Check if the clause is wiped or modified
            affected = False
            for lit in clause.literals:
                if lit.num == var:
                    affected = True
                    if lit.sign * sign < 0:
                        new_clause = clause.copy()
                        new_clause.removeVariable(var)
                        new_clause_list.append(new_clause)
                    else:
                        #--- Do nothing -> clause is wiped
                        pass

            if not affected:
                new_clause_list.append(clause.copy())

        if self.debug:
            print "Clause list before resolving with " + str(var * sign) + ":"
            print cls_list
            print "...and after:"
            print new_clause_list

        return False, new_clause_list


    def static_pick_var(self, cls_list, var_list):
        return len(var_list) - 1, random.choice([-1, 1])

    def random_pick_var(self, cls_list, var_list):
        return random.randint(0, (len(var_list) - 1)), random.choice([-1, 1])

    def vsids_pick_var(self, cls_list, var_list):
        var_count = {}
        for var in var_list:
            var_count[var] = [0,0]

        for clause in cls_list:
            for lit in clause.literals:
                if lit.sign < 0:
                    var_count[lit.num][0] += 1
                else:
                    var_count[lit.num][1] += 1

        max = 0
        best_var = 0
        best_sign = 0
        for (var, pair) in var_count.items():
            if (pair[0] + pair[1]) > max:
                max = pair[0] + pair[1]
                best_var = var
                if pair[0] > pair[1]:
                    best_sign = -1
                else:
                    best_sign = 1

        return var_list.index(best_var), best_sign


def getopts(argv):
    opts = {}
    flags = []
    while argv:
        if argv[0][0] == '-':                  # find "-name value" pairs
            opts[argv[0]] = argv[1]            # dict key is "-name" arg
            argv = argv[2:]
        else:
            flags.append(argv[0])
            argv = argv[1:]
    return opts, flags

if __name__ == '__main__':
    from sys import argv
    import os
    myargs, flags = getopts(argv)

    if not myargs.has_key('-i'):
        print "Must specify input:"
        print USAGE_STRING
        os._exit(1)

    use_gui = True
    if myargs.has_key('-gui'):
        if myargs['-gui'] == "off":
            use_gui = False

    display_search_tree = False
    if myargs.has_key('-showtree'):
        if myargs['-showtree'] == "on":
            display_search_tree = True

    timeout = 120
    if myargs.has_key('-timeout'):
        timeout = int(myargs['-timeout'])

    coh = 'random'
    if myargs.has_key('-voh'):
        voh = myargs['-voh']

    if 'DEBUG' in flags:
        debug = True
    else:
        debug = False

    if 'DISABLE_RESULTS' in flags:
        disable_results = True
    else:
        disable_results = False


    solver = DPLL(myargs['-i'], debug, timeout, voh)
    solver.solve(use_gui=use_gui, display_search_tree=display_search_tree, disable_results=disable_results)
