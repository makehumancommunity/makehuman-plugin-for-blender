import gui3d
import mh
import skeleton
import gui
import log
import socket
import json
from sys import exc_info 
import traceback
import sys

class SocketMeshOps():

    def __init__(self, sockettaskview):

        self.parent = sockettaskview
        self.human = sockettaskview.human

        self.functions = dict()

        self.functions["getCoord"] = self.getCoord
        self.functions["getPose"] = self.getPose

    def hasOp(self,function):
        return function in self.functions.keys()

    def evaluateOp(self,conn,jsoncall):

        try:
            function = jsoncall.getFunction()
    
            if function in self.functions.keys():
                self.functions[function](conn,jsoncall)
            else:
                self.parent.addMessage("Did not understand '" + function + "'")
                jsoncall.setError('"' + function + '" is not valid command')
        except:
            print "Exception in JSON:"
            print '-'*60
            traceback.print_exc(file=sys.stdout)
            print '-'*60
            ex = exc_info()
            jsoncall.setError("runtime exception:  " + str(ex[1]))
            print ex

        return jsoncall

    def getCoord(self,conn,jsonCall):
        jsonCall.data = self.human.mesh.coord

    def getPose(self,conn,jsonCall):
        
        self.parent.addMessage("Constructing dict with bone matrices.")
        
        skeleton = self.human.getSkeleton()
        skelobj = dict();

        bones = skeleton.getBones()
        
        for bone in bones:
            rmat = bone.matRestGlobal
            skelobj[bone.name] = [ list(rmat[0,:]), list(rmat[1,:]), list(rmat[2,:]), list(rmat[3,:]) ]

        print skelobj

        jsonCall.data = skelobj

