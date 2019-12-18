from ..sensor_runtime import *

from struct      import calcsize # needed to figure out whether on 32 or 64 bit Blender
from ctypes      import cdll, c_char, c_char_p, c_void_p, CFUNCTYPE
from os          import path
from sys         import platform
#===============================================================================
#Dump of file KinectToJSON_x64.dll
#
#File Type: DLL
#
#  Section contains the following exports for KinectToJSON_x64.dll
#
#    00000000 characteristics
#    FFFFFFFF time date stamp
#        0.00 version
#           1 ordinal base
#           4 number of functions
#           4 number of names
#
#    ordinal hint RVA      name
#
#          1    0 000115D7 ?beginBodyTracking@@YAJP6AXPEAD@Z@Z = @ILT+1490(?beginBodyTracking@@YAJP6AXPEAD@Z@Z)
#          2    1 000114BA ?closeSensor@@YAXXZ = @ILT+1205(?closeSensor@@YAXXZ)
#          3    2 00011398 ?endBodyTracking@@YAXXZ = @ILT+915(?endBodyTracking@@YAXXZ)
#          4    3 0001109B ?openSensor@@YAJDDD@Z = @ILT+150(?openSensor@@YAJDDD@Z)

# ordinal seems to be alphabetical; calling by ordinal here
BEGIN_BODY_TRACKING = 1
CLOSE_SENSOR        = 2
END_BODY_TRACKING   = 3
OPEN_SENSOR         = 4

#===============================================================================
# all static class.
class Kinect2Sensor():
    DLL = None
    LOAD_EXCEPTION = None
    callback_func = None # cannot be a local var, or segfault

    JOINTS = {
        # keys are kinect joints names coming from the sensor
        # values are the "parent" joints
        'SpineBase'    : None,
        'SpineMid'     : 'SpineBase',
        'SpineShoulder': 'SpineMid',

        'Neck'         : 'SpineShoulder',
        'Head'         : 'Neck',

        'ShoulderLeft' : 'SpineShoulder',
        'ElbowLeft'    : 'ShoulderLeft',
        'WristLeft'    : 'ElbowLeft',
        'HandLeft'     : 'WristLeft',
        'HandTipLeft'  : 'HandLeft',
        'ThumbLeft'    : 'WristRight', # thumb works better with wrist parent than hand

        'ShoulderRight': 'SpineShoulder',
        'ElbowRight'   : 'ShoulderRight',
        'WristRight'   : 'ElbowRight',
        'HandRight'    : 'WristRight',
        'HandTipRight' : 'HandRight',
        'ThumbRight'   : 'WristRight',  # thumb works better with wrist parent than hand

        'HipLeft'      : 'SpineBase',
        'KneeLeft'     : 'HipLeft',
        'AnkleLeft'    : 'KneeLeft',
        'FootLeft'     : 'AnkleLeft',

        'HipRight'     : 'SpineBase',
        'KneeRight'    : 'HipRight',
        'AnkleRight'   : 'KneeRight',
        'FootRight'    : 'AnkleRight',
    }
    
    @staticmethod
    def getSensorInfo():
        ret = SensorInfo()
        ret.setJointDict(Kinect2Sensor.JOINTS)
        ret.setPelvisName('SpineBase')
        ret.setAnkleNames('AnkleLeft', 'AnkleRight')
        ret.setKneeNames ('KneeLeft' , 'KneeRight')
        ret.setWristNames('WristLeft', 'WristRight')
        ret.setElbowNames('ElbowLeft', 'ElbowRight')
        
        return ret

    @staticmethod
    def loadLibrary():
        # This is only performed once.  Subsequent calls just echo first test, so can be used in UI polling
        if Kinect2Sensor.LOAD_EXCEPTION is not None:
            return Kinect2Sensor.LOAD_EXCEPTION

        if Kinect2Sensor.DLL is not None:
             return None

        # Sensor only works on windows.  Keep Linux, others from erroring
        if platform != "win32" and platform != "win64":
            LOAD_EXCEPTION = 'Kinect2 only works on a Windows operating system.'
            return LOAD_EXCEPTION

        # actually try to load the dll, inside try block, in case they failed do to install Kinect runtime re-distributable
        try:
            is64Bit = calcsize("P") * 8 == 64  # using sys.platform is NOT reliable
            fileName = 'KinectToJSON_' + ('x64' if is64Bit else 'x86') + '.dll'
            moduleDirectory = path.dirname(__file__)
            filepath = path.join(moduleDirectory, fileName)
            Kinect2Sensor.DLL = cdll.LoadLibrary(filepath)
            print('DLL: ' + fileName + ', loaded from: ' + moduleDirectory)

        except:
            LOAD_EXCEPTION = 'DLL: ' + fileName + ', on path: ' + moduleDirectory +', failed to load.\nIs Kinect re-distributable installed?'
            return LOAD_EXCEPTION

        # the only way to be sure is to open the sensor & check the result
        Kinect2Sensor.DLL[OPEN_SENSOR].argtypes = (c_char, c_char, c_char)
        hresult = Kinect2Sensor.DLL[OPEN_SENSOR](c_char('\1'.encode()), c_char('F'.encode()), c_char('W'.encode()))
        testWorked = Kinect2Sensor.SUCCEEDED(hresult)

        #when successful, have the side effect of sensor being open. Reverse that
        if testWorked:
            Kinect2Sensor.DLL[CLOSE_SENSOR]()
            return None
        else:
            LOAD_EXCEPTION = 'Kinect open sensor failed.  Is it plugged in & connected?'
            return LOAD_EXCEPTION

    @staticmethod
    def capture():
        problemMsg = Kinect2Sensor.loadLibrary()
        if problemMsg is not None:
            return problemMsg

        # prep args & define to call
        tPoseStart = c_char('\1'.encode()) # always say true
        ForM  = c_char('F'.encode()) # forward, not mirror
        worldSpace  = c_char('W'.encode()) # world space, not camera
        Kinect2Sensor.DLL[OPEN_SENSOR].argtypes = (c_char, c_char, c_char)

        hresult = Kinect2Sensor.DLL[OPEN_SENSOR](tPoseStart, ForM, worldSpace)
        if not Kinect2Sensor.SUCCEEDED(hresult):
            return 'Sensor did not open.  Is it still plugged in / connected?'

        # call to start tracking
        callback_type = CFUNCTYPE(c_void_p, c_char_p)
        Kinect2Sensor.callback_func = callback_type(Kinect2Sensor.bodyReaderCallback)

        Kinect2Sensor.DLL[BEGIN_BODY_TRACKING].argtypes = [c_void_p, c_char_p]
        hresult = Kinect2Sensor.DLL[BEGIN_BODY_TRACKING](Kinect2Sensor.callback_func)
        if not Kinect2Sensor.SUCCEEDED(hresult):
             return 'Error beginning capture.'

        return None

    @staticmethod
    def bodyReaderCallback(data):
        Sensor.process(data)

    @staticmethod
    def close():
        # closeSensor automatically closes body reader in DLL
        millisFromFloor = Kinect2Sensor.DLL[CLOSE_SENSOR]()
        return millisFromFloor

    # windows dll call return evaluater
    @staticmethod
    def SUCCEEDED(hresult):
        return hresult == 0