#!/usr/bin/python
import sys
import MySQLdb
import MySQLdb.cursors
import numpy
import random

class Splitter:

    eval_ids = set()
    feat_ids = set()
    mod_ids = set()

    #Class functions
    def __init__(self,getall):
        self.getall = getall
        #Set random seed
        #For repeatability from run to run (CRITICAL), use constant seed
        random.seed(0)

        #Get all id numbers from database into a set
        conn = MySQLdb.connect(host="localhost",user="guest",passwd="",db="Ravelry_Projects",cursorclass=MySQLdb.cursors.SSCursor)
        x = conn.cursor()
        x.execute("""SELECT id FROM patterns_full where days_since_pub < 4000""")
        all_ids = [ele[0] for ele in x.fetchall()]

        #Use cool random sample function to produce a random sample
        self.eval_ids = random.sample(tuple(set(all_ids)),5000)
        rem_ids = set(all_ids).difference(set(self.eval_ids))
        self.feat_ids = random.sample(tuple(rem_ids),10000)
        self.mod_ids = rem_ids.difference(self.feat_ids)

        #########################################3

    def fillSample(self,s_ids):
        #Query database again to build numpy array from that data
        #I am assuming this is faster than loading all 35000 points into
        #memory, but I could be wrong
        #Note that the final answer (nprojects) is part of the array, 
        #in the first slot
        #Note that the initialization parameter dictates how much information to extract
        feature_list = ""
        if self.getall: feature_list = "id,nprojects,days_since_pub,craft,diff_avg,diff_count,favs_count,free,category,des_npatts,des_favs,nsources,rate_avg,rate_count,yardage,yarn_weight,downloadable,sti_gauge,row_gauge,nproj_class"
        else: feature_list = "id,nprojects,days_since_pub"

        conn = MySQLdb.connect(host="localhost",user="guest",passwd="",db="Ravelry_Projects",cursorclass=MySQLdb.cursors.SSCursor)
        x = conn.cursor()

        holder = []
        for num in s_ids:
            x.execute("SELECT "+feature_list+" FROM patterns_full WHERE id="+str(num))
            data = x.fetchall()
            holder.append(list(data[0]))

        return(numpy.array(holder))

    def getEvalSample(self):
        return self.fillSample(self.eval_ids)

    def getFeatureSample(self):
        return self.fillSample(self.feat_ids)

    def getModelSample(self):
        return self.fillSample(self.mod_ids)
