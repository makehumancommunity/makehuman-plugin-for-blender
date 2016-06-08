import gui3d
import mh
import skeleton
#from transformations import quaternion_from_matrix
import gui
import log
import socket
import json
from sys import exc_info 

class SocketMeshOps():

    def __init__(self, sockettaskview):

        self.parent = sockettaskview
        self.human = sockettaskview.human

    def evaluateOp(self,conn,data):

        valProblem = None

        try:
            if data == "getCoord":
                self.getCoord(conn)
            elif data == "getPose": 
                if self.human.getSkeleton():
                    self.getPose(conn)
                else:
                    valProblem = "no skeleton assigned in MH"
            else:
                valProblem = '"' + data + '" is not valid command'
                
        except:
            ex = exc_info()
            valProblem = "runtime exception:  " + str(ex[1])

        return valProblem

    def getCoord(self,conn):

        self.parent.addMessage("Constructing JSON object with vertex coords. This might take some time.")
        coords = '{ "data" : [ ';

        first = True
        for c in self.human.mesh.coord:
            if first:
                first = False
            else:
                coords += ","
            coords += "\n" + arrayAsString(c);

        coords += "\n] }\n";
        #print coords
        self.parent.addMessage("Sending JSON")
        conn.send(coords)

    def getPose(self,conn):
        
        self.parent.addMessage("Constructing JSON object with bone matrices.")
        
        skeleton = self.human.getSkeleton()
        pose = '{ ';

        first = True
        
        bones = skeleton.getBones()
        
        for bone in bones:
            if first:
                first = False
            else:
                pose += ","
            
            rmat = bone.matRestGlobal
            pose += '\n"' + bone.name + '":[' + arrayAsString(list(rmat[0,:])) + ', ' + arrayAsString(list(rmat[1,:])) + ', ' + arrayAsString(list(rmat[2,:])) + ', ' + arrayAsString(list(rmat[3,:])) + "]"

        pose += "\n}\n";
#        print pose
        self.parent.addMessage("Sending JSON")
        conn.send(pose)
        
def arrayAsString(array):
    ret = "[ "
    n = len(array)
    for i in range(n):
        ret +="{0:.8f}".format(array[i])
        if i + 1 < n:
            ret += ","
    return ret + " ]"
