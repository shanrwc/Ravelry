import sys, urllib2, json, base64

def queryRavelry(query):
    request = urllib2.Request(query)
    base64string = base64.encodestring('%s:%s' % ('DF2EF65A6DCD4910BC39','6NYcEbfAk6OGorac_zccaLp0vklTFTy8MXB1t6de')).replace('\n','')
    request.add_header("Authorization","Basic %s" % base64string)
    response = urllib2.urlopen(request)
    return(response)
