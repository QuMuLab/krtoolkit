
from charts import ScatterPlot

# Check the xdot dependencies
xdot_ok = True
try:
    import os
    import sys
    import subprocess
    import math
    import colorsys
    import time
    import re

    import gobject
    import gtk
    import gtk.gdk
    import gtk.keysyms
    import cairo
    import pango
    import pangocairo
    
except:
    print "Warning: xdot not available. Please check the dependency list."
    xdot_ok = False

if xdot_ok:
    from lib import xdot

