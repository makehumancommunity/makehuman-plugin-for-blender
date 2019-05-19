#!/usr/bin/python
# -*- coding: utf-8 -*-

#  Author: Joel Palmius

import bpy

from .maketarget2 import MHC_PT_MakeTarget_Panel

from .createprimarytarget import MHC_OT_CreatePrimaryTargetOperator
from .printprimarytarget import MHC_OT_PrintPrimaryTargetOperator

MAKETARGET2_CLASSES = [
    MHC_OT_CreatePrimaryTargetOperator,
    MHC_OT_PrintPrimaryTargetOperator,
    MHC_PT_MakeTarget_Panel
]

__all__ = [
    "MHC_OT_CreatePrimaryTargetOperator",
    "MHC_OT_PrintPrimaryTargetOperator",
    "MHC_PT_MakeTarget_Panel",
    "MAKETARGET2_CLASSES"
]

