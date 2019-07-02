#!/usr/bin/python
# -*- coding: utf-8 -*-

bl_info = {
    "name": "Import body from MakeHuman",
    "category": "Mesh",
}

import bpy
import bmesh
import pprint
import struct
import time
import itertools

from .material import *
from .fetch_server_data import FetchServerData
from ..util import *

pp = pprint.PrettyPrinter(indent=4)

ENABLE_PROFILING_OUTPUT = False

PROXY_COLORS = {"Proxymeshes": (1.0, 0.7, 0.7, 1.0),
                "Clothes": (0.5, 1.0, 1.0, 1.0),
                "Hair": (0.08, 0.015, 0.015, 1.0),
                "Eyebrows": (0.08, 0.015, 0.015, 1.0),
                "Eyelashes": (0.08, 0.015, 0.015, 1.0),
                "Eyes": (1.0, 1.0, 1.0, 1.0)
                }

class ImportProxyBinary():

    def __init__(self, humanObject, humanName, proxyInfo, onFinished=None, collection=None):
        print("Importing proxy: " + proxyInfo["name"])

        #pp.pprint(proxyInfo)

        self.humanObject = humanObject
        self.humanName = humanName
        self.proxyInfo = proxyInfo
        self.onFinished = onFinished
        self.collection = collection

        self.handleMaterials = str(bpy.context.scene.MhHandleMaterials)
        self.prefixMaterial = bpy.context.scene.MhPrefixMaterial
        self.matobjname = bpy.context.scene.MhMaterialObjectName
        self.prefixProxy = bpy.context.scene.MhPrefixProxy

        self.scaleFactor = 0.1

        self.startMillis = int(round(time.time() * 1000))
        self.lastMillis = self.startMillis

        self.scaleMode = str(bpy.context.scene.MhScaleMode)

        self.generalPreset = str(bpy.context.scene.MhGeneralPreset)

        if self.generalPreset != "DEFAULT":
            self.scaleMode = "DECIMETER"
            self.handleMaterials = "CREATENEW"
            self.importWhat = "EVERYTHING"
            self.helpers = "MASK"
            self.subdiv = False
            self.matobjname = True
            self.importRig = False
            self.detailedHelpers = True
            self.rigisparent = False
            self.adjust = False
            self.prefixProxy = False

        if self.scaleMode == "DECIMETER":
            self.scaleFactor = 1.0

        if self.scaleMode == "CENTIMETER":
            self.scaleFactor = 10.0

        self.minimumZ = 10000.0

        namebase = ""
        if self.prefixProxy:
            namebase = humanName + "."

        self.mesh = bpy.data.meshes.new(namebase + self.proxyInfo["name"] + "Mesh")
        self.obj = bpy.data.objects.new(namebase + self.proxyInfo["name"], self.mesh)

        self.obj.MhHuman = False
        self.obj.MhObjectType = proxyInfo["type"]
        self.obj.MhProxyUUID = proxyInfo["uuid"]
        self.obj.MhProxyName = proxyInfo["name"]

        # TODO: Set more info, for example name of toon

        self.vertPosCache = []
        self.mid_verts = []
        self.left_verts = []
        self.right_verts = []

        linkObject(self.obj, self.collection)
        activateObject(self.obj)
        selectObject(self.obj)

        self.mesh = bpy.context.object.data
        self.bm = bmesh.new()
        FetchServerData('getProxyVerticesBinary', self.gotVerticesData, expectBinary=True, params={ "uuid": self.proxyInfo["uuid"] })

    def _profile(self, position="timestamp"):
        if not ENABLE_PROFILING_OUTPUT:
            return
        currentMillis = int(round(time.time() * 1000))
        print(position + ": " + str(currentMillis - self.startMillis) + " / " + str(currentMillis - self.lastMillis))
        self.lastMillis = currentMillis

    def gotVerticesData(self, data):
        self._profile()
        self.vertCache = []

        iMax = int(len(data) / 4 / 3)

        assert(iMax == int(self.proxyInfo["numVertices"]))

        i = 0
        while i < iMax:
            sliceStart = i * 4 * 3 # 4-byte floats, three values per vertex

            # Coordinate order from MH is XZY
            xbytes = data[sliceStart:sliceStart + 4]
            zbytes = data[sliceStart + 4:sliceStart + 4 + 4]
            ybytes = data[sliceStart + 4 + 4:sliceStart + 4 + 4 +4]

            x = struct.unpack("f", bytes(xbytes))[0] * self.scaleFactor
            y = struct.unpack("f", bytes(ybytes))[0] * self.scaleFactor
            z = struct.unpack("f", bytes(zbytes))[0] * self.scaleFactor

            if z < self.minimumZ:
                self.minimumZ = z

            vert = self.bm.verts.new( (x, -y, z) )
            vert.index = i

            self.vertCache.append(vert)
            self.vertPosCache.append( (x, -y, z) )

            i = i + 1

        FetchServerData('getProxyFacesBinary',self.gotFacesData, expectBinary=True, params={ "uuid": self.proxyInfo["uuid"] })

    def gotFacesData(self, data):
        self._profile()
        self.faceCache = []
        self.faceVertIndexes=[]

        iMax = int(len(data) / 4 / 4)
        assert (iMax == int(self.proxyInfo["numFaces"]))

        i = 0
        while i < iMax:
            stride = 0
            verts = [None, None, None, None]
            vertIdxs = [None, None, None, None]
            while stride < 4:
                sliceStart = i * 4 * 4  # 4-byte ints, four vertices per face
                vertbytes = data[sliceStart + stride * 4:sliceStart + stride * 4 + 4]
                vert = self.vertCache[int(struct.unpack("I", bytes(vertbytes))[0])]
                verts[stride] = vert
                vertIdxs[stride] = vert.index
                stride = stride + 1
            if verts[0] == verts[3]:
                verts.pop(3)
                vertIdxs.pop(3)
            face = self.bm.faces.new(verts)
            face.index = i
            face.smooth = True
            self.faceCache.append(face)
            self.faceVertIndexes.append(vertIdxs)
            i = i + 1

        FetchServerData('getProxyTextureCoordsBinary', self.gotTextureCoords, expectBinary=True, params={ "uuid": self.proxyInfo["uuid"] })


    def gotTextureCoords(self, data):
        iMax = int(len(data) / 4 / 2)
        assert (iMax == int(self.proxyInfo["numTextureCoords"]))

        self.texco = []

        i = 0
        while i < iMax:
            sliceStart = i * 4 * 2  # 4-byte floats, two values per coordinate
            ubytes = data[sliceStart:sliceStart + 4]
            vbytes = data[sliceStart + 4:sliceStart + 4 + 4]
            u = struct.unpack("f", bytes(ubytes))[0]
            v = struct.unpack("f", bytes(vbytes))[0]
            self.texco.append([u, v])
            i = i + 1

        FetchServerData('getProxyFaceUVMappingsBinary', self.gotFaceUVMappings, expectBinary=True, params={ "uuid": self.proxyInfo["uuid"] })

    def gotFaceUVMappings(self, data):
        iMax = int(len(data) / 4 / 4)
        assert (iMax == int(self.proxyInfo["numFaceUVMappings"]))

        i = 0
        faceTexco = []

        while i < iMax:
            stride = 0
            ftex = [None, None, None, None]
            while stride < 4:
                sliceStart = i * 4 * 4  # 4-byte ints, four mappings per face
                mapbytes = data[sliceStart + stride * 4:sliceStart + stride * 4 + 4]
                idx = struct.unpack("I", bytes(mapbytes))[0]
                ftex[stride] = self.texco[int(idx)]
                stride = stride + 1
            faceTexco.append(ftex)
            i = i + 1

        uv_layer = self.bm.loops.layers.uv.verify()

        if not bl28():
            # TODO: There is probably a way to do this in blender 2.8 too
            self.bm.faces.layers.tex.verify()

        for face in self.bm.faces:
            for i, loop in enumerate(face.loops):
                uv = loop[uv_layer].uv
                texco = faceTexco[face.index][i]
                uv[0] = texco[0]
                uv[1] = texco[1]

        self.afterMeshData()

    def _faceListToVertSet(self, faceList):
        vertList = []
        for faceIdx in list(faceList):
            if faceIdx >= len(self.faceVertIndexes):
                print("WARNING: face index " + str(faceIdx) + " > " + str(len(self.faceVertIndexes)))
            else:
                vertList.extend( self.faceVertIndexes[faceIdx] )
        return set(vertList)

    def maskFaces(self):

        if len(self.proxyInfo["faceMask"]) < 1:
            return

        allVisibleFaces = []

        for facelist in self.proxyInfo["faceMask"]:
            first = facelist[0]
            last = facelist[1]
            allVisibleFaces.extend(list(range(first, last + 1)))

        allVisibleFaces = set(allVisibleFaces)
        allVisibleVerts = list(self._faceListToVertSet(allVisibleFaces))
        allVerts = set(range(0, len(self.vertCache)))

        # TODO:   This approach may cause single vertex outliers. At some point it might make sense
        # TODO:   to find and exclude these
        allInvisibleVerts = list(allVerts - set(allVisibleVerts))

        vgroupInvis = self.obj.vertex_groups.new(name="Delete")
        vgroupInvis.add(allInvisibleVerts, 1.0, 'ADD')

        mask = self.obj.modifiers.new("Hide faces", 'MASK')
        mask.vertex_group = "Delete"
        mask.show_in_editmode = True
        mask.show_on_cage = True
        mask.invert_vertex_group = True

    def makeClothesExtras(self):
        i = 0
        print("MakeClothes extras")

        while i < len(self.vertPosCache):
            vert = self.vertPosCache[i]
            x = vert[0]

            if x > -0.01 and x < 0.01:
                self.mid_verts.append(i)
            else:
                if x < 0.0:
                    self.right_verts.append(i)
                if x > 0.0:
                    self.left_verts.append(i)

            i = i + 1

        if len(self.right_verts) > 0:
            vgroup = self.obj.vertex_groups.new(name="Right")
            vgroup.add(self.right_verts, 1.0, 'ADD')

        if len(self.left_verts) > 0:
            vgroup = self.obj.vertex_groups.new(name="Left")
            vgroup.add(self.left_verts, 1.0, 'ADD')

        if len(self.mid_verts) > 0:
            vgroup = self.obj.vertex_groups.new(name="Mid")
            vgroup.add(self.mid_verts, 1.0, 'ADD')

    def afterMeshData(self):

        bmesh.ops.recalc_face_normals(self.bm, faces=self.bm.faces)

        self.bm.to_mesh(self.mesh)
        self.bm.free()

        if self.generalPreset == "MAKECLOTHES":
            self.makeClothesExtras()

        self.maskFaces()

        del self.vertCache
        del self.faceCache
        del self.texco

        FetchServerData('getProxyMaterialInfo', self.gotProxyMaterialInfo, expectBinary=False, params={ "uuid": self.proxyInfo["uuid"] })

    def gotProxyMaterialInfo(self, data):
        matname = data["name"]

        if self.matobjname or matname in ["material", "materialMaterial", "bodyMaterial", "", "none"]:
            matname = self.proxyInfo["name"]

        if self.prefixMaterial:
            matname = self.humanName + "." + matname

        baseColor = data.get("viewPortColor", PROXY_COLORS.get(self.proxyInfo["type"], (0.8, 0.8, 0.8, 1.0)))

        if len(baseColor) < 4:
            baseColor = tuple([*baseColor, data.get("viewPortAlpha", 1.0)])

        mat = createMHMaterial(matname, data, baseColor=baseColor, ifExists=self.handleMaterials)

        self.obj.data.materials.append(mat)
        if not self.onFinished is None:
            self.onFinished(self)













