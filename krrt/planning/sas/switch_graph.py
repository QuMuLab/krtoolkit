
from krrt.utils.experimentation import get_lines

class SwitchNode(object):
    def __init__(self, var, range, parent):
        self.var = var
        self.range = range
        self.opNode = None
        self.choices = {}
        self.alwaysNode = None
        self.parent = parent
    
    def add_ops(self, opNode):
        self.opNode = opNode
    
    def add_choice(self, choice, node):
        self.choices[choice] = node
    
    def add_always(self, alwaysNode):
        self.alwaysNode = alwaysNode
    
    def gen_output(self):
        toReturn = "switch %d\n" % self.var
        toReturn += self.opNode.gen_output()
        for i in range(self.range):
            toReturn += self.choices[i].gen_output()
        toReturn += self.alwaysNode.gen_output()
        
        return toReturn
        
    @property
    def label(self):
        return str(self.var)
    
    def __str__(self):
        return str(self.__hash__())
    
class LeafNode(object):
    def __init__(self, ops, parent):
        self.ops = ops
        self.parent = parent
    
    def gen_output(self):
        toReturn = "check %d\n" % len(self.ops)
        for op in self.ops:
            toReturn += "%d\n" % op
        
        return toReturn
    
    @property
    def label(self):
        return str(self.ops)
    
    def __str__(self):
        return str(self.__hash__())
            
class SG(object):
    
    def __init__(self, var_lines):
        
        try:
            from pygraph.classes.digraph import digraph
        except:
            print ("Error: pygraph not available. Advanced SAS+ reasoning will not work.")
            return None
        
        self.graph = digraph()
        self.graph.name = 'SuccessorGraph'
        self.var_names = []
        self.var_ranges = []
        
        self.root = None
        
        for var in var_lines:
            var_name, var_size, _ = var.split()
            self.var_names.append(var_name)
            self.var_ranges.append(int(var_size))
    
    def gen_output(self):
        return "begin_SG\n" + self.root.gen_output() + "end_SG\n"
    
    def parse(self, lines, parent, index = 0):
        if 'check' == lines[index][:5]:
            lNode, index = self._parse_leaf(lines, parent, index)
            self.graph.add_node(lNode, [('label', lNode.label)])
            return lNode, index
        
        #--- Get the variable
        var = int(lines[index].split(' ')[1])
        index += 1
        
        #--- Create the node
        sNode = SwitchNode(var, self.var_ranges[var], parent)
        self.graph.add_node(sNode, [('label', sNode.label)])
        
        #--- Parse the 'immediately' operators
        lNode, index = self._parse_leaf(lines, sNode, index)
        self.graph.add_node(lNode, [('label', lNode.label)])
        self.graph.add_edge((sNode, lNode), label = 'immediately')
        sNode.add_ops(lNode)
        
        #--- Parse each of the cases
        for i in range(sNode.range):
            cNode, index = self.parse(lines, sNode, index)
            self.graph.add_edge((sNode, cNode), label = str(i))
            sNode.add_choice(i, cNode)
        
        #--- Parse the 'always' operators
        cNode, index = self.parse(lines, sNode, index)
        self.graph.add_edge((sNode, cNode), label = 'always')
        sNode.add_always(cNode)
        
        return sNode, index
    
    def _parse_leaf(self, lines, parent, index):
        assert 'check' == lines[index][:5]
        
        num = int(lines[index].split(' ')[1])
        index += 1
        
        ops = []
        for i in range(num):
            ops.append(int(lines[index]))
            index += 1
        
        #- Create the node
        lNode = LeafNode(ops, parent)
        
        return lNode, index
    
    def dot(self):
        import pygraph
        return pygraph.readwrite.dot.write(self.graph, weighted = False)


####################
# Parsing Function #
####################

def parseSG(filename):
    """
    Given a SAS output file that has gone through preproccessing,
     parse and return the successor generator data structure.
    """
    
    #--- Pull in the SG text
    SG_lines = get_lines(filename, 'begin_SG', 'end_SG')
    
    #--- Pull in the variables
    Var_lines = get_lines(filename, 'begin_variables', 'end_variables')
    
    #--- Build the SG
    sg = SG(Var_lines[1:])
    sg.root = sg.parse(SG_lines, None)[0]
    
    return sg
