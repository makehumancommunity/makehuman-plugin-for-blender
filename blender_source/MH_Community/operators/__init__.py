#!/usr/bin/python
# -*- coding: utf-8 -*-


from .actionkeyframereducer import MHC_OT_ActionKeyframeReducerOperator
from .actiontrimleft import MHC_OT_ActionTrimLeftOperator
from .actiontrimright import MHC_OT_ActionTrimRightOperator
from .amputateface import MHC_OT_AmputateFaceOperator
from .amputatefingers import MHC_OT_AmputateFingersOperator
from .bodyimport import MHC_OT_BodyImportOperator
from .expressiontrans import MHC_OT_ExpressionTransOperator
from .mocapassignment import MHC_OT_MocapAssignmentOperator
from .mocaprefresh import MHC_OT_MocapRefreshOperator
from .meshsync import MHC_OT_MeshSyncOperator
from .poseright import MHC_OT_PoseRightOperator
from .posesync import MHC_OT_PoseSyncOperator
from .removefingerrig import MHC_OT_RemoveFingerRigOperator
from .removeikrig import MHC_OT_RemoveIkRigOperator
from .separateeyes import MHC_OT_SeparateEyesOperator
from .snaponfingerrig import MHC_OT_SnapOnFingerRigOperator
from .snaponikrig import MHC_OT_SnapOnIkRigOperator
from .startmocaprecording import MHC_OT_StartMocapRecordingOperator
from .stopmocaprecording import MHC_OT_StopMocapRecordingOperator
from .toSensorRig import MHC_OT_ToSensorRigOperator
from .loadpreset import MHC_OT_LoadPresetOperator
from .savepreset import MHC_OT_SavePresetOperator

OPERATOR_CLASSES = (
    MHC_OT_ActionKeyframeReducerOperator,
    MHC_OT_ActionTrimLeftOperator,
    MHC_OT_ActionTrimRightOperator,
    MHC_OT_AmputateFaceOperator,
    MHC_OT_AmputateFingersOperator,
    MHC_OT_BodyImportOperator,
    MHC_OT_ExpressionTransOperator,
    MHC_OT_MocapAssignmentOperator,
    MHC_OT_MocapRefreshOperator,
    MHC_OT_MeshSyncOperator,
    MHC_OT_PoseRightOperator,
    MHC_OT_PoseSyncOperator,
    MHC_OT_RemoveFingerRigOperator,
    MHC_OT_RemoveIkRigOperator,
    MHC_OT_SeparateEyesOperator,
    MHC_OT_SnapOnFingerRigOperator,
    MHC_OT_SnapOnIkRigOperator,
    MHC_OT_StartMocapRecordingOperator,
    MHC_OT_StopMocapRecordingOperator,
    MHC_OT_ToSensorRigOperator,
    MHC_OT_LoadPresetOperator,
    MHC_OT_SavePresetOperator
)

__all__ = [
    'MHC_OT_ActionKeyframeReducerOperator',
    'MHC_OT_ActionTrimLeftOperator',
    'MHC_OT_ActionTrimRightOperator',
    'MHC_OT_AmputateFaceOperator',
    'MHC_OT_AmputateFingersOperator',
    'MHC_OT_BodyImportOperator',
    'MHC_OT_ExpressionTransOperator',
    'MHC_OT_MocapAssignmentOperator',
    'MHC_OT_MocapRefreshOperator',
    'MHC_OT_MeshSyncOperator',
    'MHC_OT_PoseRightOperator',
    'MHC_OT_PoseSyncOperator',
    'MHC_OT_RemoveFingerRigOperator',
    'MHC_OT_RemoveIkRigOperator',
    'MHC_OT_SeparateEyesOperator',
    'MHC_OT_SnapOnFingerRigOperator',
    'MHC_OT_SnapOnIkRigOperator',
    'MHC_OT_StartMocapRecordingOperator',
    'MHC_OT_StopMocapRecordingOperator',
    'MHC_OT_ToSensorRigOperator',
    'MHC_OT_LoadPresetOperator',
    'MHC_OT_SavePresetOperator',
    'OPERATOR_CLASSES'
]
