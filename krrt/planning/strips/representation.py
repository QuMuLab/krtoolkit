
from krrt.utils import read_file
from krrt.planning.pddl import open as parsePDDL
from krrt.planning.pddl import Assign, Atom, Conjunction, NegatedAtom
from krrt.planning.pddl.instantiate import explore
from krrt.planning import Action as GroundAction

# Degrade gracefully when using python < 2.6
try:
    from itertools import product
except:
    def product(*args, **kwds):
        # product('ABCD', 'xy') --> Ax Ay Bx By Cx Cy Dx Dy
        # product(range(2), repeat=3) --> 000 001 010 011 100 101 110 111
        pools = map(tuple, args) * kwds.get('repeat', 1)
        result = [[]]
        for pool in pools:
            result = [x+[y] for x in result for y in pool]
        for prod in result:
            yield tuple(prod)

class Action(GroundAction):
    def __init__(self, precond = None, adds = None, dels = None, line = 'unknown unknown', cost = 1):
        self.precond = precond or set([])
        self.adds = adds or set([])
        self.dels = dels or set([])
        self.line = line
        self.cost = cost
        GroundAction.__init__(self, line)

    def addPrecond(self, fluent):
        self.precond.add(fluent)

    def addAdd(self, fluent):
        self.adds.add(fluent)

    def addDel(self, fluent):
        self.dels.add(fluent)

    def copy(self):
        return Action(self.precond.copy(), self.adds.copy(), self.dels.copy(), self.line, self.cost)

class Fluent(object):
    def __init__(self, name):
        self.name = name
        self.hash_val = name.__hash__()

    def __str__(self):
        return "(%s)" % self.name

    def __repr__(self):
        return self.__str__()

    def __hash__(self):
        return self.hash_val

    def __cmp__(self, other):
        return self.__hash__() == other.__hash__()

    def __eq__(self, other):
        return self.__cmp__(other)

    def __neq__(self, other):
        return not self.__cmp__(other)

def parse_init_state(pddl_domain_name, pddl_file_name):

    t = parsePDDL(task_filename=pddl_file_name, domain_filename=pddl_domain_name)

    # Lift the initial state
    inits = set([])
    for init in t.init:
        # We don't want to keep around the trivial equality constraints
        if Assign == init.__class__:
            continue

        if Atom != init.__class__:
            print ("Error: Init condition not an Atom -- " + str(init.__class__))
            return set([])

        fluent = str(init.predicate)

        for arg in init.args:
            fluent += ' ' + str(arg)

        inits.add(Fluent(fluent))

    return inits

def parse_goal_state(pddl_domain_name, pddl_file_name):

    t = parsePDDL(task_filename=pddl_file_name, domain_filename=pddl_domain_name)

    # Only lift the goal if it is a conjunction of atoms
    if Conjunction != t.goal.__class__:
        print ("Error: Goal condition must be a conjunction of atoms -- " + str(t.goal.__class__))
        return set([])

    # Lift the goal state
    goals = set([])
    for g in t.goal.parts:
        if Atom != g.__class__:
            print ("Error: Goal condition not an Atom -- " + str(init.__class__))
            return set([])

        fluent = str(g.predicate)

        for arg in g.args:
            fluent += ' ' + str(arg)

        # We don't want to keep around the trivial equality constraints
        if fluent[0] != '=':
            goals.add(Fluent(fluent))

    return goals

def generate_action(action, act):

    print ("Warning: This code is deprecated. Please report your usage to a developer.")

    params = act.arguments

    assert len(params) == len(action.parameters)

    mapping = {}
    for i in range(len(params)):
        mapping[action.parameters[i].name] = params[i]

    PRE = set([])
    ADD = set([])
    DEL = set([])

    for p in action.precondition.parts:
        name = ' '.join([p.predicate] + map(lambda x: mapping[x], p.args))
        PRE.add(Fluent(name))

    for eff in action.effects:
        name = ' '.join([eff.literal.predicate] + map(lambda x: mapping[x], eff.literal.args))
        if eff.literal.__class__ == NegatedAtom:
            DEL.add(Fluent(name))
        elif eff.literal.__class__ == Atom:
            ADD.add(Fluent(name))
        else:
            print ("Error: Effect isn't an Atom or NegatedAtom: %s" % str(eff.literal.__class__))
            return None

    return Action(PRE, ADD, DEL, ' '.join([act.operator] + act.arguments))

def parse_problem(pddl_domain_name, pddl_file_name):

    # Get the init and goal conditions
    I = parse_init_state(pddl_domain_name, pddl_file_name)
    G = parse_goal_state(pddl_domain_name, pddl_file_name)

    # Parse our task
    t = parsePDDL(task_filename=pddl_file_name, domain_filename=pddl_domain_name)
    _, atoms, actions, _, _ = explore(t)

    F = set([])
    FMAP = {}
    for atom in atoms:
        fname = ' '.join([atom.predicate] + list(atom.args))
        f = Fluent(fname)
        F.add(f)
        FMAP[fname] = f

    A = {}
    for a in actions:
        PRE = set([])
        ADD = set([])
        DEL = set([])

        for p in a.precondition:
            assert not p.negated, "Error: Cannot handle negative preconditions"
            PRE.add(FMAP[' '.join([p.predicate] + list(p.args))])

        for cond, fact in a.add_effects:
            ADD.add(FMAP[' '.join([fact.predicate] + list(fact.args))])

        for cond, fact in a.del_effects:
            DEL.add(FMAP[' '.join([fact.predicate] + list(fact.args))])

        A[a.name[1:-1].lower().strip()] = Action(PRE, ADD, DEL, a.name[1:-1].lower().strip())

    return (F, A, I, G)
