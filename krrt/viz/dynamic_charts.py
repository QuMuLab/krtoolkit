##################################
# This file contains widgets
#  that correspond to dynamic
#  charts from matplotlib.
#############################

try:
    import matplotlib.pyplot as plt
except:
    print ("Warning: matplotlib not available. Charts will not work.")

class DynamicAreaGraph(object):
    def __init__(self, title, xs, ys, color):
        
        self.xs = [xs[0]] + xs + [xs[-1]]
        self.ys = [min(ys)] + ys + [min(ys)]
        self.color = color
        
        self.figure = plt.figure()
        self.plot = self.figure.add_subplot(111)
        
        self.plot.grid(False)
        self.plot.xaxis.set_visible(False)
        self.plot.yaxis.set_visible(False)
        
        self.plot.fill(self.xs, self.ys, color = self.color)
        self.plot.set_title(title)
        

    def set_frame(self, frame):
        #--- Make this figure the current one
        plt.figure(self.figure.number)
        
        self.ys[-2] = frame
        self.plot.clear()
        self.plot.fill(self.xs, self.ys, color = self.color)
