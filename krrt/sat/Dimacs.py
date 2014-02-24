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
    
    while len(file_lines) > 0:
        line = file_lines.pop(0)
        
        # Only deal with lines that aren't comments
        if not pComment.match(line) and not pStats.match(line):
            nums = line.rstrip('\n').split(' ')
            cls = []
            for lit in nums[:-1]:
                if lit != '':
                    num = abs(int(lit))
                    if int(lit) < 0:
                        cls.append(Not(num))
                    else:
                        cls.append(num)
            
            if len(cls) > 0:
                formula.addClause(cls)
    
    return formula
    
