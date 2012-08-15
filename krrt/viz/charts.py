##################################
# This file contains widgets
#  that correspond to charts
#  from matplotlib.
#############################


class ScatterPlot(object):
    def __init__(self, title, xs, ys):
        try:
            import matplotlib.pyplot as plt
        except:
            print "Error: matplotlib not available. Charts will not work."
            return None
        # Todo: Write me
        pass
