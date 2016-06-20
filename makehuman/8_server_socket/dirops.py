import gui3d
import mh
import gui
import log
import socket
import json
from sys import exc_info 
import traceback
import sys
import os

class SocketDirOps():

    def __init__(self, sockettaskview):

        self.parent = sockettaskview

        self.functions = dict()

        self.functions["getUserDir"] = self.getUserDir
        self.functions["getSysDir"] = self.getSysDir

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


    def getUserDir(self,conn,jsonCall):
        jsonCall.data = os.path.abspath(mh.getPath())

    def getSysDir(self,conn,jsonCall):
        jsonCall.data = os.path.abspath(mh.getSysPath()) 


