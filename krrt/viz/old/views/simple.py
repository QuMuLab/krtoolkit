
from simple_generated import SimpleView

import wx

######################################
#  Note: Make sure the following
#          line is placed in the
#          slider change handler:
#
#  self.slider_changed_func(self.scrub_slider.GetValue())
#
#

VIEW_OBJ = None

def handle_change(val):
    #- Make sure that the value has indeed changed
    if val != VIEW_OBJ.frame:
        VIEW_OBJ.frame = val
        
        for widget in VIEW_OBJ.small_vizs_top + \
                      VIEW_OBJ.small_vizs_bot + \
                      VIEW_OBJ.large_vizs:
            widget.set_frame(val)
        

class View(object):
    def __init__(self, title):
        global VIEW_OBJ
        VIEW_OBJ = self
        
        self.title = title
        self.frame = 0
        
        self.small_vizs_top = []
        self.small_vizs_bot = []
        self.large_vizs = []
    
    def add_large(self, widget):
        self.large_vizs.append(widget)
    
    def add_small(self, widget, spot = None):
        if not spot:
            if len(self.small_vizs_bot) < len(self.small_vizs_top):
                spot = 'bottom'
            else:
                spot = 'top'
        
        if 'top' == spot:
            self.small_vizs_top.append(widget)
        else:
            self.small_vizs_bot.append(widget)
        
    def run(self):
        #--- Create the window
        simple_view = SimpleView(0)
        top_frame = simple_view.GetTopWindow()
        
        #--- Set up our stuff and make the connections
        top_frame.SetTitle(self.title)
        top_frame.slider_changed_func = handle_change
        
        for widget in self.large_vizs:
            widget.parent = top_frame.notebook_central
            widget.init_widget()
            top_frame.notebook_central.AddPage(widget, widget.title)
        
        for widget in self.small_vizs_top:
            widget.parent = top_frame.notebook_topright
            widget.init_widget()
            top_frame.notebook_topright.AddPage(widget, widget.title)
        
        for widget in self.small_vizs_bot:
            widget.parent = top_frame.notebook_bottomright
            widget.init_widget()
            top_frame.notebook_bottomright.AddPage(widget, widget.title)
        
        #--- Run the GUI
        #
        #         NOTE: This is a blocking call
        #
        simple_view.MainLoop()
