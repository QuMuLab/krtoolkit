#######################################
## Useful plotting methods for pylab ##
#######################################

USAGE_STRING = """
Usage: python plots.py <flag> -option <value> ...

        Where options may be:
          csv: The path to the csv file. (mandatory)
          title: The graph title.
          xlabel: The x-axis label
          ylabel: The y-axis label
          legend: The legend name
          
        Where flags may be:
          useheader: Use the first line of the csv as header data.
          xlog: Use a log scale for the x-axis
          ylog: Use a log scale for the y-axis
          noxtics: Turn of the x-axis tick marks
          noxy: Disable the x=y line
          noscatter: Use a regular line graph, and not a scatter plot
          nosymbols: Don't display the symbols (assumes noscatter is used)
          bw: Use black and white
          multplots: Display multiple plots (x is first column, each subsequent is a plot) (assumes useheader)
          
        """

#SYMBOLS = ['-','--','-.',':','.',',','o','^','v','<','>','s','+','x','D','d','1','2','3','4','h','H','p']
SYMBOLS = ['s', 'x', 'o', '^', '>', 'v', '<', 'd', 'p', 'h', '8']
COLOURS = ['b','g','r','c','m','y','k']

def get_figsize(fig_width_pt):
    import math
    inches_per_pt = 1.0/72.0                # Convert pt to inch
    golden_mean = (math.sqrt(5)-1.0)/2.0    # Aesthetic ratio
    fig_width = fig_width_pt*inches_per_pt  # width in inches
    fig_height = fig_width*golden_mean     # height in inches
    fig_size =  [fig_width,fig_height]      # exact figsize
    return fig_size

# Publishable quality image settings for 2-column papers
params_twocolumn = {'backend': 'eps',
                    'legend.pad': 0.1,    # empty space around the legend box
                    'legend.fontsize': 11,
                    'lines.markersize': 3,
                    'font.size': 12,
                    'font.family': 'serif',
                    'ps.usedistiller': 'xpdf',
                    #'font.family': 'sans-serif',
                    'font.serif': 'Times New Roman',
                    #'font.sans-serif': 'Helvetica',
                    'text.usetex': True,
                    'figure.figsize': get_figsize(250)}

# Medium size charts (not yet complete)
params_onecolumn = {'backend': 'eps',
                    'axes.labelsize': 16,
                    'text.fontsize': 12,
                    'xtick.labelsize': 12,
                    'ytick.labelsize': 12,
                    'legend.pad': 0.1,    # empty space around the legend box
                    'legend.fontsize': 12,
                    'lines.markersize': 3,
                    'font.size': 12,
                    'font.family': 'serif',
                    #'font.family': 'sans-serif',
                    'font.serif': 'Times New Roman',
                    #'font.sans-serif': 'Helvetica',
                    'text.usetex': True,
                    'ps.usedistiller': 'xpdf',
                    'figure.figsize': get_figsize(500)}

def plot_from_file(csvfile, title = None, use_header = True, xlog = False, ylog = False, no_x_tics = False, noxy = False, no_scatter = False, bw = False, mult_plots = False, xlabel = "", ylabel = "", legendname = "Legend", nosymbols = False):
    from krrt.utils import load_CSV
    
    data = load_CSV(csvfile)
    
    if use_header:
        header = data.pop(0)
    else:
        header = ['x-axis', 'y-axis', 'Legend']
    
    if mult_plots:
        
        num_plots = len(data[0]) - 1
        x = [float(item[0]) for item in data]
        
        xs = []
        ys = []
        ps = []
        
        assert use_header
        
        for i in range(1, num_plots+1):
            
            y = [float(item[i]) for item in filter(lambda x: x[i] != '', data)]
            
            xs.append(x[:len(y)])
            ys.append(y)
            ps.append(header[i])
            
        plot(xs, ys, x_label = header[0], y_label = ylabel, x_log = xlog, y_log = ylog, names = ps, graph_name = title, legend_name = legendname, disable_x_tics = no_x_tics, xyline = not noxy, no_scatter = no_scatter, col = not bw, nosymbols = nosymbols)
        
        return
    if len(data[0]) > 2:
        data_keys = sorted(list(set([item[2] for item in data])))
        
        xs = []
        ys = []
        ps = []
        
        for key in data_keys:
            relevant_data = filter(lambda x: x[2] == key, data)
            xs.append([])
            ys.append([])
            ps.append(key)
            for line in relevant_data:
                xs[-1].append(float(line[0]))
                ys[-1].append(float(line[1]))
        
        plot(xs, ys, x_label = header[0], y_label = header[1], x_log = xlog, y_log = ylog, names = ps, graph_name = title, legend_name = header[2], disable_x_tics = no_x_tics, xyline = not noxy, no_scatter = no_scatter, col = not bw, nosymbols = nosymbols)

    else:
        
        xs = []
        ys = []
        
        for d in data:
            xs.append(float(d[0]))
            ys.append(float(d[1]))
        
        plot ([xs], [ys], x_label = header[0], y_label = header[1], x_log = xlog, y_log = ylog, graph_name = title, disable_x_tics = no_x_tics, xyline = not noxy, no_scatter = no_scatter, col = not bw, nosymbols = nosymbols)

def plot_loglog(x, y, x_label = '', y_label = '', col = True, names = None, graph_name = None, legend_name = None, xyline = True):
    plot(x, y, x_label, y_label, col, True, True, names, graph_name, legend_name, xyline)
    
