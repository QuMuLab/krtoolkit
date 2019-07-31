from .sas_tasks import read as parseSAS_Old
from .sas_tasks import SasTask, Variable, Proposition, Operator, Axiom
from .sas_tasks import SymbolTable

from .statistics import Statistics

from .group_keys import read as parseGroups
from .group_keys import Group, GroupKey

from .dtg import DTG, DTGTransition, parseDTG
from .cg import CG, parseCG

from .switch_graph import SG, parseSG
from .switch_graph import SwitchNode as SGSwitchNode
from .switch_graph import LeafNode as SGLeafNode

from .mutex_groups import AllGroups, MutexGroup

from .extra import parsePRE
from .extra import augment_SAS_task, augment_SAS_props
from .extra import convert_PRE

def parseSAS(filename, key_filename):
    task = parseSAS_Old(filename, key_filename)
    group_key = parseGroups(key_filename)
    
    augment_SAS_task(task, group_key)
    augment_SAS_props(task, group_key)
    
    return task
