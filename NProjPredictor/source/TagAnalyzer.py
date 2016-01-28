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
from sklearn.naive_bayes import GaussianNB
from sklearn.naive_bayes import MultinomialNB
from sklearn.naive_bayes import BernoulliNB
from sklearn.grid_search import GridSearchCV
from sklearn.cross_validation import KFold
from sklearn.metrics import classification_report,confusion_matrix

def getNProjClass(dummyn):
    if dummyn < 1: return(1)
#    elif dummyn < 1.0: return(2)
    else: return(3)

#########################################################################
##                           Code goes here                            ##
#########################################################################

train_size = 9000

#This code:
#1. grabs the subsample to use for feature development (after ids here)
mysplitter = Splitter(False)
fdata = mysplitter.getFeatureSample()
ids = fdata[:,[0]].reshape(10000)
nprojs = fdata[:,[1]].reshape(10000)
days = fdata[:,[2]].reshape(10000)

#2. Query database for attribute tags
conn = MySQLdb.connect(host="localhost",user="guest",passwd="",db="Ravelry_Projects",cursorclass=MySQLdb.cursors.SSCursor)
x = conn.cursor()

fholder = []
lholder = []
llholder = []
for i in ids:
    x.execute("SELECT nprojects,days_since_pub,patt_attribs FROM patterns_full WHERE id = "+str(i))
    entry = x.fetchall()[0]
    #3. Convert number of projects to a class label
    #4. Convert attribute tags to a list of features
    lholder.append(getNProjClass(entry[0]/float(entry[1])))
    temp = entry[2].split("-")
    fholder.append(temp)
    llholder.append(len(temp))

uniquefs = list(set([item for sub in fholder for item in sub]))
f2holder = []
for fs in fholder:
    temp = [0]*len(uniquefs)
    for ele in fs:
        temp[uniquefs.index(ele)] = 1
    f2holder.append(temp)

features = numpy.array(f2holder)
labels = numpy.array(lholder)
ntags = numpy.array(llholder)

#Pause to make some scatter plots
nnprojs = numpy.array([a/float(b) for a,b in itertools.izip(nprojs,days)])
makeHistogram(nnprojs,"Normalized_Number_Projects",[0,0.1,1.0,6.0],"_taganal")
makeScatterPlot(ntags,"Number_of_Tags",nprojs,"Number_of_Projects","_corrcheck")

#also, make a pretty bar chart comparing tags of high performers to everything else
#this requires reorganizing
#low_guys = collections.Counter()
#high_guys = collections.Counter()
#for i in range(len(lholder)):
#    if lholder[i] < 2: low_guys.update(fholder[i])
#    else: high_guys.update(fholder[i])

#print low_guys.most_common(10)
#print high_guys.most_common(10)
 
#5. Build classifiers linking tags to nprojs class
#5.5. Print out all the performance stats

clf = GridSearchCV(GaussianNB(),param_grid={},cv=KFold(train_size,9))
clf.fit(features[:train_size],labels[:train_size])
print "Gaussian Naive Bayes"
print "kFold Scores: ",clf.grid_scores_
print "Best Score: ",clf.best_score_
print "Final Score: ",clf.score(features[train_size:],labels[train_size:])
print "Confusion Matrix on training: "
print confusion_matrix(labels[:train_size],clf.predict(features[:train_size]))
print "Confusion Matrix on testing: "
print confusion_matrix(labels[train_size:],clf.predict(features[train_size:]))
print

clf2 = GridSearchCV(BernoulliNB(),param_grid={'alpha':[0.1,0.5,1.0]},cv=KFold(train_size,9))
clf2.fit(features[:train_size],labels[:train_size])
print "Bernoulli Naive Bayes"
print "kFold Scores: ",clf2.grid_scores_
print "Best Score: ", clf2.best_score_
print "Final Score: ", clf2.score(features[train_size:],labels[train_size:])
print

clf3 = GridSearchCV(MultinomialNB(),param_grid={'alpha':[0.1,0.5,1.0]},cv=KFold(train_size,9))
clf3.fit(features[:train_size],labels[:train_size])
test_preds = clf3.predict(features[train_size:])
print "Multinomial Naive Bayes"
print "kFold Scores: ",clf3.grid_scores_
print "Best Score: ", clf3.best_score_
print "Final Score: ", clf3.score(features[train_size:],labels[train_size:])
#print clf3.best_estimator_.feature_log_prob_
print "Confusion Matrix on training: "
print confusion_matrix(labels[:train_size],clf3.predict(features[:train_size]))
print "Confusion Matrix on testing: "
print confusion_matrix(labels[train_size:],test_preds)
#print "Classification Report: ", classification_report(labels[train_size:],test_preds)
print

#6. Assign class labels to everything in database (that needs them)
#mids = (mysplitter.getModelSample())[:,[0]].reshape(20000)
#for m in mids[:50]:
#    x.execute("SELECT patt_attribs FROM patterns_full WHERE id="+str(m))
#    entry = x.fetchall()[0]
#    taglist = entry[0].split("-")
#    temp = [0]*len(uniquefs)
#    for ele in taglist:
#        temp[uniquefs.index(ele)] = 1
#    pred = clf3.predict(numpy.array(temp).reshape(1,-1))
#    print pred
#    x.execute("UPDATE patterns_full SET 'ntags'="+str(len(taglist))+" 'nproj_class'="+str(pred[0])+" WHERE id="+str(m))

#eids = (mysplitter.getEvaluationSample())[:,[0]].reshape(5000)
