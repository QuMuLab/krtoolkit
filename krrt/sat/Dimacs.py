import re
from CNF import *

def nullCNF():
    """Return a default CNF Formula (no clauses / variables)"""
    return Formula()

def parseFile(file):
    """Parse a Dimacs CNF file and return the appropriate CNF Formula Object"""
    
    pComment = re.compile('c.*')
    pStats = re.compile('p\s*cnf\s*(\d*)\s*(\d*)')
    
    formula = Formula()
    
    f = open(file, 'r')
    file_lines = f.readlines()
    f.close()
    
    numVars = 0
    numClauses = 0
    
    while len(file_lines) > 0:
        line = file_lines.pop(0)
        
        # Only deal with lines that aren't comments
        if not pComment.match(line):
            m = pStats.match(line)
            
            if m:
                numVars = int(m.group(1))
                numClauses = int(m.group(2))
                
            else:
                nums = line.rstrip('\n').split(' ')
                list = []
                for lit in nums[0:-1]:
                    if lit != '':
                        num = abs(int(lit))
                        sign = 1
                        if int(lit) < 0:
                            sign = -1
                            
                        list.append(Literal(num, sign))
                    
                if len(list) > 0:
                    formula.addClause(Clause(list))
            
        
    formula.setStats(numVars, numClauses)
        
    return formula
    
