#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

""" 
**Project Name:**      MakeHuman server socket plugin

**Product Home Page:** TBD

**Code Home Page:**    TBD

**Authors:**           Joel Palmius

**Copyright(c):**      Joel Palmius 2016

**Licensing:**         MIT

Abstract
--------

This plugin opens a TCP socket and accepts some basic commands. It 
does not make much sense without a corresponding client.

"""

import gui3d
import mh
import gui
import log
import socket
import json

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from dirops import SocketDirOps
from meshops import SocketMeshOps
from modops import SocketModifierOps

class WorkerThread(QThread):

    def __init__(self, parent = None):
        QThread.__init__(self, parent)
        self.exiting = False
        #self.taskview = taskview

    def addMessage(self,message,newLine = True):
        self.emit(SIGNAL("addMessage(QString)"),QString(message))
        print message
        pass

    def run(self):
        self.addMessage("Opening server socket... ")        
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket.bind(('127.0.0.1', 12345))
        except socket.error , msg:
            self.addMessage('Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1] + "\n")
            return;

        self.addMessage("opened at port 12345\n")        

        self.socket.listen(10)

        while not self.exiting:
            self.addMessage("Waiting for connection.")        

            try:
                conn, addr = self.socket.accept()
    
                if conn and not self.exiting:
                    self.addMessage("Connected with " + addr[0] + ":" + str(addr[1]))
                    data = conn.recv(8192)
                    self.addMessage("Client says: '" + data + "'")
                    data = gui3d.app.mhapi.internals.JsonCall(data)
    
                    self.jsonCall = data
                    self.currentConnection = conn
    
                    self.emit(SIGNAL("evaluateCall()"))
            except socket.error:
                """Assume this is because we closed the socket from outside"""
                pass

    def stopListening(self):
        if not self.exiting:
            self.addMessage("Stopping socket connection")
            self.exiting = True
            try:
                self.socket.shutdown(socket.SHUT_RDWR)
            except socket.error:
                """If the socket was not connected, shutdown will complain. This isn't a problem, 
                so just ignore."""
                pass
            self.socket.close()

    def __del__(self):        
        self.stopListening()


