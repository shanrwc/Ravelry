import sys
import urllib2
import json
import base64
import os
import os.path
import fileinput

from source.ravelryApi import *

###########################################################################
###########################################################################
###########################################################################

# Get pattern name from user.  Query Ravelry for patterns with that name.
#print("Welcome to the Yarn Use Calculator.")
#print ("This program calculates statistics about the amounts of yarn used for knitting and crochet patterns.")
#name = str(raw_input("To start, please enter a pattern's name: "))
#print ("Looking for pattern "+name)

#convert name to something Ravelry will understand
#pieces = (name.lower()).split()
#ravname = ""
#for bit in pieces:
#    ravname = ravname + bit + "-"
#ravname = ravname[:-1]
#print ravname

response = queryRavelry("https://api.ravelry.com/patterns/search.json?query=shetland-border-shawl")
pattList = json.load(response)
#print pattList["patterns"][0]["id"]

#If only one pattern was found, proceed with it.  Otherwise, cancel (for now).
pattNumber = ""
if pattList["paginator"]["results"] == 1:
    pattNumber = pattList["patterns"][0]["id"]
    print pattNumber
else:
    print ("Your selected pattern is not a name found in the database.")
    print ("Good-bye")
    sys.exit()


#Get completed projects associated wth pattern number/give pattern number to class to do this
