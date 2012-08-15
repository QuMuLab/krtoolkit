
from krrt.utils.experimentation import get_lines

class CG(object):
    def __init__(self, var_lines):
        try:
            import pygraph
        except:
            print "Error: pygraph is not available. Advanced SAS+ reasoning requires pygraph."
            return None
        
        self.graph = digraph()
        self.graph.name = 'CausalGraph'
        self.var_names = []
        
        for var in var_lines:
            var_name, var_size, _ = var.split()
            
            self.graph.add_node(var_name, [('size', var_size)])
            self.var_names.append(var_name)
    
    @property
    def size(self):
        return len(self.graph.nodes())
    
    def dot(self):
        from pygraph.readwrite.dot import write as write_dot
        return write_dot(self.graph, weighted = True)
    
    def isAcyclic(self):
        import pygraph
        return 0 == len(pygraph.algorithms.cycles.find_cycle(self.graph))
    
    def parse(self, lines):
        
        for var in self.var_names:
            num_edges = int(lines.pop(0))
            for edge in range(num_edges):
                _target, weight = map(int, lines.pop(0).split())
                target = self.var_names[_target]
                self.graph.add_edge((var, target), wt = weight)
        
        assert 0 == len(lines)


####################
# Parsing Function #
####################

def parseCG(filename):
    """
    Given a SAS output file that has gone through preproccessing,
     lift and parse the causal graph and return a CG object.
    """
    #--- Pull in the CG text
    CG_lines = get_lines(filename, 'begin_CG', 'end_CG')
    
    #--- Pull in the variables
    Var_lines = get_lines(filename, 'begin_variables', 'end_variables')
    
    #--- Build the CG
    cg = CG(Var_lines[1:])
    cg.parse(CG_lines)
    
    return cg
