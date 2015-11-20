#!/usr/bin/python
import matplotlib.pyplot as plt
import sys
import MySQLdb
import MySQLdb.cursors
import numpy

############################################################################
##                      Helpful Functions                                 ##
############################################################################

def convertToList(tion,label):
    arr = []
    for ele in tion:
        for k in ele.keys():
            if k == label: arr.append(ele[k])
    return arr

def rescaleFeatures(bict,labs):
    #This could be done with sklearn's minmaxscaler, but I can preserve my 
    #data formatting by doing it myself
    for name in labs:
        subset = convertToList(bict,name)
        mi = min(subset)
        ma = max(subset)
        for ele in bict:
            for k in ele.keys():
                if k == name: ele[k] = (ele[k]-mi)/(ma-mi)
    return bict        

def separateFeatures(book):
    features = []
    labels = []

    for ele in book:
#        features.append((ele["patterns"],ele["p_torso"],ele["p_feet"],ele["p_head"],ele["p_hand"],ele["p_other"],ele["p_free"],ele["avg_sources"],ele["avg_favorites"],ele["avg_difficulty"],ele["designer_favs"],ele["designer_patts"]))
        features.append((ele["avg_favorites"],ele["p_feet"],ele["designer_favs"],ele["p_other"],ele["avg_difficulty"],ele["p_head"]))
        labels.append(ele["projects"]/float(ele["days_since_pub"]))

    return features,labels

############################################################################
##                      Plotting Functions                                ##
############################################################################

def makeScatterPlot(xs,xlabel,ys,ylabel,otherlabel = ""):
    plt.scatter(xs,ys)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
#    plt.show()
    plotname = xlabel+"_v_"+ylabel
    if len(otherlabel) > 0: plotname += otherlabel
    plt.savefig(plotname)
    plt.clf()

