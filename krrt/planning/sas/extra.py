
from krrt.utils import read_file, write_file
from krrt.utils.experimentation import get_lines
from krrt.planning.sas import SymbolTable, Operator

from switch_graph import parseSG
from dtg import parseDTG
from cg import parseCG

####################
# Parsing Function #
####################

def parsePRE(filename):
    """
    Given a SAS output file that has gone through preprocessing,
     this function will parse and return the data structures that
     are encoded, including the DTGs, CG, and SG.
    """
    return {
            'dtg': parseDTG(filename),
            'cg': parseCG(filename),
            'sg': parseSG(filename)
            }



########################
# Augmenting Functions #
########################
def augment_SAS_task(task, group_key):
    # Add a dict that maps proposition name to var / val #'s and vice versa
    task.lookupProp = SymbolTable(task.variables)
    task.lookupVarVal = {}
    
    for var_no in range(len(task.lookupProp.variables)):
        var = task.lookupProp.variables[var_no]
        for val_no in range(var.range):
            prop = var.propositions[val_no]
            task.lookupVarVal[prop] = (var_no, val_no)
    
    for op_no in range(len(task.operators)):
        task.operators[op_no].val = op_no

def augment_SAS_props(task, group_key):
    #--- We want to add the val to each proposition and variable
    #-- Additionally we want a mapping from variable name to id
    task.lookupVarID = {}
    #- Iterate through all of the variables
    for v_num in range(len(task.variables)):
        
        v = task.variables[v_num]
        v.val = v_num
        task.lookupVarID[v.name] = v_num
        
        #- Iterate through all of the conditions
        for p_num in range(len(v.propositions)):
            v.propositions[p_num].val = p_num


########################
# Conversion Functions #
########################
def convert_PRE(input, output):
    def cpyrtn(old, new):
        new.append(old[0])
        return old.pop(0)
    
    old_lines = read_file(input)
    new_lines = []
    
    #-- Pop the top MPT flag
    old_lines.pop(0)
    
    #-- Convert the operators back to normal form
    #- Find the operator section
    while 'end_goal' != old_lines[0]:
        new_lines.append(old_lines.pop(0))
    
    new_lines.append(old_lines.pop(0))
    
    #- Get the number of operators
    num_ops = int(old_lines.pop(0))
    new_lines.append(str(num_ops))
    
    for op_num in range(num_ops):
        assert('begin_operator' == cpyrtn(old_lines, new_lines))
        op_name = cpyrtn(old_lines, new_lines)
        
        num_prevail = int(cpyrtn(old_lines, new_lines))
        
        for prev_num in range(num_prevail):
            cpyrtn(old_lines, new_lines)
        
        num_effects = int(cpyrtn(old_lines, new_lines))
        
        for eff_num in range(num_effects):
            preconds = []
            num_precond = old_lines.pop(0)
            
            for precond_num in range(int(num_precond)):
                var, val = old_lines.pop(0).split()
                preconds.append(var + " " + val)
                
            effect = old_lines.pop(0)
            
            new_lines.append(num_precond + " " + " ".join(preconds) + " " + effect)
        
        op_cost = int(cpyrtn(old_lines, new_lines))
        
        assert('end_operator' == cpyrtn(old_lines, new_lines))
    
    #-- Get rid of SG and everything after it.
    while 'begin_SG' != old_lines[0]:
        new_lines.append(old_lines.pop(0))
    
    write_file(output, new_lines)
