import xmlrpclib
from time import sleep
import sys

class TreeWindow:
    def __init__(self, time = 30):
        self.connect()
        self.time = time
        
    def connect(self):
        # Create an object to represent our server.
        server_url = 'http://127.0.0.1:20738/RPC2'
        self.server = xmlrpclib.Server(server_url)
        self.G = self.server.ubigraph
        
    def batch(self, arr, delList, colourList):
        #--- Find out the time step
        time_step = float(self.time) / float(len(arr))
        
        #--- Clear the old graph
        self.G.clear()
        
        #--- Create the styles
        #- Default
        self.G.set_vertex_style_attribute(0, "shape", "sphere")
        self.G.set_vertex_style_attribute(0, "size", "0.5")
        
        self.G.set_edge_style_attribute(0, "oriented", "true")
        
        #- Current
        currentStyle = self.G.new_vertex_style(0)
        self.G.set_vertex_style_attribute(currentStyle, "color", "#e76d6d")

        #--- Create the root
        vertexArr = []
        vertexStack = []
        root = self.G.new_vertex()
        self.G.set_vertex_attribute(root, "shape", "icosahedron")
        self.G.set_vertex_attribute(root, "color", "#ff0000")
        self.G.set_vertex_attribute(root, "size", "1.5")
        
        vertexStack.append(root)
        vertexArr.append(root)
        
        
        #--- Build the tree
        delCount = 0
        for dir in arr:
            sleep(time_step)
            
            if dir == 0:
                last = vertexStack.pop()
                
                if vertexStack[len(vertexStack) - 1] != root:
                    self.G.change_vertex_style(vertexStack[len(vertexStack) - 1], currentStyle)
                    
                self.G.change_vertex_style(last, 0)
                self.G.set_vertex_attribute(last, "colour", colourList[len(vertexStack)])
            else:
                parent = vertexStack[len(vertexStack) - 1]
                child = self.G.new_vertex()
                self.G.new_edge(parent, child)
                vertexStack.append(child)
                vertexArr.append(child)
                
                self.G.change_vertex_style(child, currentStyle)
                if parent != root:
                    self.G.change_vertex_style(parent, 0)
                    self.G.set_vertex_attribute(parent, "colour", colourList[len(vertexStack) - 1])
                
                #--- Delete the vertex (to keep a window) if there is one
                if delList[delCount] != None:
                    self.G.remove_vertex(vertexArr[delList[delCount]])
            
            #--- Keep track of where we are in the window    
            delCount += 1
                
    def batch_bounded(self, arr, window = 10):
        #--- Sanity check to see if the window is big enough
        depth = self.getDepth(arr)
        if not depth < window:
            print "Error: The depth of the search tree (" + str(depth) + ") is larger than the viewing window"
            sys.exit()
        
        #--- Build the graph representation
        root = self.Node(0, 0)
        
        #--- Build the delete list
        delList = []
        vertexStack = []
        leafList = []
        
        vertexStack.append(root)
        leafList.append(root)
        
        #--- Simulate and Populate
        total = 0
        for dir in arr:
            if dir == 0:
                delList.append(None)
                vertexStack.pop()
                
            else:
                total += 1
                
                #-- Add the new node
                parent = vertexStack[len(vertexStack) - 1]
                child = self.Node(total, parent)
                vertexStack.append(child)
                leafList.append(child)
                
                #-- Kill the old node
                if total > window:
                    #-- Sort to keep the list populated with the last leaf
                    leafList.sort(sortNodeCompare)
                    delList.append(leafList[0].id)
                    leafList[0].kill()
                    
                else:
                    delList.append(None)
                
        self.batch(arr, delList, self.genColours(arr))
                
        
    
    def batch_unbounded(self, arr):
        delList = []
        for i in arr:
            delList.append(None)
            
        self.batch(arr, delList, self.genColours(arr))
        
    def genColours(self, arr):
        #--- Find the max depth
        max = self.getDepth(arr)
        
        #--- Blend the depth so deepest is red and shallowest is blue
        colourArr = []
        
        for i in range(max + 1):
            #--- Red value
            red = int((float(i) / float(max)) * 255)
            redHex = hex(red).split('x')[1]
            
            #--- Blue value
            blue = int((float(max - i) / float(max)) * 255)
            blueHex = hex(blue).split('x')[1]
            
            if len(redHex) == 1:
                redHex = "0" + redHex
                
            if len(blueHex) == 1:
                blueHex = "0" + blueHex
            
            #--- Add the colour
            colourArr.append("#" + redHex + "00" + blueHex)
            
        return colourArr
    
    def getDepth(self, arr):
        max = 0
        depth = 0
        for i in arr:
            if i == 1:
                depth += 1
            else:
                depth -= 1
                
            if depth > max:
                max = depth
                
        return max
        
    class Node:
        def __init__(self, id, parent):
            self.id = id
            self.parent = parent
            self.children = []
            self.active = True
            if parent == 0:
                self.newChild(self)
                self.kill()
            else:
                self.parent.newChild(self)
            
        def newChild(self, node):
            self.children.append(node)
            
        def leaf(self):
            for n in self.children:
                if n.active:
                    return False
            
            return True
        
        def kill(self):
            self.active = False
        
        def __str__(self):
            return str(self.id)
            
        def __repr__(self):
            return self.__str__()
        
#--- Sort comparison for the Node class when dealing
#---   with bounded search tree displays.
def sortNodeCompare(node1, node2):
    if not node1.active:
        return 1
    if not node2.active:
        return - 1
    
    if node1.leaf() and not node2.leaf():
        return - 1
    if node2.leaf() and not node1.leaf():
        return 1
    
    return node1.id - node2.id

def genDirListFromDepth(depths):
    dirs = []
    for i in range(1, len(depths)):
        count = depths[i] - depths[i - 1]
        
        #--- Downs
        if count > 0:
            for i in range(count):
                dirs.append(1)
        
        #--- Ups
        elif count < 0:
            for i in range(0 - count):
                dirs.append(0)
                
    return dirs
    

if __name__ == '__main__':
    TW = TreeWindow(10)
    
    #TW.batch_unbounded([1,1,1,1,0,1,0,0,1,1,0,1,0,0,0,1,1,1,0,1,0,0,1,1,0,1,0,0,0,0,1,1,1,1,0,1,0,0,1,1,0,1,0,0,0,1,1,1,0,1,0,0,1,1,0,1,0,0,0,0])
    TW.batch_bounded([1, 1, 1, 1, 0, 1, 0, 0, 1, 1, 0, 1, 0, 0, 0, 1, 1, 1, 0, 1, 0, 0, 1, 1, 0, 1, 0, 0, 0, 0, 1, 1, 1, 1, 0, 1, 0, 0, 1, 1, 0, 1, 0, 0, 0, 1, 1, 1, 0, 1, 0, 0, 1, 1, 0, 1, 0, 0, 0, 0], 10)
    
    #TW.batch_unbounded([1,1,1,1,0,1,0,0,1,1,0,1,0,0,0,1,1,1,0,1,0,0,1,1,0,1,0,0,0,0,1,1,1,1,0,1,0,0,1,1,0,1,0,0,0,1,1,1,0,1,0,0,1,1,0,1,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1])
    #TW.batch_bounded([1,1,1,1,0,1,0,0,1,1,0,1,0,0,0,1,1,1,0,1,0,0,1,1,0,1,0,0,0,0,1,1,1,1,0,1,0,0,1,1,0,1,0,0,0,1,1,1,0,1,0,0,1,1,0,1,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1], 10)
