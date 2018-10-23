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

from mathutils import Matrix, Vector
from .material import *
from .fetch_server_data import FetchServerData
from .import_proxy_binary import ImportProxyBinary

pp = pprint.PrettyPrinter(indent=4)

ENABLE_PROFILING_OUTPUT = False

class ImportBodyBinary():

    def __init__(self):
        print("Import body")

        self.armatureObject = None

        self.scaleFactor = 0.1

        self.startMillis = int(round(time.time() * 1000))
        self.lastMillis = self.startMillis

        self.scaleMode = str(bpy.context.scene.MhScaleMode)

        if self.scaleMode == "DECIMETER":
            self.scaleFactor = 1.0

        if self.scaleMode == "CENTIMETER":
            self.scaleFactor = 10.0

        self.minimumZ = 10000.0
        FetchServerData('getBodyMeshInfo', self.gotBodyInfo)

    def _profile(self, position="timestamp"):
        if not ENABLE_PROFILING_OUTPUT:
            return
        currentMillis = int(round(time.time() * 1000))
        print(position + ": " + str(currentMillis - self.startMillis) + " / " + str(currentMillis - self.lastMillis))
        self.lastMillis = currentMillis

    def gotBodyInfo(self, data):

        #pp.pprint(data)

        self.bodyInfo = data
        self.mesh = bpy.data.meshes.new("HumanBodyMesh")
        self.obj = bpy.data.objects.new("HumanBody", self.mesh)

        self.obj.MhHuman = True

        # TODO: Set more info, for example name of toon

        scene = bpy.context.scene
        scene.objects.link(self.obj)
        scene.objects.active = self.obj
        self.obj.select = True

        self.mesh = bpy.context.object.data
        self.bm = bmesh.new()

        FetchServerData('getBodyVerticesBinary',self.gotVerticesData,True)

    def gotVerticesData(self, data):
        self._profile()
        self.vertCache = []

        iMax = int(len(data) / 4 / 3)
        assert(iMax == int(self.bodyInfo["numVertices"]))

        i = 0
        while i < iMax:
            sliceStart = i * 4 * 3 # 4-byte floats, three values per vertex

            # Coordinate order from MH is XZY
            xbytes = data[sliceStart:sliceStart + 4]
            zbytes = data[sliceStart + 4:sliceStart + 4 + 4]
            ybytes = data[sliceStart + 4 + 4:sliceStart + 4 + 4 +4]

            x = struct.unpack("f", bytes(xbytes))[0] * self.scaleFactor
            z = struct.unpack("f", bytes(zbytes))[0] * self.scaleFactor
            y = struct.unpack("f", bytes(ybytes))[0] * self.scaleFactor

            if z < self.minimumZ:
                self.minimumZ = z

            vert = self.bm.verts.new( (x, -y, z) )
            vert.index = i

            self.vertCache.append(vert)

            i = i + 1

        FetchServerData('getBodyFacesBinary',self.gotFacesData,True)

    def gotFacesData(self, data):
        self._profile()
        self.faceCache = []
        self.faceVertIndexes=[]

        iMax = int(len(data) / 4 / 4)
        assert (iMax == int(self.bodyInfo["numFaces"]))

        i = 0
        while i < iMax:
            stride = 0;
            verts = [None, None, None, None]
            vertIdxs = [None, None, None, None]
            while stride < 4:
                sliceStart = i * 4 * 4  # 4-byte ints, four vertices per face
                vertbytes = data[sliceStart + stride * 4:sliceStart + stride * 4 + 4]
                vert = self.vertCache[int(struct.unpack("I", bytes(vertbytes))[0])]
                verts[stride] = vert
                vertIdxs[stride] = vert.index
                stride = stride + 1
            face = self.bm.faces.new(verts)
            face.index = i
            face.smooth = True
            self.faceCache.append(face)
            self.faceVertIndexes.append(vertIdxs)
            i = i + 1

        FetchServerData('getBodyTextureCoordsBinary', self.gotTextureCoords, True)

    def gotTextureCoords(self, data):
        iMax = int(len(data) / 4 / 2)
        assert (iMax == int(self.bodyInfo["numTextureCoords"]))

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

        FetchServerData('getBodyFaceUVMappingsBinary', self.gotFaceUVMappings, True)

    def gotFaceUVMappings(self, data):
        iMax = int(len(data) / 4 / 4)
        assert (iMax == int(self.bodyInfo["numFaceUVMappings"]))

        i = 0
        faceTexco = []

        while i < iMax:
            stride = 0;
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
        self.bm.faces.layers.tex.verify()

        for face in self.bm.faces:
            for i, loop in enumerate(face.loops):
                uv = loop[uv_layer].uv
                texco = faceTexco[face.index][i]
                uv[0] = texco[0]
                uv[1] = texco[1]

        self.afterMeshData()

    def handleHelpers(self):

        all_joint_verts = []
        all_helper_verts = []

        for fg in self.bodyInfo["faceGroups"]:
            name = fg["name"]
            self._profile(name)
            first = fg["first"]
            last = fg["last"]
            faceSubSet = self.faceVertIndexes[first:last]
            verts = list(set(itertools.chain.from_iterable(faceSubSet)))

            if len(verts) > 0:
                if name.startswith("joint-"):
                    all_joint_verts.extend(verts)
                if name.startswith("helper-"):
                    all_helper_verts.extend(verts)
                if self.helpers == "MASK":
                    vgroup = self.obj.vertex_groups.new(name=name)
                    vgroup.add(verts, 1.0, 'ADD')

        if self.helpers == "DELETE":
            if len(all_joint_verts) > 0:
                # TODO: delete vertices
                pass
            if len(all_helper_verts) > 0:
                # TODO: delete vertices
                pass

        if self.helpers == "MASK":
            mask = self.obj.modifiers.new("Mask", 'MASK')
            mask.vertex_group = "body"
            mask.show_in_editmode = True
            mask.show_on_cage = True

    def afterMeshData(self):

        bmesh.ops.recalc_face_normals(self.bm, faces=self.bm.faces)

        self.bm.to_mesh(self.mesh)
        self.bm.free()

        self.helpers = str(bpy.context.scene.handle_helper)

        if self.helpers != "NOTHING":
            self.handleHelpers()

        del self.vertCache
        del self.faceCache
        del self.texco

        FetchServerData('getBodyMaterialInfo',self.gotBodyMaterialInfo)

    def gotBodyMaterialInfo(self, data):
        #print(data)
        mat = createMHMaterial("testa", data)
        self.obj.data.materials.append(mat)

        FetchServerData('getSkeleton', self.gotSkeleton)

    def gotProxiesInfo(self, data):
        self.proxiesInfo = data
        self.proxiesToImport = data
        self.nextProxyToImport = 0
        self.importNextProxy()

    def importNextProxy(self):
        if self.nextProxyToImport >= len(self.proxiesToImport):
            self.afterProxiesImported()
            return
        ImportProxyBinary(self.obj, "human", self.proxiesInfo[self.nextProxyToImport], self.proxyLoaded)

    def proxyLoaded(self, proxy):
        print("Proxy loaded")

        if self.armatureObject is None:
            proxy.obj.parent = self.obj
        else:
            proxy.obj.parent = self.armatureObject

        self.nextProxyToImport = self.nextProxyToImport + 1
        self.importNextProxy()

    def afterProxiesImported(self):
        print("Proxies imported")
        self.finalize()

    def _deselectAll(self):
        for ob in bpy.context.selected_objects:
            ob.select = False

    def _addBone(self, boneInfo, parentBone=None):
        bone = self.armature.edit_bones.new(boneInfo["name"])

        head = boneInfo["headPos"]
        tail = boneInfo["tailPos"]

        scale = self.scaleFactor

        # Z up
        vHead = Vector( (head[0] * scale, -head[2] * scale, head[1] * scale) )
        vTail = Vector( (tail[0] * scale, -tail[2] * scale, tail[1] * scale) )

        #offset = Vector(self.skeletonOffset) * scale
        #bone.head = vHead + offset
        #bone.tail = vTail + offset

        bone.head = vHead
        bone.tail = vTail

        if not parentBone is None:
            bone.parent = parentBone

        if "matrix" in boneInfo.keys():
            # from MHX2 exporter:
            mat = Matrix(boneInfo["matrix"])
            nmat = Matrix((mat[0], -mat[2], mat[1])).to_3x3().to_4x4()
            nmat.col[3] = bone.matrix.col[3]
            bone.matrix = nmat
        else:
            if "roll" in boneInfo.keys():
                bone.roll = boneInfo["roll"]

        for child in boneInfo["children"]:
            self._addBone(child, bone)

    def gotSkeleton(self, data):

        if data["name"] != "none" and len(data["bones"]) > 0:
            self._deselectAll()

            self.armature = bpy.data.armatures.new("human.armature")
            self.armatureObject = bpy.data.objects.new("human.armature", self.armature)

            scene = bpy.context.scene
            scene.objects.link(self.armatureObject)
            scene.objects.active = self.armatureObject

            bpy.ops.object.mode_set(mode='EDIT', toggle=False)

            self.skeletonOffset = data["offset"]

            for boneInfo in data["bones"]:
                self._addBone(boneInfo)

            bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

            self.obj.parent = self.armatureObject

        FetchServerData('getProxiesInfo', self.gotProxiesInfo)

    def finalize(self):

        self._deselectAll()

        if self.armatureObject is None:
            self.obj.select = True
        else:
            self.armatureObject.select = True

        print("DONE!")

