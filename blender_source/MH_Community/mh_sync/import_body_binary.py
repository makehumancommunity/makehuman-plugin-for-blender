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
import numpy as np

from mathutils import Matrix, Vector
from .material import *
from .fetch_server_data import FetchServerData
from .import_proxy_binary import ImportProxyBinary
from .import_weighting import ImportWeighting
from ..util import *
from .meshutils import *

pp = pprint.PrettyPrinter(indent=4)

ENABLE_PROFILING_OUTPUT = True

class ImportBodyBinary():

    def __init__(self):
        print("Import body")

        self.name = "human"

        self.armature = None
        self.armatureObject = None
        self.hasProxy = False
        self.scaleFactor = 0.1
        self.groundMean = 0.0

        self.startMillis = int(round(time.time() * 1000))
        self.lastMillis = self.startMillis

        self.scaleMode = str(bpy.context.scene.MhScaleMode)
        self.handleMaterials = str(bpy.context.scene.MhHandleMaterials)
        self.prefixMaterial = bpy.context.scene.MhPrefixMaterial
        self.importWhat = str(bpy.context.scene.MhImportWhat)
        self.helpers = str(bpy.context.scene.MhHandleHelper)
        self.subdiv = bpy.context.scene.MhAddSubdiv
        self.matobjname = bpy.context.scene.MhMaterialObjectName
        self.importRig = bpy.context.scene.MhImportRig
        self.detailedHelpers = bpy.context.scene.MhDetailedHelpers
        self.rigisparent = bpy.context.scene.MhRigIsParent
        self.adjust = bpy.context.scene.MhAdjustPosition
        self.addCollection = bpy.context.scene.MhAddCollection
        self.defaultSkinColor = (1.0, 0.7, 0.7, 1.0)
        self.hiddenFaces = bpy.context.scene.MhHiddenFaces
        self.subCollection = bpy.context.scene.MhSubCollection

        self.baseColor = (1.0, 0.7, 0.7)

        self.all_joint_verts = []
        self.all_helper_verts = []
        self.all_meta_faces = []

        self.left_verts = []
        self.right_verts = []
        self.mid_verts = []

        self.vertPosCache = None

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
        self.obj = bpy.data.objects.new(self.name + ".Body", self.mesh)

        self.obj.MhHuman = True
        self.obj.MhObjectType = "Basemesh"

        # TODO: Set more info, for example name of toon

        self.collection = None
        if self.addCollection and bl28():
            self.collection = bpy.data.collections.new(self.name)
            if self.subCollection:
                bpy.context.collection.children.link(self.collection)
                bpy.context.collection.hide_select = False
                bpy.context.collection.hide_render = False
                bpy.context.collection.hide_viewport = False
                # TODO:      Unfortunately, these three are not enough to avoid the crash that
                # TODO:      happens when a collection is hidden in the viewport. Apparently
                # TODO:      something more needs to be done to show the collection, but
                # TODO:      at this point I don't know what
            else:
                bpy.context.scene.collection.children.link(self.collection)
            self.collection.hide_select = False
            self.collection.hide_render = False
            self.collection.hide_viewport = False

        linkObject(self.obj, self.collection)
        activateObject(self.obj)
        selectObject(self.obj)

        self.skinColor = data.get('skinColor', self.defaultSkinColor)

        if len(self.skinColor) == 3:
            self.skinColor.append(1.0)

        self.mesh = bpy.context.object.data
        self.bm = bmesh.new()

        self._profile("gotBodyInfo")
        FetchServerData('getBodyVerticesBinary',self.gotVerticesData,True)


    def gotVerticesData(self, data):
        self.vertCache = []

        shape = self.bodyInfo["verticesShape"]
        typeCode = self.bodyInfo["verticesTypeCode"]
        numpyMesh = convertBufferToShapedNumpyArray(data, typeCode, shape, self.scaleFactor)

        iMax = len(numpyMesh)
        assert(iMax == int(self.bodyInfo["numVertices"]))

        self.vertPosCache = np.zeros(numpyMesh.shape, numpyMesh.dtype)

        addNumpyArrayAsVerts(self.bm, numpyMesh, self.vertCache, self.vertPosCache)

        for i in range(iMax):
            if numpyMesh[i][1] < self.minimumZ:
                self.minimumZ = numpyMesh[i][1]

        self._profile("gotVerticesData")
        FetchServerData('getBodyFacesBinary',self.gotFacesData,True)


    def gotFacesData(self, data):
        self.faceCache = []

        shape = self.bodyInfo["facesShape"]
        typeCode = self.bodyInfo["facesTypeCode"]
        numpyMesh = convertBufferToShapedNumpyArray(data, typeCode, shape)

        iMax = len(numpyMesh)
        assert(iMax == int(self.bodyInfo["numFaces"]))

        self.faceVertIndexes = numpyMesh.tolist()

        addNumpyArrayAsFaces(self.bm, numpyMesh, self.vertCache, faceCache=self.faceCache, smooth=True)

        self._profile("gotFacesData")
        FetchServerData('getBodyTextureCoordsBinary', self.gotTextureCoords, True)

    def gotTextureCoords(self, data):

        shape = self.bodyInfo["textureCoordsShape"]
        typeCode = self.bodyInfo["textureCoordsTypeCode"]
        numpyMesh = convertBufferToShapedNumpyArray(data, typeCode, shape)

        iMax = len(numpyMesh)
        assert (iMax == int(self.bodyInfo["numTextureCoords"]))

        self.texco = numpyMesh

        self._profile("gotTextureCoords")
        FetchServerData('getBodyFaceUVMappingsBinary', self.gotFaceUVMappings, True)

    def gotFaceUVMappings(self, data):

        shape = self.bodyInfo["faceUVMappingsShape"]
        typeCode = self.bodyInfo["faceUVMappingsTypeCode"]
        numpyMesh = convertBufferToShapedNumpyArray(data, typeCode, shape)

        iMax = len(numpyMesh)
        assert (iMax == int(self.bodyInfo["numFaceUVMappings"]))

        faceTexco = np.zeros((iMax, 4, 2), self.texco.dtype)

        for i in range(iMax):
            stride = 0
            while stride < 4:
                idx = numpyMesh[i][stride]
                faceTexco[i][stride] = self.texco[int(idx)]
                stride = stride + 1

        uv_layer = self.bm.loops.layers.uv.verify()

        if not bl28():
            # TODO: There's probably some way to do this in blender 2.8 too
            self.bm.faces.layers.tex.verify()

        for face in self.bm.faces:
            for i, loop in enumerate(face.loops):
                uv = loop[uv_layer].uv
                texco = faceTexco[face.index][i]
                uv[0] = texco[0]
                uv[1] = texco[1]

        self._profile("gotFaceUVMappings")
        self.afterMeshData()

    def handleHelpers(self):
        self._profile()
        for fg in self.bodyInfo["faceGroups"]:
            name = fg["name"]
            #self._profile(name)
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
                    if name == "joint-ground":
                        sum = 0.0
                        for v in verts:
                            sum = sum + self.vertPosCache[v][2]
                        self.groundMean = sum / 8.0
                        print("GROUND MEAN: " + str(self.groundMean))

                if name.startswith("helper-"):
                    self.all_helper_verts.extend(verts)
                if self.helpers == "MASK":
                    if name == "body" or self.detailedHelpers:
                        vgroup = self.obj.vertex_groups.new(name=name)
                        vgroup.add(verts, 1.0, 'ADD')
                    else:
                        if self.detailedHelpers and name.startswith("helper-"):
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


        if self.detailedHelpers:
            print("IS MAKECLOTHES")

            for i in range(len(self.vertPosCache)):
                vert = self.vertPosCache[i]
                x = vert[0]

                if x > -0.01 and x < 0.01:
                    self.mid_verts.append(i)
                else:
                    if x < 0.0:
                        self.right_verts.append(i)
                    if x > 0.0:
                        self.left_verts.append(i)


            if len(self.right_verts) > 0:
                vgroup = self.obj.vertex_groups.new(name="Right")
                vgroup.add(self.right_verts, 1.0, 'ADD')

            if len(self.left_verts) > 0:
                vgroup = self.obj.vertex_groups.new(name="Left")
                vgroup.add(self.left_verts, 1.0, 'ADD')

            if len(self.mid_verts) > 0:
                vgroup = self.obj.vertex_groups.new(name="Mid")
                vgroup.add(self.mid_verts, 1.0, 'ADD')

        if self.helpers == "MASK":
            mask = self.obj.modifiers.new("Toggle helper visibility", 'MASK')
            mask.vertex_group = "body"
            mask.show_in_editmode = True
            mask.show_on_cage = True

        self._profile("handleHelpers")

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

        vgroupInvis = self.obj.vertex_groups.new(name="Delete")
        vgroupInvis.add(allInvisibleVerts, 1.0, 'ADD')

        mask = self.obj.modifiers.new("Hide faces", 'MASK')
        mask.vertex_group = "Delete"
        mask.show_in_editmode = True
        mask.show_on_cage = True
        mask.invert_vertex_group = True

        self._profile("maskBody")

    def afterMeshData(self):
        self._profile()
        bmesh.ops.recalc_face_normals(self.bm, faces=self.bm.faces)

        self.bm.to_mesh(self.mesh)
        self.bm.free()
        self.handleHelpers()

        if self.hiddenFaces == "MASK":
            self.maskBody()
        # TODO: handle "MATERIAL" and "DELETE" too

        del self.vertCache
        del self.faceCache
        del self.texco
        del self.vertPosCache

        FetchServerData('getBodyMaterialInfo',self.gotBodyMaterialInfo)

    def gotBodyMaterialInfo(self, data):
        self._profile()
        matname = data["name"]

        if self.matobjname:
            matname = "body"

        if self.prefixMaterial:
            matname = self.name + "." + matname

        mat = createMHMaterial(matname, data, baseColor=self.skinColor, ifExists=self.handleMaterials)

        self.obj.data.materials.append(mat)

        self._profile("gotBodyMaterialInfo")

        if self.importRig:
            FetchServerData('getSkeleton', self.gotSkeleton)
        else:
            FetchServerData('getProxiesInfo', self.gotProxiesInfo)

    def _deselectAll(self):
        for ob in bpy.context.selected_objects:
            deselectObject(ob)

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

            linkObject(self.armatureObject, self.collection)
            activateObject(self.armatureObject)
            if bl28():
                self.armatureObject.data.display_type = 'WIRE'
                self.armatureObject.show_in_front = True
            else:
                self.armatureObject.data.draw_type = 'WIRE'
                self.armatureObject.show_x_ray = True

            bpy.ops.object.mode_set(mode='EDIT', toggle=False)

            self.skeletonOffset = data["offset"]

            for boneInfo in data["bones"]:
                self._addBone(boneInfo)

            bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

            if self.rigisparent:
                self.obj.parent = self.armatureObject
            else:
                self.armatureObject.parent = self.obj

            modifier = self.obj.modifiers.new("Armature", 'ARMATURE')
            modifier.object = self.armatureObject

            if self.helpers == "MASK":
                activateObject(self.obj)
                bpy.ops.object.modifier_move_up(modifier="Armature")

        self._profile("gotSkeleton")
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
            ImportProxyBinary(self.obj, self.name, self.proxiesInfo[self.nextProxyToImport], self.proxyLoaded, self.collection)

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
            if self.rigisparent:
                proxy.obj.parent = self.armatureObject
            else:
                proxy.obj.parent = self.obj
            modifier = proxy.obj.modifiers.new("Armature", 'ARMATURE')
            modifier.object = self.armatureObject

        self.nextProxyToImport = self.nextProxyToImport + 1
        self.importNextProxy()

    def afterProxiesImported(self):
        self._profile("afterProxiesImported")
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
            return

        if self.nextProxyToWeight < len(self.importedProxies):
            proxy = self.importedProxies[self.nextProxyToWeight]
            self.nextProxyToWeight = self.nextProxyToWeight + 1
            ImportWeighting(proxy.obj, onFinished=self.weightNextProxy)
        else:
            self.finalize()

        self._profile("weightNextProxy")


    def finalize(self):

        self._deselectAll()

        if self.hasProxy and bpy.context.scene.MhMaskBase:
            mask = self.obj.modifiers.new("Hide base mesh", 'MASK')
            mask.vertex_group = "body"
            mask.show_in_editmode = True
            mask.show_on_cage = True
            mask.invert_vertex_group = True

        self.objToAdjust = self.obj

        if self.armatureObject is None:
            selectObject(self.obj)
        else:
            selectObject(self.armatureObject)
            self.objToAdjust = self.armatureObject

        if self.adjust:
            self.objToAdjust.location.z = -self.groundMean

        print("SUBDIV")
        print(self.subdiv)
        print(type(self.subdiv))

        if self.subdiv:
            print("Adding subdiv")
            subdiv = self.obj.modifiers.new("Subdivision", 'SUBSURF')
            subdiv.levels = 0
            subdiv.render_levels = 2
            for proxy in self.importedProxies:
                subdiv = proxy.obj.modifiers.new("Subdivision", 'SUBSURF')
                subdiv.levels = 0
                subdiv.render_levels = 2

        print("DONE!")

