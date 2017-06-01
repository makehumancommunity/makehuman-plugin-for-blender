#!/usr/bin/python
# -*- coding: utf-8 -*-

bl_info = {
    "name": "Synchronize MakeHuman mesh",
    "category": "Mesh",
}

from .sync_ops import SyncOperator

import bpy
import pprint

pp = pprint.PrettyPrinter(indent=4)

class SyncMesh(SyncOperator):
    def __init__(self):
        super().__init__('getCoord')
        self.executeJsonCall()

    def callback(self,json_obj):

        print("Update mesh")

        obj = bpy.context.active_object
        print(type(json_obj))
        data = json_obj.data
        l = len(data)
        print("Length of vertex array in incoming data: " + str(l))
        l2 = len(obj.data.vertices)
        print("Length of vertex array in selected object: " + str(l2))

        i = 0

        while i < l and i < l2:
            obj.data.vertices[i].co[0] = data[i][0]
            obj.data.vertices[i].co[1] = -data[i][2]
            obj.data.vertices[i].co[2] = data[i][1]
            i = i + 1
