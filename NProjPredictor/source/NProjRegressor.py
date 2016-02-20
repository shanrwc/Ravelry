#!/usr/bin/python
import sys
import itertools
import collections
import numpy
import MySQLdb
import MySQLdb.cursors

from Splitter import Splitter
from prettyPlotCode import *

#sklearn imports go here
from sklearn.preprocessing import MinMaxScaler
from sklearn.neighbors import KNeighborsRegressor

from sklearn.grid_search import GridSearchCV
from sklearn.cross_validation import KFold
from sklearn.metrics import classification_report,confusion_matrix

###################################################################### 
###                         Code goes here                         ###
######################################################################

#Get your data
mysplitter = Splitter(True)
feature_list = "days_since_pub,craft,diff_avg,favs_count,free,category,des_favs,nsources,rate_avg,yarn_weight,downloadable,sti_gauge,nproj_class,ntags,ncomments" 
features = mysplitter.getModelSample(feature_list)
nprojects = mysplitter.getModelSample("nprojects")

#Rescale everything, because the kNN and SVM will need it
min_max_scaler = MinMaxScaler()
sfeatures = min_max_scaler.fit_transform(features)

#Build my regressors
#Print stats of those regressors

#kNN
clf1 = GridSearchCV(KNeighborsRegressor(),param_grid={'n_neighbors':[5,10,15,20],'weights':['uniform','distance']},cv=KFold(len(sfeatures),5),scoring='mean_squared_error')
clf1.fit(sfeatures,nprojects)
print "k-Nearest Neighbor"
print "kFold Scores: ",clf1.grid_scores_
print "Best Score: ",clf1.best_score_
print "Final Score: ",clf1.score(sfeatures,nprojects)
print

#SVM

#RandomForest

#Evaluate regressors on eval data
