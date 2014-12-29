import sys
import urllib2
import json
import base64
import os
import os.path
import fileinput

from source.ravelryApi import *

#################################################
#################################################
#################################################

# This class handles assigning difficulty to a pattern based on
# a user's stored preferences

class Ranker:
    def __init__(self,name):
        self.username = name
    
    tagDiffs = {}
    typeDiffs = {}

##############################################################################

#load stored dictionaries
    def loadDicts(self,label):
        file1name = "data/tagDifficulties_"+label+".txt"
        infile1 = open(file1name,"r")
        lines = infile1.readlines()
        for line in lines:
            pieces = line.split(":")
            bits = (pieces[1].rstrip('\n')).split("-")
            self.tagDiffs.update({pieces[0]:bits})

        file2name = "data/typeDifficulties_"+label+".txt"
        infile2 = open(file2name,"r")
        lines = infile2.readlines()
        for line in lines:
            pieces = line.split(":")
            bits = (pieces[1].rstrip('\n')).split("-")
            self.typeDiffs.update({pieces[0]:bits})

        if label == "DEFAULT":
            out1name = "data/tagDifficulties_"+self.username+".txt"
            out1 = open(out1name,"w")
            for entry in self.tagDiffs:
                snippet = entry+":"
                for bit in self.tagDiffs[entry]:
                    snippet +=bit+"-"
                out1.write(snippet[:-1])
            out1.close()

            out2name = "data/typeDifficulties_"+self.username+".txt"
            out2 = open(out2name,"w")
            for entry in self.typeDiffs:
                snippet = entry+":"
                for bit in self.typeDiffs[entry]:
                    snippet += bit+"-"
                out2.write(snippet[:-1])
            out2.close()

###############################################################################

#classify a pattern
    def classifyPattern(self,pattNum):
        response = queryRavelry("https://api.ravelry.com/patterns/"+pattNum+".json")
        pattData = json.load(response)
#        print (pattData['pattern'])['name']
        tags = (pattData['pattern'])['pattern_attributes']
#        for entry in tags:
#            print entry['permalink']
        types = (pattData['pattern'])['pattern_categories'][0]
        cands = []
        while types['name'] != 'Categories':
            cands.append(types['name'])
            types = types['parent']
#        print cands
        label = ""
        if len(cands) > 2: label = cands[-3]
        else: label = cands[0]
#        print label
        if label == 'Other': label = label +"-"+cands[1]

        #Note: used entire labelling tree in cands, to give user access to all levels, for difficult ranking only
        #Assign difficulty if one is associated with type (if type can't be found, add it to dictionary with difficulty 2)
        keepLoop = True
        diff = "0"
        for level in self.typeDiffs:
            while keepLoop:
                for temp in cands:
                    if temp in self.typeDiffs[level] and level > diff:
                        diff = level
                        keepLoop = False
                        break
                keepLoop = False

        #Assign difficulty if one is associated with a tag (take highest possible difficulty of tags); if no tag listed, give difficulty 1
        keepLoop = True
        for level in self.tagDiffs:
            while keepLoop:
                for tag in tags:
                    if tag in self.tagDiffs[level] and level > diff:
                        if int(diff) > int(level): diff = level
                        keepLoop = False
                        break
                keepLoop = False
        
        snippet = label+":"+diff
        return(snippet)

###############################################################################

    #update tag rankings;includes saving to file
    def updateTags(self,tag, diff):
        if (diff < 1 or diff > 3): return 101
        self.tagDiffs[str(diff)].append(tag)
        self.saveToFile("Tag")
        return(100)

##############################################################################

    #update project type rankings; includes saving to file
    def updateTypes(self,typ,diff):
        if (diff < 1 or diff > 3): return 102
        self.typeDiffs[str(diff)].append(typ)
        self.saveToFile("Type")
        return(100)

###############################################################################

    #save dictionaries to file
    def saveToFile(self,label):
        if label == "Tag":
            out1name = "data/tagDifficulties_"+self.username+".txt"
            out1 = open(out1name,"w")
            for entry in self.tagDiffs:
                snippet = entry+":"
                for bit in self.tagDiffs[entry]:
                    snippet +=bit+"-"
                out1.write(snippet[:-1]+"\n")
            out1.close()
        elif label == "Type":
            out2name = "data/typeDifficulties_"+self.username+".txt"
            out2 = open(out2name,"w")
            for entry in self.typeDiffs:
                snippet = entry+":"
                for bit in self.typeDiffs[entry]:
                    snippet += bit+"-"
                out2.write(snippet[:-1]+"\n")
            out2.close()
        return(100)
