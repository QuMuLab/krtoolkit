import simple

def create_view(title, type='simple'):
    if 'simple' == type:
        return simple.View(title)
    else:
        print "Error: Unrecognized view type, %s" % type
        return None