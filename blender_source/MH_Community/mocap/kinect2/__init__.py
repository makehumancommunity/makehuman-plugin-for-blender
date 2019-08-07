if "bpy" in locals():
    print("Reloading kinect Sensor plug-in")
    import imp
    imp.reload(kinect2_sensor)
else:
    print("Loading kinect Sensor plug-in")
    from . import kinect2_sensor

import bpy
print("kinect Sensor plug-in loaded")