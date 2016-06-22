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
from core import G

class SocketModifierOps():

    def __init__(self, sockettaskview):

        self.parent = sockettaskview
        self.api = G.app.mhapi

        self.functions = dict()

        self.functions["getAvailableModifierNames"] = self.getAvailableModifierNames
        self.functions["getAppliedTargets"] = self.getAppliedTargets

    def hasOp(self,function):
        return function in self.functions.keys()

    def evaluateOp(self,conn,jsoncall):

        try:
            function = jsoncall.getFunction()
    
            if function in self.functions.keys():
                self.functions[function](conn,jsoncall)
            else:
                self.parent.addMessage("(modops) Did not understand '" + function + "'")
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


    def getAvailableModifierNames(self,conn,jsonCall):
        jsonCall.data = self.api.modifiers.getAvailableModifierNames()

    def getAppliedTargets(self,conn,jsonCall):
        jsonCall.data = self.api.modifiers.getAppliedTargets()


