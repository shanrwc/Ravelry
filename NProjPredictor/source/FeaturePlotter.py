#!/usr/bin/python

import os
import sys
import numpy
import scipy.stats

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

labels = {"Days_Since_Publication":2,"Craft":3,"Average_Difficulty":4,"Difficulty_Count":5,"Favorites_Count":6,"Free":7,"Category":8,"NPatterns_by_Designer":9,"Designer_Favorites":10,"Number_Sources":11,"Average_Rating":12,"Rating_Count":13,"Yardage":14,"Yarn_Weight":15,"Downloadable":16,"Stitch_Gauge":17,"Row_Gauge":18,"Number_Tags":20,"Number_Comments":21}
 
file1 = open("dependent_correlations.txt","w")
file1.write("\\begin{tabular}{|l|c|c|}\n")
file1.write("\\hline\n")
file1.write("\\multicolumn{3}{|c|}{Correlation with Number of Projects}\\\\\n")
file1.write("Variable & Pearson's R & p-value \\\\\n")
file1.write("\\hline\n")

badguys = []

for ele in labels:
    temp = mdata[:,[labels[ele]]].reshape(20000)
    makeScatterPlot(temp,ele,nprojs,"Number_of_Projects","_corrcheck")
    r,p = scipy.stats.pearsonr(temp,nprojs)
    snippet = ele.replace("_"," ") + " & %.2f & %.2e" % (r,p) + " \\\\\n"
    file1.write(snippet)
    if abs(r) < 0.01 or abs(r) > 0.99: badguys.append(ele)
    
file1.write("\\hline\n")
file1.write("\\end{tabular}\n")
file1.close()
os.system("mv *Number_of_Projects*_corrcheck.png plots/dependent_correlation/.")

for bit in badguys:
    del labels[bit]

print badguys
print labels

del labels["Free"]
del labels["Downloadable"]

file2 = open("independent_correlations.txt","w")
file2.write("\\begin{tabular}{|l|"+"c|"*len(labels)+"}\n")
file2.write("\\hline\n")
file2.write("\\multicolumn{"+str(1+len(labels))+"}{|c|}{Correlation (p-value) amongst Variables}\\\\\n")
file2.write(" & ".join(labels.keys())+"\\\\\n")
file2.write("\\hline\n")

for ele1 in labels:
    snippet = ele1.replace("_"," ")
    for ele2 in labels:
        if ele1 != ele2:
            temp1 = mdata[:,[labels[ele1]]].reshape(20000)
            temp2 = mdata[:,[labels[ele2]]].reshape(20000)
            makeScatterPlot(temp1,ele1,temp2,ele2,"_corrcheck")
            r,p = scipy.stats.pearsonr(temp1,temp2)
            snippet += " & %.2f(%.2e)"% (r,p)
        else: snippet += " & 1.0(0.0)"
    snippet += " \\\\ \n"
    file2.write(snippet)

file2.write("\\hline\n")
file2.write("\\end{tabular}\n")
file2.close()
os.system("mv *_corrcheck.png plots/independent_correlation/.")
