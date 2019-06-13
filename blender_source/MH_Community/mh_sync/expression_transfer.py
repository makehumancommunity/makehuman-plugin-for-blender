#!/usr/bin/python
# -*- coding: utf-8 -*-

bl_info = {
    "name": "Transfer MakeHuman expressions",
    "category": "Armature",
}

from .directory_ops import GetUserDir, GetSysDir
from .sync_pose import SyncPose
from .shapes_from_pose import shapesFromPose

import bpy
from json import load
import os
import time

class ExpressionTransfer():
    def __init__(self, operator, skeleton, toShapeKeys, exprFilter):
        self.operator = operator
        self.skeleton = skeleton
        self.toShapeKeys = toShapeKeys
        self.exprFilter = exprFilter

        if not self.toShapeKeys:
            self.frameNum = len(self.skeleton.pose_library.pose_markers)
        GetUserDir(self.UserDirReady)

    def UserDirReady(self, dir):
        self.processDirectory(dir)
        GetSysDir(self.SysDirReady)

    def SysDirReady(self, dir):
        self.processDirectory(dir)

    # get the full path file names of expressions, so that they may be passed
    # to later calls to sync pose
    def processDirectory(self, baseDir):
        expDirectory = os.path.normpath(os.path.join(baseDir, "data/expressions"))
        print("dir:" + expDirectory)
        sp = SyncPose()
        hadWarnings = False

        # go through all in  dir to get filename to pass & name to assign to pose
        didSomething = False
        for fileName in os.listdir(expDirectory):
            start = time.time()
            filepath = os.path.join(expDirectory, fileName)
            # make sure this is not a .thumb file
            if ".mhpose" not in filepath:
                continue

            with open(filepath, "rU") as file:
                expr_data = load(file)
                name = expr_data["name"]

                if self.exprFilter is not "":
                    tagFound = False
                    for key in expr_data["tags"]:
                        if key.lower() == self.exprFilter:
                            tagFound = True
                            break

                    if not tagFound:
                        continue

                sp.process(filepath, True)
                if self.toShapeKeys:
                    hadWarnings |= shapesFromPose(self.operator, self.skeleton, name)
                else:
                    self.frameNum += 1
                    bpy.ops.poselib.pose_add(frame=self.frameNum, name=name)
                    
                complete = time.time()

                totalTime    = '%4f' % (complete - start)
                mhTime       = '%4f' % (sp.startCallBack - start)
                callbackTime = '%4f' % (sp.callBackComplete - sp.startCallBack)
                saveTime     = '%4f' % (complete - sp.callBackComplete)
                print('total time:  ' + totalTime + ', makehuman:  ' + mhTime + ', callback:  ' + callbackTime + ', save:  ' + saveTime)
                
                didSomething = True

        # write out one last warning, so it shows at bottom
        if hadWarnings: self.operator.report({'WARNING'}, 'Some meshes had to be excluded, since their current modifiers change the number of vertices')
        
        # change back to rest pose; since did something know we are in pose mode
        if didSomething:
            bpy.ops.pose.select_all(action='SELECT')
            bpy.ops.pose.transforms_clear()
