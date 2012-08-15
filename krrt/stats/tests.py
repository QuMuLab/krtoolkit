##############################
##  Useful statistical tests
#############################

from random import choice
from time import time

from krrt.utils.experimentation import product
from krrt.utils import save_CSV

def anova(results, factors, dependent = None, cleanup = True):
    """
    Perform a mixed analysis of variance (ANOVA) between a number
    of degrees of freedom for a repeated experiment.
    
    results -- A list of experiment results with each item being a list
                of parameter settings or results. The first item in results
                is treated to be the headings (ie. parameter names)
    factors -- Name of the factors you want to consider in the ANOVA calc-
                ulation. They must correspond to items in the first element
                of the results list.
    dependent -- Name of the dependent variable. If missing, the last element
                  in the headers list is taken (default None)
    cleanup -- Boolean flag to decide whether or not to clean temp files (default True)
    """
    try:
        import rpy2.robjects as robjects
    except:
        print "Error: rpy2 not available. Advanced statistical testing will not work."
        return None
    
    dependent = dependent or results[0][-1]
    
    #--- Write a dummy file of the settings (without the header)
    filename = str(int(time())) + '-anova.in'
    save_CSV(results[1:], filename, delimiter="\t")
    
    #--- Run it through r
    command = "full=read.table(\"%s\")\n" % filename
    command += "names(full)<-c(" + ', '.join(["'%s'" % item for item in results[0]]) + ")\n"
    command += "attach(full)\n"
    for factor in factors:
        command += "%s = factor(%s)\n" % (factor, factor)
    command += "aov1<-aov(%s~%s)" % (dependent, '*'.join(factors))

    robjects.r(command)
    
    print robjects.r('aov1')
    summary = robjects.r('summary(aov1)').__str__()
    print summary
    
    results = [item.split()[0] for item in filter(lambda x: '*' in x[-3:] or '.' in x[-3:], summary.split("\n"))]

    for res in results:
        command = "tuk=TukeyHSD(aov1,which=\"%s\",conf.level=0.995)" % res
        robjects.r(command)
        print robjects.r('tuk')
    
    #--- Remove the file
    if cleanup:
        import os
        os.remove(filename)

def randomized_pairwise_t_test(arr1, arr2, output=True):
    """
    Perform a randomized pairwise t-test on two arrays
    of values of equal size.
    
      see Cohen, P.R., Empirical Methods for Artificial Intelligence, p. 168
    """

    # Make sure both arrays are the same length
    assert len(arr1) == len(arr2)
    
    # Cast them to floats
    arr1 = map(float, arr1)
    arr2 = map(float, arr2)

    # Calculate the absolute diffs
    diffs = [(arr1[i] - arr2[i]) for i in range(len(arr1))]
    
    # Calculate the original mean
    originalMean = sum(diffs) / float(len(diffs))
    numLess = 0
    
    # Do 10000 trials to test
    for i in range(10000):
        running_sum = 0.
        for j in range(len(diffs)):
            if choice([True,False]):
                running_sum += diffs[j]
            else:
                running_sum -= diffs[j]
        
        mean = running_sum / float(len(diffs))
        
        if mean <= originalMean:
            numLess += 1
    
    # Finally output / return the stats
    ratio = float(numLess + 1) / float(10001)
    ratio = min(ratio, 1-ratio)
    if output:
        print "mean difference: %f\nsignificant at p <= %f" % (originalMean, ratio)
    
    return originalMean, ratio
    