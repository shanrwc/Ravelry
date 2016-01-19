#!/usr/bin/python
import sys
import numpy
import matplotlib.pyplot as plt
import itertools
from prettyPlotCode import *
from Splitter import Splitter

#############################################################################
##                        The Real Code                                    ##
#############################################################################

#Load in modeling data
#The false argument is because I don't need the full pattern information
mysplitter = Splitter(False)
mdata = mysplitter.getModelSample()
days = mdata[:,[2]].reshape(20000)
nprojs = mdata[:,[1]].reshape(20000)
print mdata[0]
print days[0]
print nprojs[0]

#Slap a straight line on that data
b1,b2 = numpy.polyfit(days,nprojs,1)
print b1,b2

#Make a pretty plot
makeScatterPlot(days,"Days_Since_Publication",nprojs,"Number_of_Projects","_linearfit",b2,b1)

#Use line on eval data
edata = mysplitter.getEvalSample()
edays = edata[:,[2]].reshape(5000)
enprojs = edata[:,[1]].reshape(5000)
preds = [b2*d+b1 for d in edays]

#Make a residual plot for eval (or for both?)
#Yea, both
res_mod = itertools.starmap(lambda alpha,beta: alpha-(b2*beta+b1), zip(nprojs,days))
makeScatterPlot(days,"Days_Since_Publication",res_mod,"Fit_Residuals","_fitres")
res_eval = itertools.starmap(lambda delta,gamma: delta-gamma,zip(enprojs,preds))
makeScatterPlot(edays,"Days_Since_Publication",res_eval,"Eval_Residuals","_evalres")

#Calculate R^2 score (or other score used for comparison)
print calculateRSquared(enprojs,preds)
