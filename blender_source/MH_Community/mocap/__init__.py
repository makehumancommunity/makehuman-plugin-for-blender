if "bpy" in locals():
    import imp
    imp.reload(kinect2)  # directory

    imp.reload(animation_buffer)
    imp.reload(capture_armature)
    imp.reload(empties)
    imp.reload(keyframe_reduction)
    imp.reload(mocap_ui)
else:
    from . import kinect2 # directory

    from . import animation_buffer
    from . import capture_armature
    from . import empties
    from . import keyframe_reduction
    from . import mocap_ui

import bpy