# coding=utf-8
# https://ccrma.stanford.edu/courses/422/projects/WaveFormat/  (watch out - only int format)
# http://www-mmsp.ece.mcgill.ca/Documents/AudioFormats/WAVE/WAVE.html
import struct


def raw_pcm_to_wave(pcm_data, channels=2, rate=44100, bits=32, is_float=True):
    wFormatTag = 3 if is_float else 1
    BitsPerSample = bits
    NumChannels = channels
    SampleRate = rate

    BlockAlign = int(NumChannels * BitsPerSample / 8)
    ByteRate = SampleRate * BlockAlign

    Subchunk1Size = 16  # size: 16 or 18 or 40(16+2+22)
    Subchunk2Size = len(pcm_data)
    ChunkSize = 4 + (8 + Subchunk1Size) + (8 + Subchunk2Size)

    wave = b'RIFF'
    wave += struct.pack('i', ChunkSize)  # total size
    wave += b'WAVE'

    wave += b'fmt '
    wave += struct.pack('i', Subchunk1Size)
    wave += struct.pack('h', wFormatTag)  # 1=pcm, 3=IEEE float, ...
    wave += struct.pack('h', NumChannels)
    wave += struct.pack('i', SampleRate)
    wave += struct.pack('i', ByteRate)
    wave += struct.pack('h', BlockAlign)
    wave += struct.pack('h', BitsPerSample)
    # extra info:
    # data += struct.pack('h', 22)  # cbSize - Size of the extension (0 or 22)
    # ...

    wave += b'data'
    wave += struct.pack('i', Subchunk2Size)
    wave += pcm_data
    return wave


def chunks(l, n):
    for i in range(0, len(l), n):
        yield l[i:i + n]


def stereo_to_mono(pcm_stereo_data, sample_size=4):
    pcm_mono = b''
    for i, c in enumerate(chunks(pcm_stereo_data, sample_size)):
        if i % 2:
            continue
        pcm_mono += c
    return pcm_mono


def float32_to_unsigned8(pcm_data_f32):
    pcm_u8 = b''
    for c in chunks(pcm_data_f32, 4):
        f32 = struct.unpack('f', c)[0]
        u8 = int(f32 * 127 + 128)
        if u8 > 255:
            u8 = 255
        if u8 < 0:
            u8 = 0
        pcm_u8 += struct.pack('B', u8)
    return pcm_u8


def float32_to_signed16(pcm_data_f32):
    pcm_s16 = b''
    for c in chunks(pcm_data_f32, 4):
        f32 = struct.unpack('f', c)[0]
        s16 = int(f32 * 32768)
        if s16 > 32767:
            s16 = 32767
        if s16 < -32768:
            s16 = -32768
        pcm_s16 += struct.pack('h', s16)
    return pcm_s16
