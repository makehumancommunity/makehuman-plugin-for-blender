if "bpy" in locals():
    print("Reloading kinect Sensor plug-in")
    import imp
    imp.reload(animation_buffer)
    imp.reload(calibrate_armature)
    imp.reload(capture_armature)
    imp.reload(empties)
    imp.reload(jitter_reduction)
    imp.reload(kinect2_runtime)
    imp.reload(kinect_ui)
    imp.reload(to_kinect2)
else:
    print("Loading kinect Sensor plug-in")
    from . import animation_buffer
    from . import calibrate_armature
    from . import capture_armature
    from . import empties
    from . import jitter_reduction
    from . import kinect2_runtime
    from . import kinect_ui
    from . import to_kinect2

import bpy
print("kinect Sensor plug-in loaded")