#!/usr/bin/python
# -*- coding: utf-8 -*-

bl_info = {
    "name": "Import body from MakeHuman",
    "category": "Mesh",
}

from .sync_ops import SyncOperator

import bpy
import bmesh
import pprint
import struct

pp = pprint.PrettyPrinter(indent=4)

class GetBodyInfo(SyncOperator):
    def __init__(self, readyFunction):
        super().__init__('getBodyMeshInfo')
        self.readyFunction = readyFunction
        self.executeJsonCall()

    def callback(self, json_obj):
        self.readyFunction(json_obj.data)

class GetBodyVertices(SyncOperator):
    def __init__(self, readyFunction):
        super().__init__('getBodyVerticesBinary')
        self.readyFunction = readyFunction
        self.executeJsonCall(expectBinaryResponse=True)

    def callback(self, data):
        self.readyFunction(data)

class GetBodyFaces(SyncOperator):
    def __init__(self, readyFunction):
        super().__init__('getBodyFacesBinary')
        self.readyFunction = readyFunction
        self.executeJsonCall(expectBinaryResponse=True)

    def callback(self, data):
        self.readyFunction(data)


class ImportBodyBinary():

    def __init__(self):
        print("Import body")
        self.scaleFactor = 0.1
        self.minimumZ = 10000.0
        GetBodyInfo(self.gotBodyInfo)

    def gotBodyInfo(self, data):
        print(data)
        self.bodyInfo = data

        self.mesh = bpy.data.meshes.new("HumanBodyMesh")
        self.obj = bpy.data.objects.new("HumanBody", self.mesh)

        scene = bpy.context.scene
        scene.objects.link(self.obj)
        scene.objects.active = self.obj
        self.obj.select = True

        self.mesh = bpy.context.object.data
        self.bm = bmesh.new()

        GetBodyVertices(self.gotVerticesData)

    def gotVerticesData(self, data):
        print(len(data))
        print(len(data) / 4 / 3)
        print(self.bodyInfo["numVertices"])

        self.vertCache = []

        iMax = int(len(data) / 4 / 3)
        assert(iMax == int(self.bodyInfo["numVertices"]))

        i = 0
        while i < iMax:
            sliceStart = i * 4 * 3 # 4-byte floats, three vertices

            xbytes = data[sliceStart:sliceStart + 4]
            ybytes = data[sliceStart + 4:sliceStart + 4 + 4]
            zbytes = data[sliceStart + 4 + 4:sliceStart + 4 + 4 +4]

            x = struct.unpack("f", bytes(xbytes))[0] * self.scaleFactor
            y = struct.unpack("f", bytes(ybytes))[0] * self.scaleFactor
            z = struct.unpack("f", bytes(zbytes))[0] * self.scaleFactor

            if z < self.minimumZ:
                self.minimumZ = z

            # Coordinate order from MH is XZY
            vert = self.bm.verts.new( (x, z, y) )
            vert.index = i

            self.vertCache.append(vert)

            i = i + 1

        GetBodyFaces(self.gotFacesData)

    def gotFacesData(self, data):
        print(len(data))
        print(len(data) / 4 / 4)
        print(self.bodyInfo)

        self.faceCache = []

        iMax = int(len(data) / 4 / 4)
        assert (iMax == int(self.bodyInfo["numFaces"]))

        i = 0
        while i < iMax:
            sliceStart = i * 4 * 4  # 4-byte unsigned ints, four verts per face

            stride = 0;
            verts = [None, None, None, None]
            while stride < 4:
                sliceStart = i * 4 * 4  # 4-byte floats, three vertices
                vertbytes = data[sliceStart + stride * 4:sliceStart + stride * 4 + 4]
                vert = self.vertCache[int(struct.unpack("I", bytes(vertbytes))[0])]
                verts[stride] = vert
                stride = stride + 1
            face = self.bm.faces.new(verts)
            face.index = i
            face.smooth = True
            self.faceCache.append(face)
            i = i + 1

        self.afterMeshData()


    def afterMeshData(self):

        bmesh.ops.recalc_face_normals(self.bm, faces=self.bm.faces)

        self.bm.to_mesh(self.mesh)
        self.bm.free()

        vgbody = self.obj.vertex_groups.new(name="body")
        vgbody.add([ 0, 1, 2 ], 1.0, 'ADD')

        del self.vertCache
        del self.faceCache







