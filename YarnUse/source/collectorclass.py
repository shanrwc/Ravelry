import sys
import urllib2
import json
import base64
import os
import os.path
import fileinput

from source.ravelryApi import *

#########################################################
#########################################################
#########################################################

#This class collects data on yarn use from completed projects
#associated to a given pattern

class Collector:
    def __init__(self,name,number):
        self.pattname = name
        self.pattnum = number

    data = []
    nomWeight = ""
    nomYardage = ""

###########################################################

    def resetData(self,name,number):
        self.pattname = name
        self.pattnumb = number
        data.clear()
        nomWeight = ""
        nomYardage = ""

    def saveData(self, maxi, mini):
        filename = "data/"+self.pattname + "_yarnusage.txt"
        outfile = open(filename,"write")
        outfile.write("NAME: "+self.pattname+"\n")
        outfile.write("WEIGHT: "+self.nomWeight+"\n")
        outfile.write("YARDAGE: "+str(self.nomYardage)+"\n")
        outfile.write("MAXIMUM: "+str(maxi)+"\n")
        outfile.write("MINIMUM: "+str(mini)+"\n")
        for entry in self.data:
            snippet = "ENTRY: "+str(entry[0])+"  "+str(entry[1])+"\n"
            outfile.write(snippet)
        outfile.close()

    def compareWeights(self,weight1,weight2):
        val1 = self.convertWeight(weight1)
        val2 = self.convertWeight(weight2)
        diff = abs(val1-val2)
        wgt = 1
        if diff < 2: wgt = 1.0
        elif diff < 3: wgt = 0.8
        elif diff < 4: wgt = 0.6
        elif diff < 5: wgt = 0.4
        else: wgt = 0.1
        return(wgt)

    def convertWeight(self,weight):
        value = 0
        if weight == "Thread": value = 1
        elif weight == "Cobweb": value = 2
        elif weight == "Lace": value=3
        elif weight == "Light Fingering": value=4
        elif weight == "Fingering": value=5
        elif weight == "Sport": value=6
        elif weight == "DK": value=7
        elif weight == "Worsted": value=8
        elif weight == "Aran": value = 9
        elif weight == "Bulky": value = 10
        elif weight == "Super Bulky": value = 11
        else:
            print "Weight unknown!"
            print weight
        return(value)


############################################################

#This is the central function of this class.
#It fills the data list with pairs of amount of yardage used and weight
    def getProjectData(self):
        #Grab yarn weight expected for pattern
        response0 = queryRavelry("https://api.ravelry.com/patterns/"+str(self.pattnum)+".json")
        pattData = json.load(response0)
#        print pattData
        pattWeight = pattData["pattern"]["yarn_weight"]["name"]
        self.nomWeight = pattWeight
        self.nomYardage = pattData["pattern"]["yardage"]
        #Query once to figure out total number of projects available
        response = queryRavelry("https://api.ravelry.com/patterns/"+str(self.pattnum)+"/projects.json?page=1&page_size=10&photoless=1")
        pagedata = json.load(response)
        totalProjs = (pagedata["paginator"])["results"]
        totalpages = int(totalProjs/1000)+1
        if totalpages > 10: totalpages = 10
        inc = 100/totalpages
        maxi = 0
        mini = 10000
        for nPage in range(1,totalpages+1):
            response2 = queryRavelry("https://api.ravelry.com/patterns/"+str(self.pattnum)+"/projects.json?page="+str(nPage)+"&page_size=1000&photoless=1")
            projInfo = json.load(response2)
            projList = projInfo["projects"]
            for proj in projList:
                #if project does not have the completed_day_set bool set to true and has an incomplete project status, skip it
                if proj["status_name"] != "Finished" and proj["progress"] != 100 and proj["project_status_id"] != 2: continue
                else:
                    #Otherwise,query again to get full project details (since the list from the pattern seems to be a small version).
                    user = proj["user"]["username"]
                    projId = proj["id"]
                    response3 = queryRavelry("https://api.ravelry.com/projects/"+user+"/"+str(projId)+".json")
                    #Add "?include=comments in the above query to get the comments as well
                    yarnInfo = (json.load(response3))["project"]["packs"]
                    if len(yarnInfo) < 1: continue
#                    print yarnInfo
                    if yarnInfo[0]["total_meters"] is None: continue
                    if yarnInfo[0]["yarn_weight"] is None: continue
                    yarnUsed = yarnInfo[0]["total_meters"]
                    yarnWeight = yarnInfo[0]["yarn_weight"]["name"]
#                    snippet = str(user)+" "+str(yarnUsed)+" "+str(yarnWeight)
#                    print snippet
                    #comments = (json.load(response3))["comments"]

                    if yarnUsed > maxi: maxi = yarnUsed
                    if yarnUsed < mini: mini = yarnUsed
                    weight = 1.0
                    weight = weight*self.compareWeights(pattWeight,yarnWeight)
                    self.data.append([yarnUsed,weight])
            snippet = str(nPage*inc) + "% of projects analyzed"
            print snippet
        self.saveData(maxi,mini)
