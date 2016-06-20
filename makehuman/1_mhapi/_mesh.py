#!/usr/bin/python

from namespace import NameSpace

class Mesh(NameSpace):
    """This namespace wraps call which works directly on mesh vertices, edges and faces."""

    def __init__(self,api):
        self.api = api
        NameSpace.__init__(self)
        self.trace()

    def getVertexCoordinates(self):
        """Return an array with the current position of vertices"""
        self.trace()
        human = self.api.internals.getHuman()
        return human.mesh.coord

