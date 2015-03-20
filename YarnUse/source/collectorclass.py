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

###########################################################

def resetData(self,name,number):
    self.pattname = name
    self.pattnumb = number
    data.clear()

def saveData(self):
    print ("Function needs to be written!")
