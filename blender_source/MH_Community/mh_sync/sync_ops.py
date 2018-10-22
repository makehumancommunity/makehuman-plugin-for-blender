#!/usr/bin/python
# -*- coding: utf-8 -*-

import bpy
import json

from .JsonCall import JsonCall

class SyncOperator:
    def __init__(self, operator):
        self.call = JsonCall();
        self.call.setFunction(operator)

    def executeJsonCall(self, expectBinaryResponse=False, params=None):
        if not params is None:
            self.call.params = params
        json_obj = self.call.send(expectBinaryResponse=expectBinaryResponse)
        self.callback(json_obj)

    def callback(self,json_obj):
        raise Exception('needs to be overridden by subclass')
    