#!/usr/bin/python
# -*- coding: utf-8 -*-

bl_info = {
    "name": "Get MH directories"
}

from .sync_ops import SyncOperator

import bpy

class GetUserDir(SyncOperator):
    def __init__(self, readyFunction):
        super().__init__('getUserDir')
        self.readyFunction = readyFunction
        self.executeJsonCall()

    def callback(self,json_obj):
        self.readyFunction(json_obj.data)
                
class GetSysDir(SyncOperator):
    def __init__(self, readyFunction):
        super().__init__('getSysDir')
        self.readyFunction = readyFunction
        self.executeJsonCall()

    def callback(self,json_obj):
        self.readyFunction(json_obj.data)