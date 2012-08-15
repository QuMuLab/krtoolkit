
from krrt.utils.experimentation import get_lines

class DTG(object):
    def __init__(self, var_info):
        
        try:
            from pygraph.classes.digraph import digraph
        except:
            print "Error: pygraph not available. Advanced SAS+ reasoning will not work."
            return None
        
        # Parse the info
        self.name = var_info.split()[0]
        domain_size = int(var_info.split()[1])
        self.axiom_layer = int(var_info.split()[2])
        
        # Create the graph
        #  Node: int corresponding to the value of the SAS+ variable
        #  Edge: label that indicates the operators that affect it
        self.graph = digraph()
        self.graph.name = self.name
        self.transition_lookup = {}
        
        # Add a node for each value in the domain
        for i in range(domain_size):
            self.graph.add_node(i)
        
        # Create the accepting states
        self.goal_vals = set([])
        self.init_val = 0
    
    @property
    def domain_size(self):
        return len(self.graph.nodes())
    
    def get_transitions(self, x, y):
        """Return the DTGTransition objects associated with the edge x->y"""
        key_name = str(x) + ' ' + str(y)
        if key_name in self.transition_lookup:
            return self.transition_lookup[key_name]
        else:
            return []
    
    def dot(self, augment = True):
        
        import pygraph
        
        # Get the dot encoding
        dot = pygraph.readwrite.dot.write(self.graph, weighted = True)
        if (not augment) or (self.domain_size == 0) or (len(self.graph.edges()) == 0):
            return dot

        # Split into lines
        dot_lines = dot.split("\n")
        new_dot = []
        
        # First line is the graph header
        new_dot.append(dot_lines[0])
        
        # Next we add some FSA stuff
        new_dot.append("label=%s" % self.graph.name)
        new_dot.append("rankdir=LR;")
        
        # Next is the nodes
        init_nodes = []
        norm_nodes = []
        goal_nodes = []
        index = 1
        while '->' not in dot_lines[index]:
            # Check if the node is an initial or accepting state
            node_id = dot_lines[index].split(';')[0].split('[')[0].rstrip().strip('"')
            if node_id in [str(item) for item in self.goal_vals]:
                goal_nodes.append("node [shape = doublecircle];")
                goal_nodes.append(dot_lines[index])
            elif node_id == str(self.init_val):
                init_nodes.append("node [shape = diamond];")
                init_nodes.append(dot_lines[index])
            else:
                norm_nodes.append("node [shape = circle];")
                norm_nodes.append(dot_lines[index])
            
            index += 1
        
        # Append them in the right order
        new_dot.extend(init_nodes)
        new_dot.extend(norm_nodes)
        new_dot.extend(goal_nodes)
        
        # Add the rest
        for i in range(index, len(dot_lines)):
            new_dot.append(dot_lines[i])
        
        return "\n".join(new_dot)
    
    def setGoal(self, val):
        self.goal_vals.add(val)
    
    def setInit(self, val):
        self.init_val = val
    
    def parse(self, lines):
        
        for val_num in range(self.domain_size):
            num_transitions = int(lines.pop(0))
            
            for trans_num in range(num_transitions):
                
                target_val = int(lines.pop(0))
                op_num = int(lines.pop(0))
                num_conditions = int(lines.pop(0))
                
                newTransition = DTGTransition(val_num, target_val, op_num)
                
                for cond_num in range(num_conditions):
                    var, val = map(int, lines.pop(0).split())
                    newTransition.addCond(var, val)
                
                key_name = str(val_num) + ' ' + str(target_val)
                
                if key_name in self.transition_lookup:
                    self.transition_lookup[key_name].append(newTransition)
                else:
                    self.transition_lookup[key_name] = [newTransition]
                
        #-- After all of the transitions have been sorted out, we add edges to correspond
        #    to the transitions. Label is the operators applicable, and weight is the number
        #    of transitions associated with that edge.
        for key in self.transition_lookup.keys():
            u, v = map(int, key.split())
            opnames = '{' + \
                      ','.join([str(item.op_num) for item in self.transition_lookup[key]]) \
                      + '}'
            # Note: Weight is 1 so the shortest path algorithm works.
            self.graph.add_edge((u, v), wt = 1, label = opnames)
        
        #-- Sanity check
        assert 0 == len(lines)

class DTGTransition(object):
    def __init__(self, source_val, target_val, op_num):
        self.source_val = source_val
        self.target_val = target_val
        self.op_num = op_num
        self.conditions = []

    def addCond(self, var, val):
        self.conditions.append((var, val))


####################
# Parsing Function #
####################

def parseDTG(filename):
    """
    Given a SAS output file that has gone through preproccessing,
     lift and parse the DTG of every variable and return it as a
     list.
    """
    #--- Pull in the DTG text
    DTG_lines = get_lines(filename, 'end_SG', 'begin_CG')
    
    #--- Pull in the variables (just for a count)
    Var_lines = get_lines(filename, 'begin_variables', 'end_variables')
    
    #--- Build all of the DTGs
    dtgs = []
    for i in range(int(Var_lines.pop(0))):
        #-- Discard the first line which is 'begin_DTG'
        assert 'begin_DTG' == DTG_lines.pop(0)
        
        lines = []
        while DTG_lines and DTG_lines[0] != 'end_DTG':
            lines.append(DTG_lines.pop(0))
            
        dtgs.append(DTG(Var_lines[i]))
        dtgs[-1].parse(lines)
        
        #-- Discard the last line which is 'end_DTG'
        assert 'end_DTG' == DTG_lines.pop(0)
    
    assert 0 == len(DTG_lines)
    
    #--- For icing on the cake, we add the initial and goal states
    #- Initial state
    Init_lines = get_lines(filename, 'begin_state', 'end_state')
    for i in range(len(dtgs)):
        dtgs[i].setInit(int(Init_lines[i]))
    
    #- Goal state
    Goal_lines = get_lines(filename, 'begin_goal', 'end_goal')
    num_goals = int(Goal_lines.pop(0))
    for i in range(num_goals):
        var, val = map(int, Goal_lines[i].split())
        dtgs[var].setGoal(val)
    
    return dtgs
