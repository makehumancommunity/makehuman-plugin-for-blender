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

class ExpressionTransfer():
    def __init__(self, operator, skeleton, toShapeKeys, exprFilter):
        self.operator = operator
        self.skeleton = skeleton
        self.toShapeKeys = toShapeKeys
        self.exprFilter = exprFilter

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

        # go through all in  dir to get filename to pass & name to assign to pose
        for fileName in os.listdir(expDirectory):
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

                SyncPose(filepath, True)
                if self.toShapeKeys:
                    shapesFromPose(self.operator, self.skeleton, name)
                else:
                    self.frameNum += 1
                    bpy.ops.poselib.pose_add(frame=self.frameNum, name=name)