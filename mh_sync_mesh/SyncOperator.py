#!/usr/bin/python
# -*- coding: utf-8 -*-

import bpy
import json

from .JsonCall import JsonCall

class SyncOperator(bpy.types.Operator):

    bl_label = "abstract operator"
    bl_idname = "mhsync.abstract"

    def __init__(self, operator):
        self.call = JsonCall();
        self.call.setFunction(operator)

    def executeJsonCall(self):     
        print("About to send json:\n\n" + self.call.serialize())
        return self.call.send()

    def callback(self,json_obj):
        raise Exception('needs to be overridden by subclass')

    def execute(self, context):
        print("Execute")
        
        obj = context.object

        json_obj = self.executeJsonCall()
        self.callback(json_obj)
        
        return {'FINISHED'} 
