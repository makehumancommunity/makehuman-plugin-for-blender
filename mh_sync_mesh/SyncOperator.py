#!/usr/bin/python
# -*- coding: utf-8 -*-

import bpy
import json
import pprint
import socket

pp = pprint.PrettyPrinter(indent=4)

class SyncOperator(bpy.types.Operator):
    def __init__(self, operator):
        self.operator = operator

    def executeJsonCall(self):     
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(('127.0.0.1', 12345))
        client.send(bytes(self.operator, 'utf-8'))
     
        data = ""
    
        while True:
            buf = client.recv(1024)
            if len(buf) > 0:
                data += buf.strip().decode('utf-8')
            else:
                break
    
        return data;

    def callback(self,json_obj):
        raise Exception('needs to be overridden by subclass')

    def execute(self, context):
        print("Execute " + self.operator)
        
        obj = context.object

        json_raw = self.executeJsonCall()
        #with open("/tmp/json.json","w") as jfile:
        #    jfile.write(json_raw)
        
        if "!!!" not in json_raw:
            json_obj = json.loads(json_raw)
            self.callback(json_obj)
            
        else:
            print(json_raw)
            raise Exception(json_raw)       

        return {'FINISHED'} 