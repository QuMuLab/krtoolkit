
from krrt.utils import read_file

class AllGroups(object):
    def __init__(self, filename, orig_task, pre_task):
        
        self.groups = []
        
        self.orig_task = orig_task
        self.pre_task = pre_task
        self._parse_file(filename)
        
    
    def _parse_file(self, filename):
        #--- First and last line are useless
        lines = read_file(filename)[1:-1]
        
        #--- Second line is number of groups
        self.num_groups = int(lines.pop(0))
        
        #--- Parse each group
        for i in xrange(self.num_groups):
            self.groups.append(self._parse_group(lines))
        
        #--- Sanity check
        assert 0 == len(lines)
    
    def _parse_group(self, lines):
        #--- First line is 'group'
        assert 'group' == lines.pop(0)
        
        #--- Second line is the number of propositions in the group
        num_props = int(lines.pop(0))
        
        #--- Get each fluent
        props = []
        for i in xrange(num_props):
            entry = lines.pop(0).split(' ')
            old_var = int(entry[0])
            val = int(entry[1])
            
            #-- Translate to the new var # by retrieving the variable name
            new_var = self.pre_task.lookupVarID[self.orig_task.variables[old_var].name]
            
            #-- Add the associated prop object
            props.append(self.pre_task.variables[new_var].propositions[val])
        
        #--- Return the group
        return MutexGroup(props)

class MutexGroup(object):
    def __init__(self, props):
        self.props = props
        