def plot(x, y,
         x_label = "",
         y_label = "",
         col = True,
         x_log = False,
         y_log = False,
         names = None,
         graph_name = None,
         legend_name = None,
         xyline = True,
         disable_x_tics = False,
         no_scatter = False,
         nosymbols = False,
         makesquare = False):

    try:
        import pylab
    except:
        print "Error: pylab not available. Plotting features will not work."
        return
    
    #pylab.rcParams.update(params_onecolumn)
    pylab.rcParams.update(params_twocolumn)
    
    
    if x[0].__class__ != list:
        x = [x]
        y = [y]
    
    if not col:
        if len(x) > len(SYMBOLS):
            print "Warning: Too many types (%d) for only %d symbols." % (len(x), len(SYMBOLS))
            return
    
    else:
        if len(x) > len(COLOURS):
            print "Warning: Too many types (%d) for only %d colours." % (len(x), len(COLOURS))
            return
    
    
    pylab.figure(1)
    pylab.clf()
    
    if disable_x_tics:
        ax = pylab.axes([0.14,0.14,0.95-0.14,0.95-0.14])
        #ax = pylab.axes([0.16,0.14,0.95-0.16,0.95-0.14]) # Use this when 10^-1 kicks out the y-label
    else:
        ax = pylab.axes([0.14,0.2,0.95-0.14,0.95-0.2])
        #ax = pylab.axes([0.16,0.22,0.95-0.16,0.95-0.22])
    
    if x_log:
        ax.set_xscale('log')
    if y_log:
        ax.set_yscale('log')
    
    # Plot
    BOT_NUMS = [99999.0, 99999.0]
    TOP_NUMS = [0.0, 0.0]
    handles = []
    xy_line_col = 'b'
    
    for i in range(len(x)):
        
        if col:
            if no_scatter:
                if nosymbols:
                    handles.append(ax.plot(x[i], y[i], c=COLOURS[i]))
                else:
                    handles.append(ax.plot(x[i], y[i], c=COLOURS[i], marker='s'))
            else:
                handles.append(ax.scatter(x[i], y[i], s=40, c=COLOURS[i], marker='s'))
        else:
            xy_line_col = 'k'
            if no_scatter:
                if nosymbols:
                    handles.append(ax.plot(x[i], y[i], c='k'))
                else:
                    handles.append(ax.plot(x[i], y[i], c='k', marker=SYMBOLS[i]))
            else:
                handles.append(ax.scatter(x[i], y[i], s=40, c='k', marker=SYMBOLS[i]))
        
        if TOP_NUMS[0] < max(x[i]):
            TOP_NUMS[0] = max(x[i])
        if TOP_NUMS[1] < max(y[i]):
            TOP_NUMS[1] = max(y[i])
        
        if BOT_NUMS[0] > min(x[i]):
            BOT_NUMS[0] = min(x[i])
        if BOT_NUMS[1] > min(y[i]):
            BOT_NUMS[1] = min(y[i])
        
    
    DELTA = [(TOP_NUMS[0] - BOT_NUMS[0]) * 0.05, (TOP_NUMS[1] - BOT_NUMS[1]) * 0.05]

    if x_log:
        BOT_X = BOT_NUMS[0] / 2
        TOP_X = TOP_NUMS[0] * 2
    else:
        BOT_X = BOT_NUMS[0] - DELTA[0]
        TOP_X = TOP_NUMS[0] + DELTA[0]
        
    if y_log:
        BOT_Y = BOT_NUMS[1] / 2
        TOP_Y = TOP_NUMS[1] * 2
    else:
        BOT_Y = BOT_NUMS[1] - DELTA[1]
        TOP_Y = TOP_NUMS[1] + DELTA[1]
    
    if makesquare:
        TOP_Y = max(TOP_Y, TOP_X)
        TOP_X = max(TOP_Y, TOP_X)
        BOT_X = min(BOT_X, BOT_Y)
        BOT_Y = min(BOT_X, BOT_Y)
    
    if xyline:
        ax.plot([min([BOT_X, BOT_Y]), max([TOP_X, TOP_Y])],[min([BOT_X, BOT_Y]), max([TOP_X, TOP_Y])], c=xy_line_col)
    
    ax.set_xlim(BOT_X, TOP_X)
    #ax.set_xlim(BOT_NUMS[0], TOP_NUMS[0])
    ax.set_ylim(BOT_Y, TOP_Y)
    
    #pylab.xlabel("\\textbf{%s}" % x_label)
    #pylab.ylabel("\\textbf{%s}" % y_label)
    pylab.xlabel(x_label)
    pylab.ylabel(y_label)
    
    if names:
        if legend_name:
            pylab.legend(handles, names, loc="best", title=legend_name)
        else:
            pylab.legend(handles, names, loc="best")
    
    if graph_name:
        pylab.title(graph_name)
    
    if disable_x_tics:
        ax.xaxis.set_major_formatter( pylab.NullFormatter() )
        
    pylab.show()


def create_time_profile(times):
    x = sorted(times)
    y = [i+1 for i in range(len(times))]
    return (x,y)


if __name__ == '__main__':
    from krrt.utils import get_opts
    import os
    myargs, flags = get_opts()
    
    if '-csv' not in myargs:
        print "Error: Must include a path to the csv file:"
        print USAGE_STRING
        os._exit(1)
    
    title = None
    if '-title' in myargs:
        title = myargs['-title']
    
    xlabel = ""
    if '-xlabel' in myargs:
        xlabel = myargs['-xlabel']
    
    ylabel = ""
    if '-ylabel' in myargs:
        ylabel = myargs['-ylabel']
        
    legend = ""
    if '-legend' in myargs:
        legend = myargs['-legend']
    
    plot_from_file(myargs['-csv'], title, 'useheader' in flags, 'xlog' in flags, 'ylog' in flags, 'noxtics' in flags, 'noxy' in flags, 'noscatter' in flags, 'bw' in flags, 'multplots' in flags, xlabel, ylabel, legend, 'nosymbols' in flags)

