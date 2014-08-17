# coding=utf-8
import ctypes
import ctypes.util
import struct


CoreAudio = ctypes.cdll.LoadLibrary(ctypes.util.find_library('CoreAudio'))


bytes2int = lambda s: struct.unpack('i', s[::-1])[0]

OSStatus = ctypes.c_int32


kAudioObjectSystemObject = 1
kAudioHardwarePropertyDefaultInputDevice = bytes2int(b'dIn ')
kAudioHardwarePropertyDefaultOutputDevice = bytes2int(b'dOut')
kAudioDevicePropertyStreamFormat = bytes2int(b'sfmt')
kAudioObjectPropertyScopeGlobal = bytes2int(b'glob')
kAudioObjectPropertyScopeInput = bytes2int(b'inpt')
kAudioObjectPropertyScopeOutput = bytes2int(b'outp')
kAudioObjectPropertyScopePlayThrough = bytes2int(b'ptru')
kAudioObjectPropertyElementMaster = 0
kAudioFormatLinearPCM = bytes2int(b'lpcm')


AudioObjectPropertySelector = ctypes.c_uint32
AudioObjectPropertyScope = ctypes.c_uint32
AudioObjectPropertyElement = ctypes.c_uint32
AudioObjectID = ctypes.c_uint32
AudioDeviceID = AudioObjectID


class AudioObjectPropertyAddress(ctypes.Structure):
    _fields_ = [
        ('mSelector', AudioObjectPropertySelector),
        ('mScope', AudioObjectPropertyScope),
        ('mElement', AudioObjectPropertyElement),
    ]


class AudioStreamBasicDescription(ctypes.Structure):
    _fields_ = [
        ('mSampleRate', ctypes.c_double),
        ('mFormatID', ctypes.c_uint32),
        ('mFormatFlags', ctypes.c_uint32),
        ('mBytesPerPacket', ctypes.c_uint32),
        ('mFramesPerPacket', ctypes.c_uint32),
        ('mBytesPerFrame', ctypes.c_uint32),
        ('mChannelsPerFrame', ctypes.c_uint32),
        ('mBitsPerChannel', ctypes.c_uint32),
        ('mReserved', ctypes.c_uint32),
    ]


class AudioBuffer(ctypes.Structure):
    _fields_ = [
        ('mNumberChannels', ctypes.c_uint32),
        ('mDataByteSize', ctypes.c_uint32),
        ('mData', ctypes.c_void_p),
    ]


class AudioBufferList(ctypes.Structure):
    _fields_ = [
        ('mNumberBuffers', ctypes.c_uint32),
        ('mBuffers', AudioBuffer * 1),
    ]

# typedef OSStatus
# (*AudioDeviceIOProc)(   AudioObjectID           inDevice,
#                         const AudioTimeStamp*   inNow,
#                         const AudioBufferList*  inInputData,
#                         const AudioTimeStamp*   inInputTime,
#                         AudioBufferList*        outOutputData,
#                         const AudioTimeStamp*   inOutputTime,
#                         void*                   inClientData);
AudioDeviceIOProc = ctypes.CFUNCTYPE(
    OSStatus,  # result type
    AudioObjectID,  # AudioObjectID           inDevice,
    ctypes.c_void_p,  # const AudioTimeStamp*   inNow,
    ctypes.POINTER(AudioBufferList),  # const AudioBufferList*  inInputData,
    ctypes.c_void_p,  # const AudioTimeStamp*   inInputTime,
    ctypes.c_void_p,  # AudioBufferList*        outOutputData,
    ctypes.c_void_p,  # const AudioTimeStamp*   inOutputTime,
    ctypes.c_void_p,  # void*                   inClientData
)
AudioDeviceIOProcID = AudioDeviceIOProc


def define(name, restype, argtypes):
    f = getattr(CoreAudio, name)
    f.restype = restype
    f.argtypes = argtypes
    return f


# extern OSStatus
# AudioObjectGetPropertyData( AudioObjectID                       inObjectID,
#                             const AudioObjectPropertyAddress*   inAddress,
#                             UInt32                              inQualifierDataSize,
#                             const void*                         inQualifierData,
#                             UInt32*                             ioDataSize,
#                             void*                               outData)
AudioObjectGetPropertyData = define('AudioObjectGetPropertyData', restype=OSStatus, argtypes=(
    AudioObjectID,  # inObjectID
    ctypes.POINTER(AudioObjectPropertyAddress),  # inAddress
    ctypes.c_uint32,  # inQualifierDataSize
    ctypes.c_void_p,  # inQualifierData
    ctypes.POINTER(ctypes.c_uint32),  # inDataSize
    ctypes.c_void_p,  # outData
))


# extern OSStatus
# AudioObjectSetPropertyData( AudioObjectID                       inObjectID,
#                             const AudioObjectPropertyAddress*   inAddress,
#                             UInt32                              inQualifierDataSize,
#                             const void*                         inQualifierData,
#                             UInt32                              inDataSize,
#                             const void*                         inData)
AudioObjectSetPropertyData = define('AudioObjectSetPropertyData', restype=OSStatus, argtypes=(
    AudioObjectID,  # inObjectID
    ctypes.POINTER(AudioObjectPropertyAddress),  # inAddress
    ctypes.c_uint32,  # inQualifierDataSize
    ctypes.c_void_p,  # inQualifierData
    ctypes.c_uint32,  # inDataSize
    ctypes.c_void_p,  # outData
))



# extern OSStatus
# AudioDeviceCreateIOProcID(  AudioObjectID           inDevice,
#                             AudioDeviceIOProc       inProc,
#                             void*                   inClientData,
#                             AudioDeviceIOProcID*    outIOProcID)
AudioDeviceCreateIOProcID = define('AudioDeviceCreateIOProcID', restype=OSStatus, argtypes=(
    AudioObjectID,
    AudioDeviceIOProc,
    ctypes.c_void_p,
    ctypes.POINTER(AudioDeviceIOProcID),
))


# extern OSStatus
# AudioDeviceStart(   AudioObjectID       inDevice,
#                     AudioDeviceIOProcID inProcID)
AudioDeviceStart = define('AudioDeviceStart',
                          restype=OSStatus, argtypes=(AudioObjectID, AudioDeviceIOProcID))


AudioDeviceStop = define('AudioDeviceStop',
                         restype=OSStatus, argtypes=(AudioObjectID, AudioDeviceIOProcID))


AudioDeviceDestroyIOProcID = define('AudioDeviceDestroyIOProcID',
                                    restype=OSStatus, argtypes=(AudioObjectID, AudioDeviceIOProcID))
