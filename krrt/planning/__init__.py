
#############
## Parsers ##
#############
class Plan():
    def __init__(self, actions=None):
        self.actions = actions or []

    def add_actions(self, new_actions):
        self.actions.extend(new_actions)

    def write_to_file(self, file_name):
        # Write the script to a file
        f = open(file_name, 'w')

        step = 0
        for action in self.actions:
            line = str(step) + ': (' + action.operator + ' ' + ' '.join(action.arguments) + ") [1]\n"
            f.write(line)
            step += 1

        f.close()

    def get_action_sequence(self):
        return [item.operator for item in self.actions]

class Action():
    def __init__(self, line):
        self.operator = line.split(' ')[0]
        self.arguments = line.split(' ')[1:]

    def compact_rep(self):
        toReturn = self.operator
        for arg in self.arguments:
            toReturn += "\\n" + str(arg)
        return toReturn

    def __str__(self):
        return "(" + ' '.join([self.operator] + self.arguments) + ")"

    def __repr__(self):
        return self.__str__()

def parse_output_FF(file_name):
    from krrt.utils import match_value, get_lines

    # Check for the failed solution
    if match_value(file_name, '.* No plan will solve it.*'):
        print "No solution."
        return None

    # Get the plan
    ff_actions = get_lines(file_name,
                            lower_bound='.*found legal plan.*',
                            upper_bound='.*time spent.*')

    ff_actions = filter(lambda x: x != '', [item.strip(' ') for item in ff_actions])

    ff_actions = [item.split(':')[1].strip(' ').lower() for item in ff_actions]

    actions = [Action(item) for item in ff_actions]

    return Plan(actions)

def parse_output_lapkt(file_name):
    from krrt.utils import read_file

    # Check for the failed solution
    #if match_value(file_name, '.* No plan will solve it.*'):
    #    print "No solution."
    #    return None

    # Get the plan
    action_list = read_file(file_name)

    actions = [Action(line[1:-1].strip(' ').lower()) for line in action_list]

    return Plan(actions)

def parse_output_popf(file_name):
    from krrt.utils import match_value, get_lines

    # Check for the failed solution
    if not match_value(file_name, '.*;;;; Solution Found.*'):
        print "No solution."
        return None

    # Get the plan lines
    popf_actions = get_lines(file_name, lower_bound = ';;;; Solution Found')[1:]

    time_slots = [popf_actions[0].split(':')[0]]
    for act in popf_actions:
        if time_slots[-1] != act.split(':')[0]:
            time_slots.append(act.split(':')[0])

    layered_solution = []
    for time in time_slots:
        actions = filter(lambda x: x.split(':')[0] == time, popf_actions)
        layered_solution.append([])
        for act in actions:
            action_line = act.split('(')[1].split(')')[0]
            layered_solution[-1].append(Action(action_line))

    return layered_solution


def parse_output_VAL(file_name, initialState):





    # TODO: Fix this...it probably doesn't work.





    # Get the plan
    VAL_output = exp.get_lines(file_name,
                               lower_bound='.*-----------------------.*',
                               upper_bound='.*Plan executed successfully.*')

    # Each item is now an action's add/delete effects
    VAL_output = ('\n'.join(VAL_output)).split('\n\n')

    # Strip the newlines
    VAL_output = [item.strip('\n') for item in VAL_output]

    # Get rid of the timing info and split the lines up
    VAL_output = [item.split('\n')[1:] for item in VAL_output]

    # Put them in the form of (add, delete) lists
    deltas = []
    for item in VAL_output:
        adds = []
        dels = []
        for eff in item:
            if eff[0:8] == 'Deleting':
                dels.append(eff.split('(')[1].split(')')[0])
            elif eff[0:6] == 'Adding':
                adds.append(eff.split('(')[1].split(')')[0])
            else:
                print "Error: " + eff[0:8] + " / " + eff[0:6]

        deltas.append((adds, dels))

    states = [initialState]
    for (adds, dels) in deltas:
        newState = states[-1].apply_changes(adds, dels)
        states.append(newState)

    return states

#################
# Other imports #
#################
import pddl
import sas
import strips
