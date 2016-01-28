#!/usr/bin/python

import sys
import numpy

from Splitter import Splitter
from prettyPlotCode import *

#########################################################################
##                           Code goes here                            ##
#########################################################################

## The point of this script to make many, many scatter plots examining
##potential features and checking for correlations.  
## So get the modeling sample, and start looping

mysplitter = Splitter(True)
mdata = mysplitter.getModelSample()
nprojs = mdata[:,[1]].reshape(20000)
print len(nprojs)

labels = {"Days_Since_Publication":2,"Craft":3,"Average_Difficulty":4,"Difficulty_Count":5,"Favorites_Count":6,"Free":7,"Category":8,"NPatterns_by_Designer":9,"Designer_Favorites":10,"Number_Sources":11,"Average_Rating":12,"Rating_Count":13,"Yardage":14,"Yarn_Weight":15,"Downloadable":16,"Stitch_Gauge":17,"Row_Gauge":18}

for ele in labels:
    makeScatterPlot(mdata[:,[labels[ele]]].reshape(20000),ele,nprojs,"Number_of_Projects","_corrcheck")

labels2 = [[("Difficulty_Count",5),("Rating_Count",13)]]

for ele in labels2:
    makeScatterPlot(mdata[:,[ele[0][1]]].reshape(20000),ele[0][0],mdata[:,[ele[1][1]]].reshape(20000),ele[1][0],"_corrcheck")
