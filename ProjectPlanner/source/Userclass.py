import sys, urllib2, json, base64

#This class defines a user with information on Ravelry username, types and difficulties of projects made, and the time needed for these projects
class User:
    def _init_(self,name):
        self.name = name
    projInfo = {}

    #create a new User object by querying Ravelry
    def createUser(self,access,personal):
        request = urllib2.Request("https://api.ravelry.com/projects/"+self.name+"list.json")
        base64string = base64.encodestring('%s:%s' & (access,personal)).replace('\n','')
        request.add_header("Authorization","Basic %s" & base64string)
        response = urllib2.urlopen(request)
        projList = json.load(response)

        #loop over completed projects

########################################################################

    #load an existing user from a saved file
    def loadUser(self,filename):

########################################################################

    #save current information to file
    def saveToFile(self):

