#!/usr/bin/python
# -*- coding: utf-8 -*-


from .actionjitterreducer import ActionJitterReducerOperator
from .actiontrimleft import ActionTrimLeftOperator
from .actiontrimright import ActionTrimRightOperator
from .amputateface import AmputateFaceOperator
from .amputatefingers import AmputateFingersOperator
from .bodyimport import BodyImportOperator
from .expressiontrans import ExpressionTransOperator
from .kinectassignment import KinectAssignmentOperator
from .kinectrefresh import KinectRefreshOperator
from .meshsync import MeshSyncOperator
from .poseright import PoseRightOperator
from .posesync import PoseSyncOperator
from .removefingerrig import RemoveFingerRigOperator
from .removeikrig import RemoveIkRigOperator
from .separateeyes import SeparateEyesOperator
from .snaponfingerrig import SnapOnFingerRigOperator
from .snaponikrig import SnapOnIkRigOperator
from .startkinectrecording import StartKinectRecordingOperator
from .stopkinectrecording import StopKinectRecordingOperator
from .tokinect2 import ToKinect2Operator

OPERATOR_CLASSES = (
    ActionJitterReducerOperator,
    ActionTrimLeftOperator,
    ActionTrimRightOperator,
    AmputateFaceOperator,
    AmputateFingersOperator,
    BodyImportOperator,
    ExpressionTransOperator,
    KinectAssignmentOperator,
    KinectRefreshOperator,
    MeshSyncOperator,
    PoseRightOperator,
    PoseSyncOperator,
    RemoveFingerRigOperator,
    RemoveIkRigOperator,
    SeparateEyesOperator,
    SnapOnFingerRigOperator,
    SnapOnIkRigOperator,
    StartKinectRecordingOperator,
    StopKinectRecordingOperator,
    ToKinect2Operator
)

__all__ = [
    'ActionJitterReducerOperator',
    'ActionTrimLeftOperator',
    'ActionTrimRightOperator',
    'AmputateFaceOperator',
    'AmputateFingersOperator',
    'BodyImportOperator',
    'ExpressionTransOperator',
    'KinectAssignmentOperator',
    'KinectRefreshOperator',
    'MeshSyncOperator',
    'PoseRightOperator',
    'PoseSyncOperator',
    'RemoveFingerRigOperator',
    'RemoveIkRigOperator',
    'SeparateEyesOperator',
    'SnapOnFingerRigOperator',
    'SnapOnIkRigOperator',
    'StartKinectRecordingOperator',
    'StopKinectRecordingOperator',
    'ToKinect2Operator',
    'OPERATOR_CLASSES'
]
