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
from workerthread import WorkerThread

class SocketTaskView(gui3d.TaskView):

    def __init__(self, category):
        self.human = gui3d.app.selectedHuman
        gui3d.TaskView.__init__(self, category, 'Socket')

        box = self.addLeftWidget(gui.GroupBox('Server'))
        
        self.aToggleButton = box.addWidget(gui.CheckBox('Accept connections'))

        @self.aToggleButton.mhEvent
        def onClicked(event):
            if self.aToggleButton.selected:
                self.openSocket()
            else:
                self.closeSocket()

        self.scriptText = self.addTopWidget(gui.DocumentEdit())
        self.scriptText.setText('');
        self.scriptText.setLineWrapMode(gui.DocumentEdit.NoWrap)

        self.dirops = SocketDirOps(self)
        self.meshops = SocketMeshOps(self)
        self.modops = SocketModifierOps(self)        

    def threadMessage(self,message):
        self.addMessage(str(message))

    def evaluateCall(self):
        ops = None
        data = self.workerthread.jsonCall
        conn = self.workerthread.currentConnection

        if self.meshops.hasOp(data.function):
            ops = self.meshops

        if self.dirops.hasOp(data.function):
            ops = self.dirops

        if self.modops.hasOp(data.function):
            ops = self.modops

        if ops:                
            jsonCall = ops.evaluateOp(conn,data)
        else:
            jsonCall = data
            jsonCall.error = "Unknown command"

        self.addMessage("About to serialize JSON. This might take some time.")
        response = jsonCall.serialize()

        print "About to send:\n\n" + response
        conn.send(response)
        conn.close()
 
    def addMessage(self,message,newLine = True):
        if newLine:
            message = message + "\n";
        self.scriptText.addText(message)
        
    def openSocket(self):
        self.addMessage("Starting server thread.")
        self.workerthread = WorkerThread()
        self.scriptText.connect(self.workerthread,SIGNAL("evaluateCall()"),self.evaluateCall)
        self.scriptText.connect(self.workerthread,SIGNAL("addMessage(QString)"),self.threadMessage)
        self.workerthread.start()
        #start_new_thread(self.serverThread,(None,))

    def closeSocket(self):
        #self.addMessage("Closing socket.")
        if not self.workerthread is None:
            self.workerthread.stopListening();
        self.workerthread = None

category = None
taskview = None


def load(app):
    category = app.getCategory('Community')
    taskview = category.addTask(SocketTaskView(category))

def unload(app):
    if taskview:
        taskview.closeSocket()
