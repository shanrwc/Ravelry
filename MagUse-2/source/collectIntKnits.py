#!/usr/bin/python
import sys, urllib2, json, base64, MySQLdb
import calendar
import time
from datetime import date

def findCategories(d,labels):
    for k, v in d.iteritems():
        if k == 'name': labels.append(v)
        if isinstance(v,dict):
            labels = findCategories(v,labels)
    return labels

def calcPubDate(title):
    month=0
    year = int(title[-4:])
    if 'winter' in title:
        year -= 1
        month = 11
    if 'spring' in title: month = 2
    if 'summer' in title: month = 5
    if 'fall' in title: month = 8
    cal = calendar.monthcalendar(year,month)
    day = 0
    count = 0
    for week in cal:
        if week[0] != 0: count += 1
        if count == 3: day = week[0]
    return date(year,month,day)

############################################################

if len(sys.argv) < 4:
    print "Usage: collectData.py <Access Key> <Personal Key> <pattern source> . . ."
    print "The pattern source is a magazine or book title, in Ravelry-recognized format."
    print "More than one pattern source can be listed."
    sys.exit
else:

    access = sys.argv[1]
    personal = sys.argv[2]
    books = sys.argv[3:]

    #First, set up your database connection
    conn = MySQLdb.connect(host="localhost",user="guest",passwd="",db="Ravelry_Projects")
    x = conn.cursor()

    for book in books:
        print "Collecting data from ", book

        #Remove database entries for this pattern source
        x.execute("""DELETE from magazines where issue = %s""",book)

        #Variables to fill
        nProjects = 0
        nPatterns = 0
        nTorso = 0
        nFeet = 0
        nHead = 0
        nHand = 0
        nNeck = 0
        nOther = 0
        nFree = 0
        avgNSources = 0
        daysSincePub = 0
        avgFavorites = 0
        avgDifficulty = 0
        avgDesignFavs = 0
        avgDesignPatts = 0

        #import raw JSON data from the Ravelry API
        request = urllib2.Request("https://api.ravelry.com/pattern_sources/"+book+"/patterns.json")
        base64string = base64.encodestring('%s:%s' % (access,personal)).replace('\n','')
        request.add_header("Authorization","Basic %s" % base64string)
        response = urllib2.urlopen(request)
        bookdata = json.load(response)

        #Start filling in values
        nPatterns = bookdata['paginator']['results']

        #Loop over all patterns
        count = 0
        for pattern in bookdata['patterns']: 
#            if count > 0: break
            id = pattern['id']
            print "Accessing ", pattern['name']
            request2 = urllib2.Request("https://api.ravelry.com/patterns/"+str(id)+".json")
            request2.add_header("Authorization","Basic %s" % base64string)
            response2 = urllib2.urlopen(request2)
            pattdata = json.load(response2)

            if pattdata['pattern']['free']: nFree += 1
            avgNSources += len(pattdata['pattern']['printings'])
            for ele in pattdata['pattern']['printings']:
                if 'Free' in ele['pattern_source']['name'].encode('utf-8') and pattdata['pattern']['free'] == False: nFree += 1
            avgFavorites += pattdata['pattern']['favorites_count']
            avgDifficulty += pattdata['pattern']['difficulty_average']
            nProjects += pattdata['pattern']['projects_count']
            avgDesignFavs += pattdata['pattern']['pattern_author']['favorites_count']
            avgDesignPatts += pattdata['pattern']['pattern_author']['patterns_count']
            category = pattdata['pattern']['pattern_categories'][0]
            bits = []
            labels = findCategories(category,bits)
            if 'Sweater' in labels or 'Tops' in labels or 'Vest' in labels or 'Shrug / Bolero' in labels or 'Dress' in labels or 'Coat / Jacket' in labels:
                nTorso += 1
            elif 'Hands' in labels:
                nHand += 1
            elif 'Hat' in labels or 'Other Headwear' in labels:
                nHead += 1
            elif 'Feet / Legs' in labels:
                nFeet += 1
            elif 'Neck / Torso' in labels:
                nNeck += 1
            else: 
                nOther += 1
            
            count += 1
        avgNSources = avgNSources/float(nPatterns)
        avgDifficulty = avgDifficulty/float(nPatterns)
        avgFavorites = avgFavorites/float(nPatterns)
        avgDesignFavs = avgDesignFavs/float(nPatterns)
        avgDesignPatts = avgDesignPatts/float(nPatterns)
        daysSincePub = abs(date.today()-calcPubDate(book)).days

#        print "nPatterns =", nPatterns
#        print "nTorso = ", nTorso
#        print "nFeet = ", nFeet
#        print "nHead = ", nHead
#        print "nHand = ", nHand
#        print "nNeck = ", nNeck
#        print "nOther = ", nOther
#        print "nFree = ",nFree
#        print "avgNSources = ",avgNSources
#        print "avgFavorites = ", avgFavorites
#        print "avgDifficulty = ", avgDifficulty
#        print "nProjects = ", nProjects
#        print "daysSincePub = ", daysSincePub

        x.execute("""INSERT INTO magazines VALUES (NULL,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",(book,str(nProjects),str(nPatterns),str(nTorso),str(nFeet),str(nHead),str(nHand),str(nNeck),str(nOther),str(nFree),str(avgNSources),str(avgFavorites),str(avgDifficulty),str(avgDesignFavs),str(avgDesignPatts),str(daysSincePub)))
        conn.commit()
        print "Saved to database\n"


    conn.close()
