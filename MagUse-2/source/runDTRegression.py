#!/usr/bin/python
import matplotlib.pyplot as plt
import sys
import MySQLdb
import MySQLdb.cursors
import numpy
from prettyPlotCode import *

#more sklearn imports will go here
from sklearn import datasets
from sklearn.cross_validation import train_test_split
from sklearn.grid_search import GridSearchCV
from sklearn.ensemble.forest import RandomForestRegressor

#############################################################################
##                        The Real Code                                    ##
#############################################################################

##Load data into arrays or dictionaries; separate out your final set of test data here
conn = MySQLdb.connect(host="localhost",user="guest",passwd="",db="Ravelry_Projects",cursorclass=MySQLdb.cursors.DictCursor)
x = conn.cursor()
x.execute("SELECT issue,patterns,projects,p_torso,p_feet,p_head,p_hand,p_neck,p_other,p_free,avg_sources,avg_favorites,avg_difficulty,designer_favs,designer_patts,days_since_pub FROM magazines WHERE issue LIKE '%200%' OR issue LIKE '%2010%' OR issue LIKE '%2011%' OR issue LIKE '%2012%' OR issue LIKE '%2013%'")
tt_data = x.fetchall()

x.execute("SELECT issue,patterns,projects,p_torso,p_feet,p_head,p_hand,p_neck,p_other,p_free,avg_sources,avg_favorites,avg_difficulty,designer_favs,designer_patts,days_since_pub FROM magazines WHERE issue LIKE '%2014%' OR issue LIKE '%2015%'")
final_data = x.fetchall()

#Separate features from dependent variable(s)
tt_features,tt_labels = separateFeatures(tt_data)
final_features,final_labels = separateFeatures(final_data)

###########################################################################

##Make scatter plots or histograms
feature_labels = ["patterns","p_torso","p_feet","p_head","p_hand","p_neck","p_other","p_free","avg_sources","avg_favorites","avg_difficulty","designer_favs","designer_patts","days_since_pub"]

for tag in feature_labels:
    xs = convertToList(tt_data,tag)
    makeScatterPlot(xs,tag,tt_labels,"Projects Per Day")

##Rescale any data that needs it, or PCA if you feel like it
tt_data = rescaleFeatures(tt_data,["avg_favorites","designer_favs","designer_patts"])
final_data = rescaleFeatures(final_data,["avg_favorites","designer_favs","designer_patts"])
tt_features,tt_labels = separateFeatures(tt_data)
final_features,final_labels = separateFeatures(final_data)

##And some more scatter plots
feature_labels = ["avg_favorites","designer_favs","designer_patts"]
for tag in feature_labels:
    xs = convertToList(tt_data,tag)
    makeScatterPlot(xs,tag,tt_labels,"Projects Per Day","rescaled")

##Create/train your machine learning algorithm of choice
##Note that I'm letting sklearn's kfold cross-validation handle the
##split into training and testing data
params = [{'n_estimators':[10,50,100,500],'max_depth':[4,8,12],'min_samples_split':[2,6,10,14]}]

forest = RandomForestRegressor(random_state=42)
reg = GridSearchCV(forest,params,cv=4,scoring='mean_squared_error')
reg.fit(tt_features,tt_labels)

print "Best parameters are: "
print reg.best_params_

print "Grid scores on training/testing data:"
for params, mean_score, scores in reg.grid_scores_:
    print ("%s (+/-%s) for %r" % (str(mean_score),str(scores.std()),params))

for ele in reg.best_estimator_.feature_importances_:
    print ele

##Rerun your algorithm on final test set and compare metrics
tt_xs = convertToList(tt_data,"days_since_pub")
val_xs = convertToList(final_data,"days_since_pub")

tt_pred = reg.best_estimator_.predict(tt_features)
final_pred = reg.best_estimator_.predict(final_features)

#print len(tt_xs),len(tt_labels)
#for i in range(len(tt_xs)):
#    print tt_xs[i],tt_labels[i]
plt.scatter(tt_xs,tt_labels,color='b',label="2005-2013 data")
plt.plot(tt_xs,tt_pred,color='b',label="2005-2013 pred")
plt.scatter(val_xs,final_labels,color='r',label="2014-2015 data")
plt.plot(val_xs,final_pred,color='r',label="2014-2015 pred")
plt.xlabel("Days since Publication")
plt.ylabel("Projects per day")
plt.axis([0,4100,0,5.0])
plt.legend()
plt.show()


