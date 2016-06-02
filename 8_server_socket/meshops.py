import gui3d
import mh
import gui
import log
import socket
import json

class SocketMeshOps():

    def __init__(self, sockettaskview):

        self.parent = sockettaskview
        self.human = sockettaskview.human

    def evaluateOp(self,conn,data):

        valid = False

        if(data == "getCoord"):
            self.getCoord(conn)
            valid = True

        return valid


    def getCoord(self,conn):

        self.parent.addMessage("Constructing JSON object with vertex coords. This might take some time.")
        coords = '{ "data" : [ ';

        first = True
        for c in self.human.mesh.coord:
            if first:
                first = False
            else:
                coords = coords + ","
            coords = coords + "\n[ ";
            coords = coords + "{0:.8f}".format(c[0]) + ", "
            coords = coords + "{0:.8f}".format(c[1]) + ", "
            coords = coords + "{0:.8f}".format(c[2]) + " ]"

        coords = coords + "\n] }\n";
        #print coords
        self.parent.addMessage("Sending JSON")
        conn.send(coords)


