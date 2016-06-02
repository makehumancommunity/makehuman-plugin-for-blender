import gui3d
import mh
import gui
import log
import socket
import json

class SocketDirOps():

    def __init__(self, sockettaskview):

        self.parent = sockettaskview

    def evaluateOp(self,conn,data):

        valid = False

        if(data == "getUserDir"):            
            self.getUserDir(conn)
            valid = True

        if(data == "getSysDir"):
            self.getSysDir(conn)
            valid = True

        return valid


    def getUserDir(self,conn):
        pth = os.path.abspath(mh.getPath()) + "\n"
        self.parent.addMessage("Sending user dir: " + pth)
        conn.send(pth)

    def getSysDir(self,conn):
        pth = os.path.abspath(mh.getSysPath()) + "\n"
        self.parent.addMessage("Sending sys dir: " + pth)
        conn.send(pth)


