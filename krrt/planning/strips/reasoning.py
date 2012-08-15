
def is_applicable(state, action, regress=False):
    """
    Given a state and an action in STRIPS format, return
      whether or not the action is applicable. Alternatively
      decide if the regression is valid or not.
      
        state:   Set of fluent objects.
        action:  Action object.
        reverse: Flag to test for regression validity.
    """
    if not regress:
        return action.precond.issubset(state)
    else:
        return not action.dels.intersection(state)

def progress_state(state, action):
    """
    Given a complete state and an action in STRIPS, progress
      the state and return the new state after applying the
      provided action.
    
        state:  Set of fluent objects.
        action: Action object.
    """
    return (state - action.dels) | action.adds

def regress_state(state, action):
    """
    Given a partial state and an action in STRIPS,
      return the regressed state.
    
        state:  Set of fluent objects.
        action: Action object.
    """
    return (state - action.adds) | action.precond
