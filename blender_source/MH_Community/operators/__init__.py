#!/usr/bin/python
# -*- coding: utf-8 -*-


from .actionjitterreducer import MHC_OT_ActionJitterReducerOperator
from .actiontrimleft import MHC_OT_ActionTrimLeftOperator
from .actiontrimright import MHC_OT_ActionTrimRightOperator
from .amputateface import MHC_OT_AmputateFaceOperator
from .amputatefingers import MHC_OT_AmputateFingersOperator
from .bodyimport import MHC_OT_BodyImportOperator
from .expressiontrans import MHC_OT_ExpressionTransOperator
from .kinectassignment import MHC_OT_KinectAssignmentOperator
from .kinectrefresh import MHC_OT_KinectRefreshOperator
from .meshsync import MHC_OT_MeshSyncOperator
from .poseright import MHC_OT_PoseRightOperator
from .posesync import MHC_OT_PoseSyncOperator
from .removefingerrig import MHC_OT_RemoveFingerRigOperator
from .removeikrig import MHC_OT_RemoveIkRigOperator
from .separateeyes import MHC_OT_SeparateEyesOperator
from .snaponfingerrig import MHC_OT_SnapOnFingerRigOperator
from .snaponikrig import MHC_OT_SnapOnIkRigOperator
from .startkinectrecording import MHC_OT_StartKinectRecordingOperator
from .stopkinectrecording import MHC_OT_StopKinectRecordingOperator
from .tokinect2 import MHC_OT_ToKinect2Operator

OPERATOR_CLASSES = (
    MHC_OT_ActionJitterReducerOperator,
    MHC_OT_ActionTrimLeftOperator,
    MHC_OT_ActionTrimRightOperator,
    MHC_OT_AmputateFaceOperator,
    MHC_OT_AmputateFingersOperator,
    MHC_OT_BodyImportOperator,
    MHC_OT_ExpressionTransOperator,
    MHC_OT_KinectAssignmentOperator,
    MHC_OT_KinectRefreshOperator,
    MHC_OT_MeshSyncOperator,
    MHC_OT_PoseRightOperator,
    MHC_OT_PoseSyncOperator,
    MHC_OT_RemoveFingerRigOperator,
    MHC_OT_RemoveIkRigOperator,
    MHC_OT_SeparateEyesOperator,
    MHC_OT_SnapOnFingerRigOperator,
    MHC_OT_SnapOnIkRigOperator,
    MHC_OT_StartKinectRecordingOperator,
    MHC_OT_StopKinectRecordingOperator,
    MHC_OT_ToKinect2Operator
)

__all__ = [
    'MHC_OT_ActionJitterReducerOperator',
    'MHC_OT_ActionTrimLeftOperator',
    'MHC_OT_ActionTrimRightOperator',
    'MHC_OT_AmputateFaceOperator',
    'MHC_OT_AmputateFingersOperator',
    'MHC_OT_BodyImportOperator',
    'MHC_OT_ExpressionTransOperator',
    'MHC_OT_KinectAssignmentOperator',
    'MHC_OT_KinectRefreshOperator',
    'MHC_OT_MeshSyncOperator',
    'MHC_OT_PoseRightOperator',
    'MHC_OT_PoseSyncOperator',
    'MHC_OT_RemoveFingerRigOperator',
    'MHC_OT_RemoveIkRigOperator',
    'MHC_OT_SeparateEyesOperator',
    'MHC_OT_SnapOnFingerRigOperator',
    'MHC_OT_SnapOnIkRigOperator',
    'MHC_OT_StartKinectRecordingOperator',
    'MHC_OT_StopKinectRecordingOperator',
    'MHC_OT_ToKinect2Operator',
    'OPERATOR_CLASSES'
]
