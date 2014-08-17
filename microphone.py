# coding=utf-8
import ctypes
import ctypes.util
import sys
import time

from coreaudio import (
    AudioObjectPropertyAddress,
    kAudioObjectPropertyScopeGlobal,
    kAudioObjectPropertyScopeInput,
    kAudioObjectPropertyElementMaster,
    kAudioObjectSystemObject,
    kAudioDevicePropertyStreamFormat,
    kAudioFormatLinearPCM,
    kAudioHardwarePropertyDefaultInputDevice,
    AudioDeviceID,
    AudioDeviceIOProc,
    AudioDeviceIOProcID,
    AudioDeviceCreateIOProcID,
    AudioDeviceDestroyIOProcID,
    AudioDeviceStart,
    AudioDeviceStop,
    AudioObjectGetPropertyData,
    AudioObjectSetPropertyData,
    AudioStreamBasicDescription,
)

GLOBAL_BUFFER = ''


def err(s):
    sys.stderr.write(str(s))


@AudioDeviceIOProc
def proc_audio_input(inDevice, inNow, inInputData, inInputTime, outOutputData, inOutputTime, inClientData):
    buf = inInputData[0].mBuffers[0]
    s = ctypes.cast(buf.mData, ctypes.POINTER(ctypes.c_char))
    # i = ctypes.cast(inClientData, ctypes.POINTER(InputData))
    # err(i.size)
    global GLOBAL_BUFFER
    GLOBAL_BUFFER += s[:buf.mDataByteSize]
    # sys.stdout.write(str(s[:buf.mDataByteSize]))
    return 0


def get_default_input_device_id():
    device_id = AudioDeviceID()
    size = ctypes.c_uint32(ctypes.sizeof(AudioDeviceID))
    addr = AudioObjectPropertyAddress(kAudioHardwarePropertyDefaultInputDevice,
                                      kAudioObjectPropertyScopeGlobal, kAudioObjectPropertyElementMaster)
    x = AudioObjectGetPropertyData(kAudioObjectSystemObject, ctypes.byref(addr), 0, None,
                                          ctypes.byref(size), ctypes.byref(device_id))
    import struct
    assert not x, Exception(struct.pack('i', x))
    return device_id


def get_default_input_device_format(input_device_id):
    fmt = AudioStreamBasicDescription()
    size = ctypes.c_uint32(ctypes.sizeof(AudioStreamBasicDescription))
    addr = AudioObjectPropertyAddress(kAudioDevicePropertyStreamFormat, kAudioObjectPropertyScopeInput,
                                      kAudioObjectPropertyElementMaster)
    assert not AudioObjectGetPropertyData(input_device_id, ctypes.byref(addr), 0, None, ctypes.byref(size),
                                          ctypes.byref(fmt))
    return fmt


def setup_default_input_device(device_id, rate=44100, channels=2, bits=32):
    size = ctypes.c_uint32(ctypes.sizeof(AudioStreamBasicDescription))
    addr = AudioObjectPropertyAddress(kAudioDevicePropertyStreamFormat, kAudioObjectPropertyScopeInput,
                                      kAudioObjectPropertyElementMaster)
    fmt = get_default_input_device_format(device_id)
    fmt.mFormatID = kAudioFormatLinearPCM
    fmt.mSampleRate = rate
    fmt.mChannelsPerFrame = channels
    fmt.mBitsPerChannel = bits
    # TODO: fmt.mFormatFlags - float
    # kAudioFormatFlagIsNonInterleaved
    # kLinearPCMFormatFlagIsFloat
    # kLinearPCMFormatFlagIsSignedInteger
    # kLinearPCMFormatFlagIsBigEndian
    # kLinearPCMFormatFlagIsPacked
    fmt.mFramesPerPacket = 1
    fmt.mBytesPerFrame = fmt.mBytesPerPacket = channels * int(bits / 8)

    assert not AudioObjectSetPropertyData(device_id, ctypes.byref(addr), 0, None, size, ctypes.byref(fmt))
    return fmt


class InputData(ctypes.Structure):
    _fields_ = [
        ('size', ctypes.c_uint32),
        ('data', ctypes.c_char_p),
    ]


def record(seconds, rate=44100, channels=2, bits=32):
    device_id = get_default_input_device_id()
    setup_default_input_device(device_id, rate=rate, channels=channels, bits=bits)
    proc_id = AudioDeviceIOProcID()

    out = ctypes.create_string_buffer(ctypes.sizeof(ctypes.c_float) * 4096 * 4096)
    inData = InputData(0, None)
    inData.data = ctypes.cast(out, ctypes.c_char_p)

    global GLOBAL_BUFFER
    GLOBAL_BUFFER = ''  # TODO: do it via inData somehow

    assert not AudioDeviceCreateIOProcID(device_id, proc_audio_input, ctypes.byref(inData), ctypes.byref(proc_id))
    assert not AudioDeviceStart(device_id, proc_id)
    try:
        time.sleep(seconds)
    except (KeyboardInterrupt, SystemExit):
        pass
    finally:
        assert not AudioDeviceStop(device_id, proc_id)
        assert not AudioDeviceDestroyIOProcID(device_id, proc_id)
    return GLOBAL_BUFFER
