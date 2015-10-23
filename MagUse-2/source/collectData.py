#!/usr/bin/python
import sys, urllib2, json, base64, MySQLdb

#Books to analyze

if len(sys.argv) < 5:
    print "Usage: collectData.py <Access Key> <Personal Key> <DB password> <pattern source> . . ."
    print "The pattern source is a magazine or book title, in Ravelry-recognized format."
    print "You can list more than one, but it isn't recommended; the macro will run"
    print " veeeeeeeeeeery sloooooooowly in that case."
    sys.exit
else:

    access = sys.argv[1]
    personal = sys.argv[2]
    dbpass = sys.argv[3]
    books = sys.argv[4:]

    #First, set up your database connection
    conn = MySQLdb.connect(host="localhost",user="root",passwd=dbpass,db="Ravelry_Projects")
    x = conn.cursor()

    for book in books:
        print "Collecting data from . . ."
        print book
        #Remove database entries for this pattern source
        x.execute("""DELETE from projects where source = %s""",book)
        x.execute("""DELETE from patterns where source = %s""",book)
#import raw JSON data from the Ravelry API
        request = urllib2.Request("https://api.ravelry.com/pattern_sources/"+book+"/patterns.json")
        base64string = base64.encodestring('%s:%s' % (access,personal)).replace('\n','')
        request.add_header("Authorization","Basic %s" % base64string)
        response = urllib2.urlopen(request)
        bookdata = json.load(response)

#Get total number of patterns and pattern ID numbers
        nPatterns = (bookdata['paginator'])['results']
        patternIDs = []
        patt_names = []
        for pattern in bookdata['patterns']:
            patternIDs.append(pattern['id'])
#            print pattern['name']
            temp = (pattern['name']).encode('ascii','ignore')
            x.execute("""INSERT INTO patterns VALUES (%s,%s,%s)""",(str(pattern['id']),book,temp))

#Now make a list of users that have made these pattern
        pagesize = 1000
        for pattern in patternIDs:
 #           if pattern != 10669: continue
            print "on pattern . . ."
            print pattern
            #Query once to figure out how many queries are needed
            request2 = urllib2.Request("https://api.ravelry.com/patterns/"+str(pattern)+"/projects.json?page=1&page_size=10&photoless=1")
            request2.add_header("Authorization","Basic %s" % base64string)
            response2 = urllib2.urlopen(request2)
            projdata = json.load(response2)
            projs = (projdata["paginator"])["results"]
            totalpages = int(projs/pagesize)+1
            #queries for more than 10000 results will fail--cap results at that limit
            if totalpages > 10: totalpages = 10
            for nPage in range(1,totalpages+1):
                request3 = urllib2.Request("https://api.ravelry.com/patterns/"+str(pattern)+"/projects.json?page="+str(nPage)+"&page_size="+str(pagesize)+"&photoless=1")
                request3.add_header("Authorization","Basic %s" % base64string)
                response3 = urllib2.urlopen(request3)
                projdata = json.load(response3)
                for project in projdata["projects"]:
                    userID = project["user_id"]
                    date = project["started"]
                    #Now write this information to the database
#                    print str(userID)+" "+str(project['id'])+" "+book+" "+str(date)+" "+str(pattern)
                    x.execute("""INSERT INTO projects VALUES (%s,%s,%s,%s,%s)""",(str(project['id']),str(userID),book,str(pattern),date))
                    conn.commit()


#Now write data to database

conn.close()
