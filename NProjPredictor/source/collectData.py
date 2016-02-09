#!/usr/bin/python
import sys, urllib2, json, base64, MySQLdb
from datetime import datetime
import random

def findCategories(d,labels):
    for k,v in d.iteritems():
        if k == 'name':labels.append(v)
        if isinstance(v,dict):
            labels = findCategories(v,labels)
    return labels

def getCategoryCode(catlist):
    bits = []
    labels = findCategories(catlist,bits)
    if 'Sweater' in labels or 'Tops' in labels or 'Vest' in labels or 'Shrug / Bolero' in labels or 'Dress' in labels or 'Coat / Jacket' in labels:
        return(0)
    elif 'Hands' in labels:
        return(1)
    elif 'Hat' in labels or 'Other Headwear' in labels:
        return(2)
    elif 'Feet / Legs' in labels:
        return(3)
    elif 'Neck / Torso' in labels:
        return(4)
    else: 
        return(5)

def collectAttribs(attlist):
    allatts = []
    for ele in attlist:
        allatts.append(ele['id'])
    return "-".join(list(map(str,allatts)))

################################################################

if len(sys.argv) != 4:
    print "Usage: collectData.py <Access Key> <Personal Key> <max number of patterns>"
    sys.exit
else:

    access = sys.argv[1]
    personal = sys.argv[2]
    total_patterns = int(sys.argv[3])

    #Set up db connection
    conn = MySQLdb.connect(host="localhost",user="guest",passwd="",db="Ravelry_Projects")
    x = conn.cursor()
    x.execute("""SELECT id FROM patterns_full """)

    all_ids = set(range(1,580171,1))
    prev_ids = [ele[0] for ele in x.fetchall()]
    print "Previously Downloaded: ", len(prev_ids)
    poss_ids = all_ids.difference(set(prev_ids))
    print "Potentially Downloadable: ", len(poss_ids)

    #Loop over patterns
    nupload = 0
    #    for i in range(500,500+total_patterns,1):
    while (nupload < total_patterns):
#        continue;
        i = random.choice(tuple(poss_ids))
        poss_ids = poss_ids.difference(set([i]))
#        print "Now Downloadable: ",len(poss_ids)

        request = urllib2.Request(("https://api.ravelry.com/patterns/"+str(i)+".json").strip())
        base64string = base64.encodestring('%s:%s' % (access,personal)).replace('\n','')
        request.add_header("Authorization","Basic %s" % base64string)

        try:
            response = urllib2.urlopen(request)
            data = json.load(response)['pattern']
            
            #Collect data on pattern

            info = []

            info.append(data['id'])
            name = data['name'].encode('utf-8').replace("'","")
            info.append("'"+name+"'")
            info.append(data['projects_count'])
            if data['published'] is None: continue
            else:
                pubdate = datetime.strptime(data['published'],'%Y/%m/%d')
                datediff = (datetime.today()-pubdate).days
                if datediff > 4000: continue
                else: info.append((datetime.today()-pubdate).days)

            #Using id numbers for crafts; knitting is 2
            info.append(data['craft']['id'])
            info.append(data['difficulty_average'])
            info.append(data['difficulty_count'])
            info.append(data['favorites_count'])
            isPattFree = data['free']
            for ele in data['printings']:
                if 'Free' in ele['pattern_source']['name'].encode('utf-8'): isPattFree = True
            if isPattFree: info.append(1)
            else: info.append(0)
            #        info.append(isPattFree)
            if len(data['pattern_categories']) > 0:
                info.append(getCategoryCode(data['pattern_categories'][0]))
            else:
                info.append(5)
            info.append(data['pattern_author']['patterns_count'])
            info.append(data['pattern_author']['favorites_count'])
            #also need to get number of pattern sources and probably check for free ones
            info.append(len(data['printings']))
            info.append(data['rating_average'])
            info.append(data['rating_count'])
            info.append(data['yardage'])
            #I think I could use Ravelry's id numbers for yarn weight as well
            if 'yarn_weight' not in data.keys(): info.append(0)
            else: info.append(data['yarn_weight']['id'])
            if data['downloadable']: info.append(1)
            else: info.append(0)
            #        info.append(data['downloadable'])
            info.append(data['gauge'])
            info.append(data['row_gauge'])
            #note that pattern attributes (things like female or unisex or lace) have id numbers
            info.append("'"+collectAttribs(data['pattern_attributes'])+"'")
            info.append(0)
            info.append(len(data['pattern_attributes']))
            info.append(data['comments_count'])

            #Clean up any Nones in the information (replace with zero)
            if None in info:
                clean_info = [0 if y==None else y for y in info]
            else: clean_info = info

            #Put data in database
            vals = ",".join(list(map(str,clean_info)))
            ctext = "INSERT INTO patterns_full VALUES ("+vals+")"
#            print ctext
            x.execute(ctext)
            conn.commit()
            nupload += 1

            if nupload % 100 == 0:
                print "Downloaded "+str(nupload)+" Patterns"

        except urllib2.HTTPError, e:
            continue

print "Finished"
conn.close()
