import math
from numpy import *
from pylab import plot, xlabel, ylabel, title, show, savefig
#import matplotlib.axes3d as p3
#import scipy


def display_diamond(state_list, output_file = None, first_bit_garbage = False, use_points = False):
    #--- Get rid of the first bit if we don't need it, and turn -1 into 0
    state_list = prep_list(state_list, first_bit_garbage)
    
    #--- First build the diamond
    diamond1 = []
    diamond2 = []
    
    size = len(state_list[0])
    
    diamond1.append(float(size) / 2.0)
    diamond2.append(float(size) / 2.0)
    
    for i in range(1,(size)):
        width = minimum(i, (size - i))
        
        diamond1.append((float(size) / float(2)) + float(width))
        diamond2.append((float(size) / float(2)) - float(width))
        
    diamond1.append(float(size) / float(2))
    diamond2.append(float(size) / float(2))
    
    plot(diamond1, 'b')
    plot(diamond2, 'b')
    
    #--- Now build the path
    pathX = []
    pathY = []
    for state in state_list:
        pathX.append(getX(state))
        pathY.append(getY(state))
    
    if use_points:
        plot(pathX, pathY, 'r,')
    else:
        plot(pathX, pathY, 'r')
    
    xlabel('weight')
    ylabel('relative location of 1\'s')
    title('Search Landscape')
    
    if output_file:
        savefig(output_file)
    else:
        show()

def display_heat_diamond(state_list, sample_size):
    import pylab as p
    import matplotlib.axes3d as p3
    
    #--- Get rid of the first bit if we don't need it, and turn -1 into 0
    list = prep_list(state_list, False)
    
    #--- First build the diamond
    diamond1 = []
    diamond2 = []
    
    size = len(list[0]) + 1
    
    diamond1.append(float(size) / 2.0)
    diamond2.append(float(size) / 2.0)
    
    for i in range(1,(size)):
        width = minimum(i, (size - i))
        
        diamond1.append((float(size) / float(2)) + float(width))
        diamond2.append((float(size) / float(2)) - float(width))
        
    diamond1.append(float(size) / float(2))
    diamond2.append(float(size) / float(2))
    
    #plot(diamond1, 'b')
    #plot(diamond2, 'b')
    
    #--- Now build the heat map
    
    #-- Init the grid
    grid = []
    for i in range(size):
        grid.append([])
        
        for j in range(size):
            grid[i].append(0)
            
    #-- Fill in the grid
    for state in list:
        
        x = getX(state)
        y = int(getY(state))
        
        #print "(" + str(getX(state)) + "," + str(getY(state)) + ")"
        
        #print str(x) + "," + str(y)
        grid[x][y] += float(1) / float(len(list))
    
    
    
    
    #for row in range(len(grid)):
    #    for col in range(len(grid[0])):
    #        print grid[row][col],
    #    print "\n",
    
    
    
    data = []
    path_x = []
    path_y = []
    path_z = []
    
    for row in range(len(grid)):
        for col in range(len(grid[0])):
            data.append((col,row,grid[row][col]))
    
    x_step = 1 / float(len(grid[0]))
    y_step = 1 / float(len(grid))
            
    X, Y = meshgrid(arange(0, 1.0, x_step), arange(0, 1.0, y_step))
    
    Z = zeros((len(Y), len(X)), 'Float32')
    for d in data:
        x, y, z = d
        ix = int(x)
        iy = int(y)
        Z[iy, ix] = z
        
    
    fig = p.figure()
    ax = p3.Axes3D(fig)
    ax.plot_wireframe(X, Y, Z)
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('probability')
    
    p.show()
    

def getX(state):
    count = 0
    for bit in state:
        if bit == 1:
            count += 1
            
    return count

def getY(state):
    ones = getX(state)
    
    #--- Sanity Check
    if (ones == len(state)) or (ones == 0):
        return (float(len(state))/2)
    
    width = getYWidth(state)
    
    return _getY(state, ((float(len(state))/2) - float(width)), ((float(len(state))/2) + float(width)))

def getYWidth(state):
    ones = getX(state)
    
    return minimum(ones, (len(state) - ones))

def _getY(state, min, max):
    ones = getX(state)
    size = len(state)
    
    sumMin = 0
    sumMax = 0
    
    for i in range(0,(size - ones)):
        sumMin += i
        
    for i in range(ones, size):
        sumMax += i
    
    #print "(min,max) for " + str(ones) + " = (" + str(sumMin) + "," + str(sumMax) + ") -> (" + str(min) + "," + str(max) + ")"
    
    sum = 0
    for i in range(len(state)):
        if state[i] == 0:
            sum += i
    
    ratio = float(sum - sumMin) / float(sumMax - sumMin)
    
    amount = ratio * float(max - min)
    
    return amount + min

def prep_list(list, garbage_bit):
    #--- Copy
    toReturn = []
    from copy import copy
    for state in list:
        toReturn.append(copy(state))
    
    for state in toReturn:
        if garbage_bit:
            state.pop(0)
        
        for i in range(len(state)):
            if state[i] == -1:
                state[i] = 0
            
    return toReturn

def rand_sign():
    import random
    if random.random() < 0.5:
        return -1
    else:
        return 1
    
def ham_dist(state1, state2):
    count = 0
    for i in range(len(state1)):
        if state1[i] != state2[i]:
            count += 1
            
    return count

if __name__ == '__main__':
    #list = [[0,0,0,1],[0,1,0,1],[1,1,0,1],[1,1,0,0]]
    list = []
    #for i in range(100000):
    for i in range(1000):
        item = []
        for i in range(100):
            item.append(rand_sign())
            
        list.append(item)
            
    display_heat_diamond(list, 1000)