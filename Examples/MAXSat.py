import sys

from krrt.sat import CNF, Dimacs
from krrt.viz import GridViz, DiamondViz

import random

USAGE_STRING = "Usage: python MAXSat.py -i <input-file>"

cnf = Dimacs.nullCNF()

def Example1(next_state):
    state_list = []
    valid_list = []
    
    state_list.append(next_state)
    valid_list.append(True)
    
    for loop in range(1):
        for i in range(50):
            (next_state, delta) = random_heuristic(next_state)
            state_list.append(next_state)
            valid_list.append(True)
        
        for i in range(30):
            (next_state, delta) = greedy_heuristic(next_state)
            state_list.append(next_state)
            valid_list.append(True)
            
        for i in range(30):
            (next_state, delta) = ungreedy_heuristic(next_state)
            state_list.append(next_state)
            valid_list.append(False)
            
        for i in range(20):
            (next_state, delta) = greedy_heuristic(next_state)
            state_list.append(next_state)
            valid_list.append(False)
            
        for i in range(10):
            (next_state, delta) = greedy_heuristic(next_state)
            state_list.append(next_state)
            valid_list.append(True)
            
        for i in range(50):
            (next_state, delta) = random_heuristic(next_state)
            state_list.append(next_state)
            valid_list.append(True)
        
    return (state_list, valid_list)


def Example2(next_state):
    state_list = []
    valid_list = []
    
    state_list.append(next_state)
    valid_list.append(True)
    
    for i in range(10):
        (next_state, delta) = random_heuristic(next_state)
        state_list.append(next_state)
        valid_list.append(True)
    
    for i in range(20):
        (next_state, delta) = greedy_heuristic(next_state)
        state_list.append(next_state)
        valid_list.append(True)
        
    for i in range(20):
        (next_state, delta) = ungreedy_heuristic(next_state)
        state_list.append(next_state)
        valid_list.append(False)
        
    for i in range(5):
        (next_state, delta) = greedy_heuristic(next_state)
        state_list.append(next_state)
        valid_list.append(False)
        
    for i in range(15):
        (next_state, delta) = greedy_heuristic(next_state)
        state_list.append(next_state)
        valid_list.append(True)
        
    for i in range(50):
        (next_state, delta) = random_heuristic(next_state)
        state_list.append(next_state)
        valid_list.append(True)
        
    return (state_list, valid_list)

def Example3(next_state):
    state_list = []
    valid_list = []
    
    state_list.append(next_state)
    valid_list.append(True)
    
    for i in range(50):
        (next_state, delta) = greedy_heuristic(next_state)
        state_list.append(next_state)
        valid_list.append(True)
        
    for i in range(30):
        (next_state, delta) = ungreedy_heuristic(next_state)
        #state_list.append(next_state)
        #valid_list.append(True)
        
    for i in range(30):
        (next_state, delta) = random_heuristic(next_state)
        #state_list.append(next_state)
        #valid_list.append(True)
        
    for i in range(30):
        (next_state, delta) = greedy_heuristic(next_state)
        #state_list.append(next_state)
        #valid_list.append(True)
        
    for i in range(50):
        (next_state, delta) = greedy_heuristic(next_state)
        state_list.append(next_state)
        valid_list.append(True)
        
    return (state_list, valid_list)


def greedy_heuristic(state):
    best_cost = 0
    best_state = []
    best_index = 0
    
    for i in range(len(state) - 1):
        new_state = delta_func(state, (i+1))
        new_cost = cost_func(new_state)
        
        if new_cost > best_cost:
            best_cost = new_cost
            best_state = new_state
            best_index = i+1
            
    
    return (best_state, best_index)

def ungreedy_heuristic(state):
    best_cost = 99999999 # some upper bound on the number of clauses...
    best_state = []
    best_index = 0
    
    for i in range(len(state) - 1):
        new_state = delta_func(state, (i+1))
        new_cost = cost_func(new_state)
        
        if new_cost < best_cost:
            best_cost = new_cost
            best_state = new_state
            best_index = i+1
            
    
    return (best_state, best_index)

def random_heuristic(state):
    num = random.randint(1,(len(state) - 1))
    return (delta_func(state, num), num)

def solve(infile):
    cnf = Dimacs.parseFile(infile)
    
    initial = []
    for i in range(cnf.num_vars + 1):
        #initial.append(rand_sign())
        initial.append(1)
        
    
    gridViz = GridViz.GridViz(initial, cost_func, delta_func, jump_func)
    
    next_state = []
    for val in initial:
        next_state.append(val)
        
    (state_list, valid_list) = Example1(next_state)
    
    DiamondViz.display_diamond(state_list, first_bit_garbage = True)
        
    #--- Get the min and max for graph height
    minVal = cost_func(state_list[0])
    maxVal = cost_func(state_list[0])
    for state in state_list:
        cost = cost_func(state)
        if cost < minVal:
            minVal = cost
        if cost > maxVal:
            maxVal = cost
            
    #--- Entire landscape
    for i in range(1, len(state_list)):
        gridViz.new_state(state_list[i], valid_list[i])
        
    (grid, mask) = gridViz.generate_grid()
    GridViz.display_matrix(grid, grid_mask = mask)
    
    #--- Choose the horizon for the path
    horizon = 100
        
    for i in range(len(state_list) - horizon):
        gridViz = GridViz.GridViz(state_list[i], cost_func, delta_func, jump_func)
        for j in range(i+1, i + horizon):
            gridViz.new_state(state_list[j], valid_list[j])
            
        img = "output/" + str(10000 + i) + ".png"
        if (i % 2) == 1:
            (grid, mask) = gridViz.generate_grid(upFirst = True)
        else:
            (grid, mask) = gridViz.generate_grid(upFirst = False)
            
        GridViz.display_matrix(grid, path_length = (horizon - 25), output_file = img, min = minVal, max = maxVal, grid_mask = mask)
    
 
    
def delta_func(state, var):
    toReturn = []
    for val in state:
        toReturn.append(val)
        
    toReturn[var] *= -1
    
    return toReturn

def cost_func(state):
    count = 0
    for clause in cnf.clauses:
        if clause_sat(clause, state):
            count += 1
            
    return count

def jump_func(start, end):
    #--- Sanity check
    if len(start) != len(end):
        print "Error: jump_func called with two unequal states"
        import os
        os._exit(1)
        
    deltas = []
    for bit in range(len(start)):
        if start[bit] != end[bit]:
            deltas.append(bit)
            
    return deltas

def clause_sat(clause, state):
    for lit in clause.literals:
        if lit.sign == state[lit.num]:
            return True
            
    return False

def rand_sign():
    if random.random() < 0.5:
        return -1
    else:
        return 1

def getopts(argv):
    opts = {}
    while argv:
        if argv[0][0] == '-':                  # find "-name value" pairs
            opts[argv[0]] = argv[1]            # dict key is "-name" arg
            argv = argv[2:]                    
        else:
            argv = argv[1:]
    return opts

if __name__ == '__main__':        
    from sys import argv
    import os
    myargs = getopts(argv)

    if not myargs.has_key('-i'):
        print "Must specify input:"
        print USAGE_STRING
        os._exit(1)
            
    solve(myargs['-i'])

