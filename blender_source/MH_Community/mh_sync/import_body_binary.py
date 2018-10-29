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
from .import_weighting import ImportWeighting

pp = pprint.PrettyPrinter(indent=4)

ENABLE_PROFILING_OUTPUT = False

class ImportBodyBinary():

    def __init__(self):
        print("Import body")

        self.name = "human"

        self.armatureObject = None
        self.hasProxy = False
        self.scaleFactor = 0.1

        self.startMillis = int(round(time.time() * 1000))
        self.lastMillis = self.startMillis

        self.scaleMode = str(bpy.context.scene.MhScaleMode)
        self.handleMaterials = str(bpy.context.scene.MhHandleMaterials)
        self.prefixMaterial = bpy.context.scene.MhPrefixMaterial
        self.detailedHelpers = bpy.context.scene.MhDetailedHelpers
        self.importWhat = str(bpy.context.scene.MhImportWhat)
        self.helpers = str(bpy.context.scene.MhHandleHelper)
        self.subdiv = str(bpy.context.scene.MhAddSubdiv)

        self.all_joint_verts = []
        self.all_helper_verts = []

        self.all_meta_faces = []

        if self.scaleMode == "DECIMETER":
            self.scaleFactor = 1.0

        if self.scaleMode == "CENTIMETER":
            self.scaleFactor = 10.0

        self.importedProxies = []

        self.minimumZ = 10000.0
        FetchServerData('getBodyMeshInfo', self.gotBodyInfo)

    def _profile(self, position="timestamp"):
        if not ENABLE_PROFILING_OUTPUT:
            return
        currentMillis = int(round(time.time() * 1000))
        print(position + ": " + str(currentMillis - self.startMillis) + " / " + str(currentMillis - self.lastMillis))
        self.lastMillis = currentMillis

    def gotBodyInfo(self, data):

        self.bodyInfo = data

        if "name" in data:
            name = data["name"]
            if not name is None and name != "untitled" and name != "":
                self.name = name

        self.mesh = bpy.data.meshes.new(self.name + "BodyMesh")
        self.obj = bpy.data.objects.new(self.name + "Body", self.mesh)

        self.obj.MhHuman = True
        self.obj.MhObjectType = "Basemesh"

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

        for fg in self.bodyInfo["faceGroups"]:
            name = fg["name"]
            self._profile(name)
            verts = []
            for startStop in fg["fgStartStops"]:
                first = startStop[0]
                last = startStop[1]
                if not fg["name"] == "body":
                    self.all_meta_faces.extend( list(range(first, last+1)) )
                faceSubSet = self.faceVertIndexes[first:last]
                verts.extend(list(set(itertools.chain.from_iterable(faceSubSet))))

            if len(verts) > 0:
                if name.startswith("joint-"):
                    self.all_joint_verts.extend(verts)
                if name.startswith("helper-"):
                    self.all_helper_verts.extend(verts)
                if self.helpers == "MASK":
                    if name == "body" or self.detailedHelpers:
                        vgroup = self.obj.vertex_groups.new(name=name)
                        vgroup.add(verts, 1.0, 'ADD')

        if self.helpers == "DELETE":
            if len(self.all_joint_verts) > 0:
                # TODO: delete vertices
                pass
            if len(self.all_helper_verts) > 0:
                # TODO: delete vertices
                pass
        else:
            vgroup = self.obj.vertex_groups.new(name="HelperGeometry")
            vgroup.add(self.all_helper_verts, 1.0, 'ADD')
            vgroup = self.obj.vertex_groups.new(name="JointCubes")
            vgroup.add(self.all_joint_verts, 1.0, 'ADD')

        if self.helpers == "MASK":
            mask = self.obj.modifiers.new("Mask", 'MASK')
            mask.vertex_group = "body"
            mask.show_in_editmode = True
            mask.show_on_cage = True

    def _faceListToVertSet(self, faceList):
        vertList = []
        for faceIdx in list(faceList):
            if faceIdx >= len(self.faceVertIndexes):
                print("WARNING: face index " + str(faceIdx) + " > " + str(len(self.faceVertIndexes)))
            else:
                vertList.extend( self.faceVertIndexes[faceIdx] )
        return set(vertList)

    def maskBody(self):

        allVisibleFaces = []

        for facelist in self.bodyInfo["faceMask"]:
            first = facelist[0]
            last = facelist[1]
            allVisibleFaces.extend( list(range(first,last+1)) )

        allVisibleFaces = set(allVisibleFaces)
        allMetaFaces = set(self.all_meta_faces)

        allVisibleVerts = list(self._faceListToVertSet(allVisibleFaces))
        allMetaVerts = list(self._faceListToVertSet(allMetaFaces))

        allVerts = set( range(0, len(self.vertCache)) )

        # TODO:   This approach may cause single vertex outliers. At some point it might make sense
        # TODO:   to find and exclude these
        allInvisibleVerts = list(allVerts - set(allVisibleVerts) - set(allMetaVerts))

        vgroupInvis = self.obj.vertex_groups.new(name="delete")
        vgroupInvis.add(allInvisibleVerts, 1.0, 'ADD')

        mask = self.obj.modifiers.new("Hide faces", 'MASK')
        mask.vertex_group = "delete"
        mask.show_in_editmode = True
        mask.show_on_cage = True
        mask.invert_vertex_group = True

    def afterMeshData(self):

        bmesh.ops.recalc_face_normals(self.bm, faces=self.bm.faces)

        self.bm.to_mesh(self.mesh)
        self.bm.free()
        self.handleHelpers()
        self.maskBody()

        del self.vertCache
        del self.faceCache
        del self.texco

        FetchServerData('getBodyMaterialInfo',self.gotBodyMaterialInfo)

    def gotBodyMaterialInfo(self, data):
        matname = data["name"]

        if self.prefixMaterial:
            matname = self.name + "." + matname

        mat = createMHMaterial(matname, data, ifExists=self.handleMaterials)
        self.obj.data.materials.append(mat)

        FetchServerData('getSkeleton', self.gotSkeleton)

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

        bone.head = vHead
        bone.tail = vTail

        if not parentBone is None:
            bone.parent = parentBone

        if "matrix" in boneInfo.keys():
            boneMatrix = Matrix(boneInfo["matrix"])
            normalizedMatrix = Matrix((boneMatrix[0], -boneMatrix[2], boneMatrix[1])).to_3x3().to_4x4()
            normalizedMatrix.col[3] = bone.matrix.col[3]
            bone.matrix = normalizedMatrix
        else:
            if "roll" in boneInfo.keys():
                bone.roll = boneInfo["roll"]

        for child in boneInfo["children"]:
            self._addBone(child, bone)

    def gotSkeleton(self, data):

        if data["name"] != "none" and len(data["bones"]) > 0:
            self._deselectAll()

            self.armature = bpy.data.armatures.new(self.name + "Armature")
            self.armatureObject = bpy.data.objects.new(self.name, self.armature)
            self.armatureObject.MhObjectType = "Skeleton"

            scene = bpy.context.scene
            scene.objects.link(self.armatureObject)
            scene.objects.active = self.armatureObject

            bpy.ops.object.mode_set(mode='EDIT', toggle=False)

            self.skeletonOffset = data["offset"]

            for boneInfo in data["bones"]:
                self._addBone(boneInfo)

            bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

            self.obj.parent = self.armatureObject

            modifier = self.obj.modifiers.new("Armature", 'ARMATURE')
            modifier.object = self.armatureObject

            if self.helpers == "MASK":
                scene.objects.active = self.obj
                bpy.ops.object.modifier_move_up(modifier="Armature")

        FetchServerData('getProxiesInfo', self.gotProxiesInfo)

    def gotProxiesInfo(self, data):
        self.proxiesInfo = data
        self.proxiesToImport = data
        self.nextProxyToImport = 0
        self.importNextProxy()

    def importNextProxy(self):
        if self.nextProxyToImport >= len(self.proxiesToImport):
            self.afterProxiesImported()
            return

        if self.importWhat == "EVERYTHING":
            ImportProxyBinary(self.obj, self.name, self.proxiesInfo[self.nextProxyToImport], self.proxyLoaded)

        if self.importWhat == "BODYPARTS":
            info = self.proxiesInfo[self.nextProxyToImport]
            type = info["type"]
            if type == "Clothes":
                print("Skipping proxy " + info[
                    "name"] + " because it is of type clothes, and only bodyparts are requested for load")
                self.nextProxyToImport = self.nextProxyToImport + 1
                self.importNextProxy()
                return
            else:
                ImportProxyBinary(self.obj, self.name, info, self.proxyLoaded)

        if self.importWhat == "BODY":
            self.afterProxiesImported()

    def proxyLoaded(self, proxy):

        if proxy.obj.MhObjectType == "Proxymeshes":
            self.hasProxy = True

        self.importedProxies.append(proxy)

        if self.armatureObject is None:
            proxy.obj.parent = self.obj
        else:
            proxy.obj.parent = self.armatureObject
            modifier = proxy.obj.modifiers.new("Armature", 'ARMATURE')
            modifier.object = self.armatureObject

        self.nextProxyToImport = self.nextProxyToImport + 1
        self.importNextProxy()

    def afterProxiesImported(self):
        print("All proxies imported")
        if not self.armatureObject is None:
            self.nextProxyToWeight = 0
            ImportWeighting(self.obj, onFinished=self.weightNextProxy)
        else:
            print("No armature object, skipping weighting")
            self.finalize()

    def weightNextProxy(self):

        if len(self.importedProxies) < 1:
            self.finalize()
            return;

        if self.nextProxyToWeight < len(self.importedProxies):
            proxy = self.importedProxies[self.nextProxyToWeight]
            self.nextProxyToWeight = self.nextProxyToWeight + 1
            ImportWeighting(proxy.obj, onFinished=self.weightNextProxy)
        else:
            self.finalize()


    def finalize(self):

        self._deselectAll()

        if self.hasProxy and bpy.context.scene.MhMaskBase:
            mask = self.obj.modifiers.new("Hide base mesh", 'MASK')
            mask.vertex_group = "body"
            mask.show_in_editmode = True
            mask.show_on_cage = True
            mask.invert_vertex_group = True

        if self.armatureObject is None:
            self.obj.select = True
        else:
            self.armatureObject.select = True

        if self.subdiv:
            subdiv = self.obj.modifiers.new("Subdivision", 'SUBSURF')
            subdiv.levels = 0
            subdiv.render_levels = 2
            for proxy in self.importedProxies:
                subdiv = proxy.obj.modifiers.new("Subdivision", 'SUBSURF')
                subdiv.levels = 0
                subdiv.render_levels = 2

        print("DONE!")

