#!/usr/bin/python
# -*- coding: utf-8 -*-

bl_info = {
    "name": "Synchronize MakeHuman mesh",
    "category": "Mesh",
}

import bpy
import json
import pprint
import socket

pp = pprint.PrettyPrinter(indent=4)

class SyncMHMeshOperator(bpy.types.Operator):
    """Synchronize the shape of a human with MH"""
    bl_idname = "mesh.sync_mh_mesh"
    bl_label = "Synchronize MH Mesh"
    bl_options = {'REGISTER', 'UNDO'}

    def executeJsonCall(self,jsoncall):
        
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(('127.0.0.1', 12345))
        client.send(jsoncall)
     
        data = ""
    
        while True:
            buf = client.recv(1024)
            if len(buf) > 0:
                data += buf.strip().decode('utf-8')
            else:
                break
    
        return data;

    def updateMesh(self,json_obj):

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

    def execute(self, context):
        print("Execute syncmesh")
        
        obj = context.object
        if obj is None or not obj.type == 'MESH':
            self.report({'ERROR'}, "Must select mesh to synchronize")
        else:
            #self.dumpObj()
            json_raw = self.executeJsonCall(b'getCoord')
            #with open("/tmp/json.json","w") as jfile:
            #    jfile.write(json_raw)
            json_obj = json.loads(json_raw)
            self.updateMesh(json_obj)

        return {'FINISHED'} 
