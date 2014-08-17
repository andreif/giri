# coding=utf-8
import urllib2
import subprocess
import . import microphone
import . import wave


def wav_to_flac(wav_data):
    process = subprocess.Popen('/usr/local/bin/flac --stdout --totally-silent --best -',
                               stdin=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)
    flac_data, stderr = process.communicate(wav_data)
    return flac_data


def ask_google(data, rate, lang='en-US', api_key='AIzaSyBOti4mM-6x9WDnZIjIeyEU21OpBXqWBgw'):
    url = 'http://www.google.com/speech-api/v2/recognize?client=chromium&lang=%s&key=%s' % (lang, api_key)
    request = urllib2.Request(url, data=data, headers={'Content-Type': 'audio/x-flac; rate=%s' % rate})
    try:
        response = urllib2.urlopen(request)
    except:
        raise KeyError(u"Server wouldn't respond (invalid key or quota has been maxed out)")
    return response.read().decode("utf-8")


def recognize(lang='en-US', seconds=3, rate=32000, channels=1, bits=16):
    pcm_data = microphone.record(seconds=seconds, rate=rate, channels=2, bits=32)
    # with open('../out', 'rb') as f:
    #     pcm_data = f.read()
    # print len(pcm_data)

    if channels == 1:
        pcm_data = wave.stereo_to_mono(pcm_data)
        # print len(pcm_data)

    if bits == 8:
        is_float = False
        pcm_data = wave.float32_to_unsigned8(pcm_data)
        # print len(pcm_data)

    elif bits == 16:
        is_float = False
        pcm_data = wave.float32_to_signed16(pcm_data)
        # print len(pcm_data)

    else:
        is_float = True

    wav_data = wave.raw_pcm_to_wave(pcm_data, rate=rate, channels=channels, bits=bits, is_float=is_float)
    # print len(wav_data)

    with open(__file__ + '.wav', 'wb') as f:
        f.write(wav_data)

    flac_data = wav_to_flac(wav_data)
    # print len(flac_data)

    with open(__file__ + '.flac', 'wb') as f:
        f.write(flac_data)

    return ask_google(flac_data, rate=rate, lang=lang)
