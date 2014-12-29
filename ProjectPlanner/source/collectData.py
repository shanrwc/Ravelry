import sys, urllib2, json, base64

#Books to analyze

if len(sys.argv) < 4:
    print "Usage: collectData.py <Access Key> <Personal Key> <book title> . . ."
    sys.exit
else:

    access = sys.argv[1]
    personal = sys.argv[2]
    books = sys.argv[3:]

    for book in books:
        print "Collecting data from . . ."
        print book
#import raw JSON data from the Ravelry API
        request = urllib2.Request("https://api.ravelry.com/pattern_sources/"+book+"/patterns.json")
        base64string = base64.encodestring('%s:%s' % (access,personal)).replace('\n','')
        request.add_header("Authorization","Basic %s" % base64string)
        response = urllib2.urlopen(request)
        bookdata = json.load(response)

#Get total number of patterns and pattern ID numbers
        nPatterns = (bookdata['paginator'])['results']
        patternIDs = []
        for pattern in bookdata['patterns']:
            patternIDs.append(pattern['id'])

#Now make a list of users that have made these pattern
        pagesize = 1000
        nProjects = 0
        user_counts = {}
        for pattern in patternIDs:
            print "on pattern . . ."
            print pattern
            #Query once to figure out how many queries are needed
            request2 = urllib2.Request("https://api.ravelry.com/patterns/"+str(pattern)+"/projects.json?page=1&page_size=10&photoless=1")
            request2.add_header("Authorization","Basic %s" % base64string)
            response2 = urllib2.urlopen(request2)
            projdata = json.load(response2)
            projs = (projdata["paginator"])["results"]
            totalpages = int(projs/pagesize)+1
            if totalpages > 10: totalpages = 10
            nProjects += projs
            for nPage in range(1,totalpages+1):
                request3 = urllib2.Request("https://api.ravelry.com/patterns/"+str(pattern)+"/projects.json?page="+str(nPage)+"&page_size="+str(pagesize)+"&photoless=1")
                request3.add_header("Authorization","Basic %s" % base64string)
                response3 = urllib2.urlopen(request3)
                projdata = json.load(response3)
                for project in projdata["projects"]:
                    userID = project["user_id"]
                    if userID in user_counts.keys():
                        (user_counts[userID])[0] += 1
                        (user_counts[userID])[1] += "-"+str(pattern)
                    else:
                        user_counts[userID] = [1,str(pattern)]
        print len(user_counts)
        print nProjects

#Now write data to file
        outfilename = book + "_RAW.txt"
        outfile = open(outfilename,"w")
        snippet = "NPATTERNS: "+str(nPatterns)+"\n"
        outfile.write(snippet)
        snippet = "NPROJECTS: "+str(nProjects)+"\n"
        outfile.write(snippet)
        snippet = "NUSERS: "+str(len(user_counts))+"\n"
        outfile.write(snippet)
        for user in user_counts.keys():
            snippet = "COUNT: "+str(user)+" "+str((user_counts[user])[0])+" "+(user_counts[user])[1]+"\n"
            outfile.write(snippet)
        outfile.close()
