#!/usr/bin/python
# -*- coding: utf-8 -*-

bl_info = {
    "name": "Synchronize MakeHuman mesh",
    "category": "Mesh",
}

from .SyncOperator import *

import bpy
import pprint

pp = pprint.PrettyPrinter(indent=4)

class SyncMHMeshOperator(SyncOperator):
    """Synchronize the shape of a human with MH"""
    bl_idname = "mesh.sync_mh_mesh"
    bl_label = "Synchronize MH Mesh"
    bl_options = {'REGISTER', 'UNDO'}

    def __init__(self):
        super().__init__('getCoord', 'MESH')

    def callback(self,json_obj):

        print("Update mesh")

        obj = bpy.context.active_object
        data = json_obj["data"]
        l = len(data)
        print(l)
        l2 = len(obj.data.vertices)
        print(l2)

        i = 0

        while i < l and i < l2:
            obj.data.vertices[i].co[0] = data[i][0]
            obj.data.vertices[i].co[1] = -data[i][2]
            obj.data.vertices[i].co[2] = data[i][1]
            i = i + 1

        
    #def dumpObj(self):
    #    print("Dump obj")

    #    obj = bpy.context.active_object

    #    with open("/tmp/blender.json","w") as bfile:
    #        bfile.write("{ \"data\": [\n")
    #        for v in obj.data.vertices:
    #            bfile.write("[ ")
    #            bfile.write("{0:.8f}".format(v.index))
    #            bfile.write(", ")
    #            bfile.write("{0:.8f}".format(v.co[0]))
    #            bfile.write(", ")
    #            bfile.write("{0:.8f}".format(v.co[2]))
    #            bfile.write(", ")
    #            bfile.write("{0:.8f}".format(v.co[1]))
    #            bfile.write(" ],\n")
    #        bfile.write("] } \n")
