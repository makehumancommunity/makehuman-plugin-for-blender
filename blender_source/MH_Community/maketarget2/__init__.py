#!/usr/bin/python
# -*- coding: utf-8 -*-

#  Author: Joel Palmius

import bpy
from bpy.props import BoolProperty, StringProperty, EnumProperty, IntProperty, CollectionProperty, FloatProperty

bpy.types.Scene.MhPrimaryTargetName = StringProperty(name='Target filename', description='Target file name, relative to the custom targets directory', default='')

from .maketarget2 import MHC_PT_MakeTarget_Panel

from .createprimarytarget import MHC_OT_CreatePrimaryTargetOperator
from .printprimarytarget import MHC_OT_PrintPrimaryTargetOperator
from .saveprimarytarget import MHC_OT_SavePrimaryTargetOperator

MAKETARGET2_CLASSES = [
    MHC_OT_CreatePrimaryTargetOperator,
    MHC_OT_PrintPrimaryTargetOperator,
    MHC_OT_SavePrimaryTargetOperator,
    MHC_PT_MakeTarget_Panel
]

__all__ = [
    "MHC_OT_CreatePrimaryTargetOperator",
    "MHC_OT_PrintPrimaryTargetOperator",
    "MHC_OT_SavePrimaryTargetOperator",
    "MHC_PT_MakeTarget_Panel",
    "MAKETARGET2_CLASSES"
]

