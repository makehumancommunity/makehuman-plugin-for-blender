#!/usr/bin/python
# -*- coding: utf-8 -*-

bl_info = {
    "name": "Import weighting from MakeHuman",
    "category": "Mesh",
}

import bpy
import bmesh
import pprint
import struct
import itertools

from mathutils import Matrix, Vector
from .material import *
from .fetch_server_data import FetchServerData
from .import_proxy_binary import ImportProxyBinary
from ..util import profile

pp = pprint.PrettyPrinter(indent=4)

class ImportWeighting():

    def __init__(self, objectToWorkWith, skeletonObject=None, onFinished=None):

        profile("start weighting")

        self.myObject = objectToWorkWith
        self.skeletonObj = skeletonObject
        self.onFinished = onFinished
        self.processedVertices = 0
        self.debug = False

        self.isBaseMesh = (self.myObject.MhObjectType == "Basemesh")

        if self.debug:
            print("Import weighting for: " + objectToWorkWith.name)
            print("isBaseMesh: " + str(self.isBaseMesh))

        if self.isBaseMesh:
            FetchServerData('getBodyWeightInfo', self.gotWeightInfo)
        else:
            self.uuid = self.myObject.MhProxyUUID
            if self.debug:
                print("Mesh uuid: " + self.uuid)
            FetchServerData('getProxyWeightInfo', self.gotWeightInfo, params={ "uuid": self.uuid })


    def gotWeightInfo(self, data):
        profile("gotWeightInfo")

        #pp.pprint(data)
        assert(not data is None)
        self.sumVerts = data["sumVerts"]
        self.sumVertListBytes = data["sumVertListBytes"]
        self.sumWeightsBytes = data["sumWeightsBytes"]
        self.weights = data["weights"]
        if self.isBaseMesh:
            FetchServerData('getBodyWeightsVertList', self.gotVertListData, expectBinary=True)
        else:
            FetchServerData('getProxyWeightsVertList', self.gotVertListData, expectBinary=True, params={ "uuid": self.uuid })

    def gotVertListData(self, data):

        profile("gotVertListData")

        if self.debug:
            print("vert list: " + str(len(data)) + " bytes")
        self.vertListBytes = bytearray(data)
        if self.isBaseMesh:
            FetchServerData('getBodyWeights', self.gotWeightsData, expectBinary=True)
        else:
            FetchServerData('getProxyWeights', self.gotWeightsData, expectBinary=True, params={ "uuid": self.uuid })

    def gotWeightsData(self, data):

        profile("gotWeightsData")

        if self.debug:
            print("weight data: " + str(len(data)) + " bytes")
        self.weightBytes = bytearray(data)
        for info in self.weights:
            self.handleWeight(info)

        profile("weightsHandled")
        self.finalize()

    def handleWeight(self, info):

        beforeTime = int(round(time.time() * 1000))

        boneName = info["bone"]
        numVerts = info["numVertices"]

        if self.debug:
            print("Handling weights for bone " + boneName + " (" + str(numVerts) + " vertices)")

        vertGroup = self.myObject.vertex_groups.new(name=boneName)

        bytesStart = self.processedVertices * 4 # both vert list and weights come as four bytes per vertex
        bytesEnd = self.processedVertices * 4 + numVerts * 4
        self.processedVertices = self.processedVertices + numVerts

        currentListBytes = self.vertListBytes[bytesStart:bytesEnd]
        currentWeightBytes = self.weightBytes[bytesStart:bytesEnd]

        i = 0
        while i < numVerts:
            oneWeightBytes = currentWeightBytes[i*4:i*4+4]
            oneVertBytes = currentListBytes[i*4:i*4+4]
            weight = struct.unpack("f", bytes(oneWeightBytes))[0]
            vertNum = struct.unpack("I", bytes(oneVertBytes))[0]
            vertGroup.add([vertNum], weight, 'ADD')
            i = i + 1

        afterTime = int(round(time.time() * 1000))

        totalTime = afterTime - beforeTime

        if totalTime > 5:
            print("Weighting bone " + boneName + " for " + self.myObject.name + " took " + str(totalTime) + " milliseconds")


    def finalize(self):
        if not self.onFinished is None:
            self.onFinished()

